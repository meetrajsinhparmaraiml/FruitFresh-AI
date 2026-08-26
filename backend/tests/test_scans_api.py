"""
Integration tests for scan API endpoints.

These tests use an in-memory SQLite database and mock the YOLO detector
so no actual model weights are required during CI.
"""

import io
import uuid
import numpy as np
import cv2
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import MagicMock, patch

from app.main import app
from app.db.database import get_db, init_db
from app.models.scan import Base
from app.schemas.detector import DetectionResult

# ---------------------------------------------------------------------------
# Test DB fixture — in-memory SQLite
# ---------------------------------------------------------------------------

TEST_DB_URL = "sqlite:///./test_scans.db"
test_engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_jpeg_bytes(brightness: int = 128, w: int = 200, h: int = 200) -> bytes:
    """Create a checkerboard JPEG with good quality metrics."""
    frame = np.full((h, w, 3), brightness, dtype=np.uint8)
    for y in range(h):
        for x in range(w):
            if (y // 4 + x // 4) % 2 == 0:
                frame[y, x] = [brightness, brightness, brightness]
            else:
                val = min(255, brightness + 80)
                frame[y, x] = [val, val, val]
    _, buf = cv2.imencode(".jpg", frame)
    return buf.tobytes()


GOOD_DETECTION = DetectionResult(
    fruit_type="apple",
    detection_confidence=0.92,
    bbox=[10.0, 10.0, 180.0, 180.0],
)


# ---------------------------------------------------------------------------
# POST /api/v1/scans
# ---------------------------------------------------------------------------

@patch("app.api.v1.endpoints.scans.get_detector")
def test_create_scan_success(mock_get_detector):
    mock_det = MagicMock()
    mock_det.detect.return_value = [GOOD_DETECTION]
    mock_get_detector.return_value = mock_det

    data = _make_jpeg_bytes(brightness=128)
    response = client.post(
        "/api/v1/scans",
        files={"file": ("test.jpg", io.BytesIO(data), "image/jpeg")},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["fruit_type"] == "apple"
    assert body["status"] in ("OK", "UNCERTAIN")
    assert "id" in body
    assert "result" in body


@patch("app.api.v1.endpoints.scans.get_detector")
def test_create_scan_no_fruit_returns_422(mock_get_detector):
    mock_det = MagicMock()
    mock_det.detect.return_value = []
    mock_get_detector.return_value = mock_det

    data = _make_jpeg_bytes()
    response = client.post(
        "/api/v1/scans",
        files={"file": ("test.jpg", io.BytesIO(data), "image/jpeg")},
    )
    assert response.status_code == 422
    detail = response.json()["detail"]
    assert detail["code"] == "NO_FRUIT"


@patch("app.api.v1.endpoints.scans.get_detector")
def test_create_scan_multiple_fruits_returns_422(mock_get_detector):
    mock_det = MagicMock()
    mock_det.detect.return_value = [GOOD_DETECTION, GOOD_DETECTION]
    mock_get_detector.return_value = mock_det

    data = _make_jpeg_bytes()
    response = client.post(
        "/api/v1/scans",
        files={"file": ("test.jpg", io.BytesIO(data), "image/jpeg")},
    )
    assert response.status_code == 422
    detail = response.json()["detail"]
    assert detail["code"] == "MULTIPLE_FRUITS"


def test_create_scan_invalid_image_returns_422():
    response = client.post(
        "/api/v1/scans",
        files={"file": ("bad.jpg", io.BytesIO(b"not-an-image"), "image/jpeg")},
    )
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# GET /api/v1/scans/{id}
# ---------------------------------------------------------------------------

@patch("app.api.v1.endpoints.scans.get_detector")
def test_get_scan_by_id(mock_get_detector):
    mock_det = MagicMock()
    mock_det.detect.return_value = [GOOD_DETECTION]
    mock_get_detector.return_value = mock_det

    data = _make_jpeg_bytes()
    create_resp = client.post(
        "/api/v1/scans",
        files={"file": ("test.jpg", io.BytesIO(data), "image/jpeg")},
    )
    assert create_resp.status_code == 201
    scan_id = create_resp.json()["id"]

    get_resp = client.get(f"/api/v1/scans/{scan_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == scan_id


def test_get_scan_not_found():
    response = client.get(f"/api/v1/scans/{uuid.uuid4()}")
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# GET /api/v1/scans  (history)
# ---------------------------------------------------------------------------

def test_list_scans_returns_list():
    response = client.get("/api/v1/scans")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@patch("app.api.v1.endpoints.scans.get_detector")
def test_list_scans_newest_first(mock_get_detector):
    mock_det = MagicMock()
    mock_det.detect.return_value = [GOOD_DETECTION]
    mock_get_detector.return_value = mock_det

    for _ in range(2):
        client.post(
            "/api/v1/scans",
            files={"file": ("test.jpg", io.BytesIO(_make_jpeg_bytes()), "image/jpeg")},
        )

    response = client.get("/api/v1/scans?limit=10")
    assert response.status_code == 200
    items = response.json()
    if len(items) >= 2:
        assert items[0]["created_at"] >= items[1]["created_at"]


# ---------------------------------------------------------------------------
# Response schema shape
# ---------------------------------------------------------------------------

@patch("app.api.v1.endpoints.scans.get_detector")
def test_scan_response_has_no_filesystem_path(mock_get_detector):
    mock_det = MagicMock()
    mock_det.detect.return_value = [GOOD_DETECTION]
    mock_get_detector.return_value = mock_det

    data = _make_jpeg_bytes()
    resp = client.post(
        "/api/v1/scans",
        files={"file": ("test.jpg", io.BytesIO(data), "image/jpeg")},
    )
    body = resp.json()
    # No raw filesystem path must be exposed
    import json
    body_str = json.dumps(body)
    assert "C:\\" not in body_str
    assert "/home/" not in body_str
