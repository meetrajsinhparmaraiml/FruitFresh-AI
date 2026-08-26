import uuid
import io
import base64
from typing import Optional
import numpy as np
import cv2
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db.database import get_db
from app.models.scan import Scan, ScanResult, DetectedIssueRecord, ScanStatus
from app.inference.detector import FruitDetector
from app.cv.quality import evaluate_quality
from app.inference.freshness import analyse as analyse_freshness
from app.rules.scoring import compute_score

router = APIRouter(prefix="/api/v1/scans", tags=["scans"])

# Lazy-load detector (singleton per process)
_detector: Optional[FruitDetector] = None


def get_detector() -> FruitDetector:
    global _detector
    if _detector is None:
        _detector = FruitDetector()
    return _detector


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------

class IssueOut(BaseModel):
    issue_type: str
    severity: str
    confidence: float
    model_config = {"from_attributes": True}


class ScanResultOut(BaseModel):
    score: Optional[int]
    label: Optional[str]
    analysis: str
    model_version: str
    rules_version: str
    model_config = {"from_attributes": True}


class ScanOut(BaseModel):
    id: str
    fruit_type: str
    status: str
    detection_confidence: Optional[float]
    created_at: str
    result: Optional[ScanResultOut]
    issues: list[IssueOut]
    model_config = {"from_attributes": True}


class ScanListItem(BaseModel):
    id: str
    fruit_type: str
    status: str
    score: Optional[int]
    label: Optional[str]
    created_at: str
    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _decode_image(data: bytes) -> np.ndarray:
    arr = np.frombuffer(data, np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Cannot decode image")
    return img


def _scan_to_out(scan: Scan) -> ScanOut:
    return ScanOut(
        id=scan.id,
        fruit_type=scan.fruit_type,
        status=scan.status.value if hasattr(scan.status, "value") else scan.status,
        detection_confidence=scan.detection_confidence,
        created_at=scan.created_at.isoformat(),
        result=ScanResultOut(
            score=scan.result.score if scan.result else None,
            label=scan.result.label if scan.result else None,
            analysis=scan.result.analysis if scan.result else "",
            model_version=scan.result.model_version if scan.result else "",
            rules_version=scan.result.rules_version if scan.result else "",
        ) if scan.result else None,
        issues=[
            IssueOut(
                issue_type=i.issue_type,
                severity=i.severity.value if hasattr(i.severity, "value") else i.severity,
                confidence=i.confidence,
            )
            for i in (scan.issues or [])
        ],
    )


# ---------------------------------------------------------------------------
# POST /api/v1/scans
# ---------------------------------------------------------------------------

@router.post("", response_model=ScanOut, status_code=201)
def create_scan(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Accept a captured frame image.
    Run detection -> quality gate -> freshness analysis -> scoring.
    Persist and return structured scan result.
    """
    raw = file.file.read()
    try:
        frame = _decode_image(raw)
    except ValueError:
        raise HTTPException(status_code=422, detail="Cannot decode uploaded image.")

    detector = get_detector()
    detections = detector.detect(frame)

    if not detections:
        raise HTTPException(status_code=422, detail={"code": "NO_FRUIT", "message": "No supported fruit detected."})

    if len(detections) > 1:
        raise HTTPException(status_code=422, detail={"code": "MULTIPLE_FRUITS", "message": "Multiple fruits detected."})

    det = detections[0]
    frame_h, frame_w = frame.shape[:2]

    quality = evaluate_quality(frame, det.bbox)
    if not quality.passed:
        raise HTTPException(status_code=422, detail={"code": quality.reason_code, "message": quality.reason_code})

    # Crop ROI for freshness analysis
    x1, y1, x2, y2 = [max(0, int(v)) for v in det.bbox]
    x2, y2 = min(x2, frame_w), min(y2, frame_h)
    crop = frame[y1:y2, x1:x2]

    freshness = analyse_freshness(crop, det.fruit_type)  # type: ignore
    scoring = compute_score(freshness)

    status = ScanStatus.UNCERTAIN if scoring.status == "UNCERTAIN" else ScanStatus.OK

    # Persist scan
    scan = Scan(
        id=str(uuid.uuid4()),
        fruit_type=det.fruit_type,
        status=status,
        image_uri=None,  # File system path not exposed per security rule
        bbox_x1=det.bbox[0],
        bbox_y1=det.bbox[1],
        bbox_x2=det.bbox[2],
        bbox_y2=det.bbox[3],
        detection_confidence=det.detection_confidence,
    )
    db.add(scan)
    db.flush()

    scan_result = ScanResult(
        scan_id=scan.id,
        score=scoring.score,
        label=scoring.label,
        analysis=scoring.analysis,
    )
    db.add(scan_result)

    for issue in freshness.issues:
        db.add(DetectedIssueRecord(
            scan_id=scan.id,
            issue_type=issue.issue_type.value,
            severity=issue.severity.value,  # type: ignore
            confidence=issue.confidence,
        ))

    db.commit()
    db.refresh(scan)
    return _scan_to_out(scan)


# ---------------------------------------------------------------------------
# GET /api/v1/scans/{id}
# ---------------------------------------------------------------------------

@router.get("/{scan_id}", response_model=ScanOut)
def get_scan(scan_id: str, db: Session = Depends(get_db)):
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found.")
    return _scan_to_out(scan)


# ---------------------------------------------------------------------------
# GET /api/v1/scans  (paginated history)
# ---------------------------------------------------------------------------

@router.get("", response_model=list[ScanListItem])
def list_scans(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    scans = (
        db.query(Scan)
        .order_by(Scan.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [
        ScanListItem(
            id=s.id,
            fruit_type=s.fruit_type,
            status=s.status.value if hasattr(s.status, "value") else s.status,
            score=s.result.score if s.result else None,
            label=s.result.label if s.result else None,
            created_at=s.created_at.isoformat(),
        )
        for s in scans
    ]
