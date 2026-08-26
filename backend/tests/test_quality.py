import numpy as np
import pytest
from app.cv.quality import evaluate_quality
from app.core.config import settings

# Frame dimensions used across all tests
FRAME_H, FRAME_W = 480, 640
# A bbox that fills ~25 % of the frame — well above the minimum ratio
GOOD_BBOX = [100.0, 100.0, 380.0, 340.0]


def _make_frame(brightness: int = 128) -> np.ndarray:
    """Return a uniformly lit BGR frame."""
    return np.full((FRAME_H, FRAME_W, 3), brightness, dtype=np.uint8)


def _make_sharp_frame(brightness: int = 128) -> np.ndarray:
    """Return a frame with a high-frequency checkerboard pattern so the
    Laplacian variance is well above the blur threshold."""
    frame = _make_frame(brightness)
    # Paint a 4-px checkerboard inside the bounding box region
    for y in range(80, FRAME_H - 80):
        for x in range(80, FRAME_W - 80):
            if (y // 4 + x // 4) % 2 == 0:
                frame[y, x] = [brightness, brightness, brightness]
            else:
                val = min(255, brightness + 80)
                frame[y, x] = [val, val, val]
    return frame


# ---------------------------------------------------------------------------
# Passing case
# ---------------------------------------------------------------------------

def test_quality_passes_for_good_frame():
    frame = _make_sharp_frame(brightness=128)
    result = evaluate_quality(frame, GOOD_BBOX)
    assert result.passed is True
    assert result.reason_code is None


# ---------------------------------------------------------------------------
# Blur
# ---------------------------------------------------------------------------

def test_detects_too_blurry():
    # A flat uniform frame has zero Laplacian variance → blurry
    settings.QUALITY_MIN_BLUR_VARIANCE = 50.0
    frame = _make_frame(brightness=128)
    result = evaluate_quality(frame, GOOD_BBOX)
    assert result.passed is False
    assert result.reason_code == "IMAGE_TOO_BLURRY"


# ---------------------------------------------------------------------------
# Brightness
# ---------------------------------------------------------------------------

def test_detects_too_dark():
    settings.QUALITY_MIN_BLUR_VARIANCE = 0.0   # disable blur gate for this test
    settings.QUALITY_MIN_BRIGHTNESS = 50.0
    frame = _make_frame(brightness=20)          # very dark
    result = evaluate_quality(frame, GOOD_BBOX)
    assert result.passed is False
    assert result.reason_code == "IMAGE_TOO_DARK"


def test_detects_too_bright():
    settings.QUALITY_MIN_BLUR_VARIANCE = 0.0
    settings.QUALITY_MAX_BRIGHTNESS = 200.0
    frame = _make_frame(brightness=240)         # overexposed
    result = evaluate_quality(frame, GOOD_BBOX)
    assert result.passed is False
    assert result.reason_code == "IMAGE_TOO_BRIGHT"


# ---------------------------------------------------------------------------
# Size
# ---------------------------------------------------------------------------

def test_detects_fruit_too_small():
    settings.QUALITY_MIN_FRUIT_AREA_RATIO = 0.10
    frame = _make_sharp_frame()
    tiny_bbox = [100.0, 100.0, 110.0, 110.0]   # 10×10 px → ~0.03 % of frame
    result = evaluate_quality(frame, tiny_bbox)
    assert result.passed is False
    assert result.reason_code == "FRUIT_TOO_SMALL"


# ---------------------------------------------------------------------------
# Occlusion / edge clip
# ---------------------------------------------------------------------------

def test_detects_fruit_occluded_clipping_left():
    settings.QUALITY_MIN_FRUIT_AREA_RATIO = 0.0  # disable size gate
    settings.QUALITY_MIN_BLUR_VARIANCE = 0.0
    settings.QUALITY_MAX_EDGE_CLIP_RATIO = 0.02
    frame = _make_frame()
    # bbox extends 50 px outside the left edge of the frame
    clipped_bbox = [-50.0, 50.0, 300.0, 300.0]
    result = evaluate_quality(frame, clipped_bbox)
    assert result.passed is False
    assert result.reason_code == "FRUIT_OCCLUDED"
