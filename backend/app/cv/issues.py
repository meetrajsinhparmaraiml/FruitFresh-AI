from enum import Enum
from typing import Optional
from pydantic import BaseModel


class IssueSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class IssueType(str, Enum):
    BROWN_SPOT = "brown_spot"
    BRUISE_LIKE_AREA = "bruise_like_area"
    WRINKLING = "wrinkling"
    MOLD_LIKE_AREA = "mold_like_area"
    SURFACE_DAMAGE = "surface_damage"
    DISCOLORATION = "discoloration"
    OVERRIPENING_LIKE = "overripening_like"
    DRYING_SHRIVELING = "drying_shriveling"


class DetectedIssue(BaseModel):
    issue_type: IssueType
    severity: IssueSeverity
    confidence: float  # 0.0 – 1.0


def _severity_from_ratio(ratio: float) -> IssueSeverity:
    if ratio < 0.05:
        return IssueSeverity.LOW
    if ratio < 0.20:
        return IssueSeverity.MEDIUM
    return IssueSeverity.HIGH


def detect_issues_apple(crop_bgr) -> list[DetectedIssue]:
    """Rule-based issue detection for Apple.

    Checks:
    - Brown/dark spots  → brown_spot / bruise_like_area
    - Excessive dull/grey pixels → surface_damage
    - Overall hue deviation from expected apple red/green → discoloration
    - Low saturation regions → wrinkling proxy
    """
    import numpy as np
    import cv2

    issues: list[DetectedIssue] = []
    hsv = cv2.cvtColor(crop_bgr, cv2.COLOR_BGR2HSV).astype(np.float32)
    h, s, v = hsv[:, :, 0], hsv[:, :, 1], hsv[:, :, 2]
    total_px = h.size

    # Brown/dark spots: low V (<60) + low S (<60) → bruise proxy
    dark_mask = (v < 60) & (s < 60)
    dark_ratio = dark_mask.sum() / total_px
    if dark_ratio > 0.02:
        issues.append(DetectedIssue(
            issue_type=IssueType.BROWN_SPOT,
            severity=_severity_from_ratio(dark_ratio),
            confidence=min(1.0, dark_ratio * 5),
        ))

    # Bruise-like: very dark V (<40), any saturation
    bruise_mask = v < 40
    bruise_ratio = bruise_mask.sum() / total_px
    if bruise_ratio > 0.01:
        issues.append(DetectedIssue(
            issue_type=IssueType.BRUISE_LIKE_AREA,
            severity=_severity_from_ratio(bruise_ratio),
            confidence=min(1.0, bruise_ratio * 8),
        ))

    # Wrinkling proxy: very low saturation overall (s mean < 30)
    mean_s = s.mean()
    if mean_s < 30:
        issues.append(DetectedIssue(
            issue_type=IssueType.WRINKLING,
            severity=IssueSeverity.MEDIUM if mean_s < 15 else IssueSeverity.LOW,
            confidence=round(1.0 - (mean_s / 30.0), 2),
        ))

    # Discoloration: pixels with hue far from apple hue ranges (0-15 red, 60-90 green, 150-180 red wrap)
    apple_hue = ((h <= 15) | ((h >= 60) & (h <= 90)) | (h >= 150))
    off_hue_ratio = (~apple_hue).sum() / total_px
    if off_hue_ratio > 0.30:
        issues.append(DetectedIssue(
            issue_type=IssueType.DISCOLORATION,
            severity=_severity_from_ratio(off_hue_ratio - 0.30),
            confidence=min(1.0, off_hue_ratio),
        ))

    return issues


def detect_issues_banana(crop_bgr) -> list[DetectedIssue]:
    """Rule-based issue detection for Banana.

    Checks:
    - Dark brown spots → overripening_like / brown_spot
    - Blackened regions → mold_like_area
    - Loss of yellow hue → discoloration / drying_shriveling
    """
    import numpy as np
    import cv2

    issues: list[DetectedIssue] = []
    hsv = cv2.cvtColor(crop_bgr, cv2.COLOR_BGR2HSV).astype(np.float32)
    h, s, v = hsv[:, :, 0], hsv[:, :, 1], hsv[:, :, 2]
    total_px = h.size

    # Very dark pixels → mold-like
    black_mask = v < 30
    black_ratio = black_mask.sum() / total_px
    if black_ratio > 0.005:
        issues.append(DetectedIssue(
            issue_type=IssueType.MOLD_LIKE_AREA,
            severity=_severity_from_ratio(black_ratio),
            confidence=min(1.0, black_ratio * 10),
        ))

    # Brown spots: dark-ish + warm hue (10-25 range) + low saturation
    brown_mask = (v < 80) & (h >= 10) & (h <= 25) & (s < 150)
    brown_ratio = brown_mask.sum() / total_px
    if brown_ratio > 0.05:
        issues.append(DetectedIssue(
            issue_type=IssueType.BROWN_SPOT,
            severity=_severity_from_ratio(brown_ratio),
            confidence=min(1.0, brown_ratio * 4),
        ))

    # Overripening: large non-yellow hue ratio (banana yellow hue: 20-35)
    non_yellow = ~((h >= 20) & (h <= 35))
    non_yellow_ratio = non_yellow.sum() / total_px
    if non_yellow_ratio > 0.40:
        issues.append(DetectedIssue(
            issue_type=IssueType.OVERRIPENING_LIKE,
            severity=_severity_from_ratio(non_yellow_ratio - 0.40),
            confidence=min(1.0, non_yellow_ratio),
        ))

    # Drying/shriveling: very low saturation overall
    mean_s = s.mean()
    if mean_s < 40:
        issues.append(DetectedIssue(
            issue_type=IssueType.DRYING_SHRIVELING,
            severity=IssueSeverity.MEDIUM if mean_s < 20 else IssueSeverity.LOW,
            confidence=round(1.0 - (mean_s / 40.0), 2),
        ))

    return issues


def detect_issues(crop_bgr, fruit_type: str) -> list[DetectedIssue]:
    """Dispatch to fruit-specific issue detector."""
    if fruit_type == "apple":
        return detect_issues_apple(crop_bgr)
    if fruit_type == "banana":
        return detect_issues_banana(crop_bgr)
    return []
