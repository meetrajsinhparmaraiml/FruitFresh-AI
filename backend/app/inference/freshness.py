"""
Freshness Inference Engine — CV Baseline

This module provides rule-based visible-condition estimation.
It is explicitly labelled as a BASELINE using classical CV feature extraction.

DISCLAIMER:
  - Estimates visible EXTERNAL condition only.
  - Does NOT assess internal rot, pathogens, pesticide safety, nutrition,
    or guaranteed shelf life.
  - This is NOT a scientific food-safety tool.
"""

from typing import Literal
import numpy as np
import cv2
from pydantic import BaseModel

from app.cv.issues import DetectedIssue, detect_issues


FruitType = Literal["apple", "banana"]


class FreshnessResult(BaseModel):
    fruit_type: FruitType
    raw_score: float          # 0.0 – 1.0 internal confidence
    issues: list[DetectedIssue]
    analysis_method: str = "cv_baseline_v1"
    uncertainty: bool = False

    model_config = {"arbitrary_types_allowed": True}


_SEVERITY_PENALTY = {"low": 0.05, "medium": 0.15, "high": 0.30}


def _base_color_score_apple(crop_bgr: np.ndarray) -> float:
    """
    Score apple freshness from HSV colour distribution.
    Fresh apple: rich red/green saturation, high V.
    Returns score in [0, 1].
    """
    hsv = cv2.cvtColor(crop_bgr, cv2.COLOR_BGR2HSV).astype(np.float32)
    s = hsv[:, :, 1]
    v = hsv[:, :, 2]

    # Fraction of pixels with good saturation (>80) and brightness (>80)
    healthy_mask = (s > 80) & (v > 80)
    return float(healthy_mask.sum() / s.size)


def _base_color_score_banana(crop_bgr: np.ndarray) -> float:
    """
    Score banana freshness from HSV colour distribution.
    Fresh banana: yellow hue (20-35), high saturation, high V.
    Returns score in [0, 1].
    """
    hsv = cv2.cvtColor(crop_bgr, cv2.COLOR_BGR2HSV).astype(np.float32)
    h = hsv[:, :, 0]
    s = hsv[:, :, 1]
    v = hsv[:, :, 2]

    yellow_mask = (h >= 20) & (h <= 35) & (s > 80) & (v > 100)
    return float(yellow_mask.sum() / h.size)


def analyse(crop_bgr: np.ndarray, fruit_type: FruitType) -> FreshnessResult:
    """
    Run the CV baseline freshness analysis on a cropped fruit image.

    Args:
        crop_bgr:   Pre-cropped fruit ROI as a BGR numpy array.
        fruit_type: "apple" or "banana".

    Returns:
        FreshnessResult with raw_score, issues, and metadata.
    """
    if crop_bgr is None or crop_bgr.size == 0:
        return FreshnessResult(
            fruit_type=fruit_type,
            raw_score=0.0,
            issues=[],
            uncertainty=True,
        )

    # Base colour health score
    if fruit_type == "apple":
        base_score = _base_color_score_apple(crop_bgr)
    else:
        base_score = _base_color_score_banana(crop_bgr)

    # Detect visible issues
    issues = detect_issues(crop_bgr, fruit_type)

    # Penalise for each issue
    penalty = sum(_SEVERITY_PENALTY.get(issue.severity, 0.0) for issue in issues)
    raw_score = max(0.0, min(1.0, base_score - penalty))

    uncertain = base_score < 0.10  # Very little signal → flag uncertainty

    return FreshnessResult(
        fruit_type=fruit_type,
        raw_score=round(raw_score, 4),
        issues=issues,
        uncertainty=uncertain,
    )
