from enum import Enum
from typing import Optional
from dataclasses import dataclass
import numpy as np
from app.core.config import settings
from app.schemas.detector import DetectionResult
from app.cv.quality import evaluate_quality
from app.cv.buffer import FrameBuffer, CandidateFrame
from app.cv.stability import StabilityTracker


class CaptureState(str, Enum):
    SEARCHING = "SEARCHING"
    DETECTED = "DETECTED"
    TRACKING = "TRACKING"
    STABLE = "STABLE"
    BEST_FRAME_SELECTED = "BEST_FRAME_SELECTED"
    CAPTURED = "CAPTURED"


@dataclass
class CaptureResult:
    image: np.ndarray
    bbox: list[float]
    fruit_type: str
    detection_confidence: float
    composite_score: float


class AutoCaptureController:
    """
    State machine that progresses through CaptureState stages.

    Feed frames via `process_frame()`.
    When state reaches CAPTURED, retrieve result via `get_capture()`.
    """

    def __init__(self, frame_h: int = 480, frame_w: int = 640):
        self.state = CaptureState.SEARCHING
        self.buffer = FrameBuffer(frame_h=frame_h, frame_w=frame_w)
        self.tracker = StabilityTracker()
        self._capture: Optional[CaptureResult] = None

    def process_frame(
        self,
        frame: np.ndarray,
        detections: list[DetectionResult],
    ) -> CaptureState:
        """
        Advance the state machine for one sampled frame.

        Returns the new CaptureState.
        """
        # --- SEARCHING: no single valid detection ---------------------------
        if len(detections) != 1:
            self.tracker.add_frame(detections)
            self._transition(CaptureState.SEARCHING)
            return self.state

        det = detections[0]
        self._transition(CaptureState.DETECTED)

        # --- Quality gate ---------------------------------------------------
        quality = evaluate_quality(frame, det.bbox)
        if not quality.passed:
            self.tracker.add_frame([det])
            return self.state

        # --- Buffer the candidate -------------------------------------------
        candidate = CandidateFrame(
            image=frame,
            bbox=det.bbox,
            fruit_type=det.fruit_type,
            detection_confidence=det.detection_confidence,
            quality=quality,
        )
        self.buffer.add(candidate)
        self.tracker.add_frame([det])
        self._transition(CaptureState.TRACKING)

        # --- Stability gate -------------------------------------------------
        if not self.tracker.is_stable():
            return self.state

        self._transition(CaptureState.STABLE)

        # --- Select best frame ----------------------------------------------
        best = self.buffer.best()
        if best is None or best.composite_score < settings.CAPTURE_MIN_SCORE_THRESHOLD:
            return self.state

        self._transition(CaptureState.BEST_FRAME_SELECTED)
        self._capture = CaptureResult(
            image=best.image,
            bbox=best.bbox,
            fruit_type=best.fruit_type,
            detection_confidence=best.detection_confidence,
            composite_score=best.composite_score,
        )
        self._transition(CaptureState.CAPTURED)
        return self.state

    def get_capture(self) -> Optional[CaptureResult]:
        return self._capture

    def reset(self) -> None:
        self.state = CaptureState.SEARCHING
        self.buffer.clear()
        self.tracker = StabilityTracker()
        self._capture = None

    def _transition(self, new_state: CaptureState) -> None:
        self.state = new_state
