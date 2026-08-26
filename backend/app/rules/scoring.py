"""
Freshness Score Engine

Pipeline:
  FreshnessResult (raw_score 0-1, issues, uncertainty)
    -> uncertainty gate
    -> continuous calibration
    -> integer score 1-10
    -> product label
    -> deterministic analysis text

Score rubric:
  8-10 : Fresh-looking
   6-7 : Generally fresh
   4-5 : Moderate visible aging
   1-3 : Severe deterioration

DISCLAIMER: Estimates visible external condition only.
"""

from typing import Optional
from pydantic import BaseModel
from app.core.config import settings
from app.inference.freshness import FreshnessResult
from app.rules.templates import build_analysis


PRODUCT_LABELS: dict[range, str] = {
    range(8, 11): "Fresh-looking",
    range(6, 8):  "Generally fresh",
    range(4, 6):  "Moderate visible aging",
    range(1, 4):  "Severe deterioration",
}

_UNCERTAINTY_MESSAGE = (
    "The image is not clear enough for a reliable estimate. "
    "Try again in better light."
)


class ScoringResult(BaseModel):
    score: Optional[int] = None          # 1-10, None when UNCERTAIN
    label: Optional[str] = None
    analysis: str
    status: str                          # "OK" | "UNCERTAIN"
    uncertainty_reason: Optional[str] = None


def _raw_to_integer(raw_score: float) -> int:
    """
    Map continuous raw_score [0.0, 1.0] to integer [1, 10].
    Clamps at boundaries to guarantee the contract.
    """
    scaled = raw_score * 9.0          # 0.0 -> 0, 1.0 -> 9
    integer = int(scaled) + 1         # shift to [1, 10]
    return max(1, min(10, integer))


def _product_label(score: int) -> str:
    for score_range, label in PRODUCT_LABELS.items():
        if score in score_range:
            return label
    return "Unknown"


def _is_uncertain(result: FreshnessResult) -> bool:
    """True when evidence is too weak to produce a reliable score."""
    if result.uncertainty:
        return True
    if result.raw_score < settings.SCORE_UNCERTAINTY_THRESHOLD:
        return True
    # All issues have low confidence → weak evidence
    if result.issues and all(i.confidence < settings.SCORE_MIN_ISSUES_CONFIDENCE for i in result.issues):
        return True
    return False


def compute_score(result: FreshnessResult) -> ScoringResult:
    """
    Convert a FreshnessResult into a final deterministic ScoringResult.

    Args:
        result: Output from the freshness inference engine.

    Returns:
        ScoringResult with integer score, product label, and analysis text.
    """
    if _is_uncertain(result):
        return ScoringResult(
            score=None,
            label=None,
            analysis=_UNCERTAINTY_MESSAGE,
            status="UNCERTAIN",
            uncertainty_reason="Insufficient image evidence for a reliable estimate.",
        )

    score = _raw_to_integer(result.raw_score)
    label = _product_label(score)
    analysis = build_analysis(score, result.issues)

    return ScoringResult(
        score=score,
        label=label,
        analysis=analysis,
        status="OK",
    )
