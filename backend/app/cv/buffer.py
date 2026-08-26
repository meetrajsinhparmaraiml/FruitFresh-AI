from collections import deque
from dataclasses import dataclass, field
from typing import Optional
import numpy as np
from app.core.config import settings
from app.cv.quality import QualityGateResult


@dataclass
class CandidateFrame:
    """A frame that has passed detection and quality gates."""
    image: np.ndarray
    bbox: list[float]
    fruit_type: str
    detection_confidence: float
    quality: QualityGateResult
    composite_score: float = field(default=0.0, init=False)


def score_frame(candidate: CandidateFrame, frame_h: int, frame_w: int) -> float:
    """
    Compute a composite quality score in [0, 1] using configurable weights.

    Metrics
    -------
    sharpness  : normalised Laplacian variance (clamped at 500 for scaling)
    area       : fruit bbox area ratio relative to frame
    brightness : proximity to mid-grey (128) normalised to [0, 1]
    position   : how centred the bounding box is in the frame
    """
    cfg = settings

    # Sharpness: normalise blur_variance to [0, 1] (cap at 500)
    sharpness = min(1.0, (candidate.quality.blur_variance or 0.0) / 500.0)

    # Area: normalise fruit_area_ratio (cap at 0.5 → full score at half frame)
    area = min(1.0, (candidate.quality.fruit_area_ratio or 0.0) / 0.5)

    # Brightness: score peaks at mid-grey (128), falls off at extremes
    mean_b = candidate.quality.mean_brightness or 128.0
    brightness = 1.0 - abs(mean_b - 128.0) / 128.0

    # Position: measure how close the bbox centre is to the frame centre
    x1, y1, x2, y2 = candidate.bbox
    cx = (x1 + x2) / 2.0
    cy = (y1 + y2) / 2.0
    dx = abs(cx - frame_w / 2.0) / (frame_w / 2.0)
    dy = abs(cy - frame_h / 2.0) / (frame_h / 2.0)
    position = 1.0 - min(1.0, (dx + dy) / 2.0)

    score = (
        sharpness  * cfg.CAPTURE_WEIGHT_SHARPNESS +
        area       * cfg.CAPTURE_WEIGHT_AREA +
        brightness * cfg.CAPTURE_WEIGHT_BRIGHTNESS +
        position   * cfg.CAPTURE_WEIGHT_POSITION
    )
    return round(score, 4)


class FrameBuffer:
    """Bounded FIFO buffer of scored candidate frames."""

    def __init__(self, frame_h: int = 480, frame_w: int = 640):
        self._buffer: deque[CandidateFrame] = deque(maxlen=settings.CAPTURE_BUFFER_SIZE)
        self.frame_h = frame_h
        self.frame_w = frame_w

    def add(self, candidate: CandidateFrame) -> None:
        candidate.composite_score = score_frame(candidate, self.frame_h, self.frame_w)
        self._buffer.append(candidate)

    def best(self) -> Optional[CandidateFrame]:
        if not self._buffer:
            return None
        return max(self._buffer, key=lambda c: c.composite_score)

    def clear(self) -> None:
        self._buffer.clear()

    def __len__(self) -> int:
        return len(self._buffer)
