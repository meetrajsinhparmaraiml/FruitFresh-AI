from typing import Optional
import numpy as np
import cv2
from pydantic import BaseModel
from app.core.config import settings


class QualityGateResult(BaseModel):
    passed: bool
    reason_code: Optional[str] = None
    blur_variance: Optional[float] = None
    mean_brightness: Optional[float] = None
    fruit_area_ratio: Optional[float] = None


QUALITY_GUIDANCE: dict[str, str] = {
    "IMAGE_TOO_BLURRY": "Hold steady / move closer",
    "IMAGE_TOO_DARK": "Use better diffuse lighting",
    "IMAGE_TOO_BRIGHT": "Reduce glare or direct light",
    "FRUIT_TOO_SMALL": "Move closer",
    "FRUIT_OCCLUDED": "Remove obstruction",
}


def evaluate_quality(
    frame: np.ndarray,
    bbox: list[float],
) -> QualityGateResult:
    """
    Evaluate image quality for a detected fruit region.

    Args:
        frame: Full BGR frame as numpy array (H, W, C).
        bbox:  Bounding box [x1, y1, x2, y2] in pixel coordinates.

    Returns:
        QualityGateResult with pass/fail status and reason code.
    """
    frame_h, frame_w = frame.shape[:2]
    x1, y1, x2, y2 = [max(0, int(v)) for v in bbox]
    x2 = min(x2, frame_w)
    y2 = min(y2, frame_h)

    # --- Size check ---------------------------------------------------------
    box_area = max(0, (x2 - x1)) * max(0, (y2 - y1))
    frame_area = frame_h * frame_w
    area_ratio = box_area / frame_area if frame_area > 0 else 0.0

    if area_ratio < settings.QUALITY_MIN_FRUIT_AREA_RATIO:
        return QualityGateResult(
            passed=False,
            reason_code="FRUIT_TOO_SMALL",
            fruit_area_ratio=area_ratio,
        )

    # --- Occlusion / edge-clip check ----------------------------------------
    clip_left   = max(0, -int(bbox[0])) / frame_w
    clip_top    = max(0, -int(bbox[1])) / frame_h
    clip_right  = max(0, int(bbox[2]) - frame_w) / frame_w
    clip_bottom = max(0, int(bbox[3]) - frame_h) / frame_h
    max_clip = max(clip_left, clip_top, clip_right, clip_bottom)

    if max_clip > settings.QUALITY_MAX_EDGE_CLIP_RATIO:
        return QualityGateResult(
            passed=False,
            reason_code="FRUIT_OCCLUDED",
            fruit_area_ratio=area_ratio,
        )

    # Crop fruit region for blur and brightness checks
    crop = frame[y1:y2, x1:x2]
    if crop.size == 0:
        return QualityGateResult(passed=False, reason_code="FRUIT_TOO_SMALL", fruit_area_ratio=0.0)

    gray_crop = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY) if len(crop.shape) == 3 else crop

    # --- Blur check (Laplacian variance) ------------------------------------
    blur_var = float(cv2.Laplacian(gray_crop, cv2.CV_64F).var())
    if blur_var < settings.QUALITY_MIN_BLUR_VARIANCE:
        return QualityGateResult(
            passed=False,
            reason_code="IMAGE_TOO_BLURRY",
            blur_variance=blur_var,
            fruit_area_ratio=area_ratio,
        )

    # --- Brightness check ---------------------------------------------------
    mean_brightness = float(gray_crop.mean())
    if mean_brightness < settings.QUALITY_MIN_BRIGHTNESS:
        return QualityGateResult(
            passed=False,
            reason_code="IMAGE_TOO_DARK",
            blur_variance=blur_var,
            mean_brightness=mean_brightness,
            fruit_area_ratio=area_ratio,
        )
    if mean_brightness > settings.QUALITY_MAX_BRIGHTNESS:
        return QualityGateResult(
            passed=False,
            reason_code="IMAGE_TOO_BRIGHT",
            blur_variance=blur_var,
            mean_brightness=mean_brightness,
            fruit_area_ratio=area_ratio,
        )

    return QualityGateResult(
        passed=True,
        blur_variance=blur_var,
        mean_brightness=mean_brightness,
        fruit_area_ratio=area_ratio,
    )
