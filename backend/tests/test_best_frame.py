import numpy as np
import pytest
from app.cv.buffer import FrameBuffer, CandidateFrame, score_frame
from app.cv.capture import AutoCaptureController, CaptureState
from app.cv.quality import QualityGateResult
from app.schemas.detector import DetectionResult
from app.core.config import settings

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

FRAME_H, FRAME_W = 480, 640
GOOD_BBOX = [100.0, 100.0, 380.0, 340.0]


def _make_checkerboard(brightness: int = 128) -> np.ndarray:
    frame = np.full((FRAME_H, FRAME_W, 3), brightness, dtype=np.uint8)
    for y in range(80, FRAME_H - 80):
        for x in range(80, FRAME_W - 80):
            if (y // 4 + x // 4) % 2 == 0:
                frame[y, x] = [brightness, brightness, brightness]
            else:
                val = min(255, brightness + 80)
                frame[y, x] = [val, val, val]
    return frame


def _good_quality(blur: float = 300.0) -> QualityGateResult:
    return QualityGateResult(
        passed=True,
        blur_variance=blur,
        mean_brightness=128.0,
        fruit_area_ratio=0.25,
    )


def _candidate(blur: float = 300.0, bbox=None) -> CandidateFrame:
    bbox = bbox or GOOD_BBOX
    return CandidateFrame(
        image=np.zeros((FRAME_H, FRAME_W, 3), dtype=np.uint8),
        bbox=bbox,
        fruit_type="apple",
        detection_confidence=0.9,
        quality=_good_quality(blur=blur),
    )


def _detection(bbox=None) -> DetectionResult:
    bbox = bbox or GOOD_BBOX
    return DetectionResult(fruit_type="apple", detection_confidence=0.9, bbox=bbox)


# ---------------------------------------------------------------------------
# FrameBuffer tests
# ---------------------------------------------------------------------------

def test_buffer_selects_highest_score():
    buf = FrameBuffer(frame_h=FRAME_H, frame_w=FRAME_W)
    low = _candidate(blur=50.0)
    high = _candidate(blur=400.0)
    buf.add(low)
    buf.add(high)
    best = buf.best()
    assert best is not None
    assert best.quality.blur_variance == 400.0


def test_buffer_evicts_oldest_on_overflow():
    settings.CAPTURE_BUFFER_SIZE = 3
    buf = FrameBuffer(frame_h=FRAME_H, frame_w=FRAME_W)
    for i in range(4):
        buf.add(_candidate(blur=float(100 + i * 50)))
    # Buffer capped at 3; oldest (blur=100) should be gone
    assert len(buf) == 3


def test_buffer_empty_best_returns_none():
    buf = FrameBuffer()
    assert buf.best() is None


def test_score_better_for_sharper_frame():
    sharp = _candidate(blur=400.0)
    blurry = _candidate(blur=10.0)
    s_sharp = score_frame(sharp, FRAME_H, FRAME_W)
    s_blurry = score_frame(blurry, FRAME_H, FRAME_W)
    assert s_sharp > s_blurry


# ---------------------------------------------------------------------------
# AutoCaptureController state machine tests
# ---------------------------------------------------------------------------

def _configure_for_fast_capture():
    """Configure stability + score thresholds for fast deterministic tests."""
    settings.STABILITY_REQUIRED_FRAMES = 3
    settings.STABILITY_IOU_THRESHOLD = 0.0
    settings.STABILITY_MAX_DISPLACEMENT = 9999.0
    settings.CAPTURE_MIN_SCORE_THRESHOLD = 0.0
    settings.QUALITY_MIN_BLUR_VARIANCE = 0.0
    settings.QUALITY_MIN_BRIGHTNESS = 0.0
    settings.QUALITY_MAX_BRIGHTNESS = 255.0
    settings.QUALITY_MIN_FRUIT_AREA_RATIO = 0.0
    settings.QUALITY_MAX_EDGE_CLIP_RATIO = 1.0


def test_state_searching_when_no_detections():
    ctrl = AutoCaptureController(frame_h=FRAME_H, frame_w=FRAME_W)
    frame = _make_checkerboard()
    state = ctrl.process_frame(frame, [])
    assert state == CaptureState.SEARCHING


def test_state_reaches_captured_after_stable_sequence():
    _configure_for_fast_capture()
    ctrl = AutoCaptureController(frame_h=FRAME_H, frame_w=FRAME_W)
    frame = _make_checkerboard()
    det = _detection()
    state = CaptureState.SEARCHING
    for _ in range(10):
        state = ctrl.process_frame(frame, [det])
        if state == CaptureState.CAPTURED:
            break
    assert state == CaptureState.CAPTURED
    assert ctrl.get_capture() is not None


def test_capture_result_has_expected_fruit_type():
    _configure_for_fast_capture()
    ctrl = AutoCaptureController(frame_h=FRAME_H, frame_w=FRAME_W)
    frame = _make_checkerboard()
    for _ in range(10):
        ctrl.process_frame(frame, [_detection()])
    result = ctrl.get_capture()
    assert result is not None
    assert result.fruit_type == "apple"


def test_reset_clears_state():
    _configure_for_fast_capture()
    ctrl = AutoCaptureController(frame_h=FRAME_H, frame_w=FRAME_W)
    frame = _make_checkerboard()
    for _ in range(10):
        ctrl.process_frame(frame, [_detection()])
    ctrl.reset()
    assert ctrl.state == CaptureState.SEARCHING
    assert ctrl.get_capture() is None
