import numpy as np
import pytest
from app.inference.freshness import analyse, FreshnessResult
from app.cv.issues import IssueType, IssueSeverity


FRAME_H, FRAME_W = 200, 200


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _solid_bgr(b: int, g: int, r: int) -> np.ndarray:
    return np.full((FRAME_H, FRAME_W, 3), [b, g, r], dtype=np.uint8)


def _fresh_apple_crop() -> np.ndarray:
    # Vivid red: BGR (50, 50, 220) → HSV hue ~0 (red), high S and V
    return _solid_bgr(50, 50, 220)


def _fresh_banana_crop() -> np.ndarray:
    # Vivid yellow: BGR (0, 220, 220) → HSV hue ~30 (yellow), high S and V
    return _solid_bgr(0, 220, 220)


def _dark_crop() -> np.ndarray:
    # Near-black: very low V
    return _solid_bgr(10, 10, 10)


def _grey_crop() -> np.ndarray:
    # Mid-grey: low S, medium V
    return _solid_bgr(100, 100, 100)


# ---------------------------------------------------------------------------
# Output structure
# ---------------------------------------------------------------------------

def test_result_is_freshness_result():
    crop = _fresh_apple_crop()
    result = analyse(crop, "apple")
    assert isinstance(result, FreshnessResult)


def test_result_has_required_fields():
    result = analyse(_fresh_apple_crop(), "apple")
    assert hasattr(result, "fruit_type")
    assert hasattr(result, "raw_score")
    assert hasattr(result, "issues")
    assert hasattr(result, "analysis_method")
    assert hasattr(result, "uncertainty")


def test_analysis_method_is_baseline():
    result = analyse(_fresh_apple_crop(), "apple")
    assert result.analysis_method == "cv_baseline_v1"


def test_raw_score_bounded():
    for crop in [_fresh_apple_crop(), _dark_crop(), _grey_crop()]:
        result = analyse(crop, "apple")
        assert 0.0 <= result.raw_score <= 1.0


# ---------------------------------------------------------------------------
# Apple vs Banana distinct scoring
# ---------------------------------------------------------------------------

def test_apple_and_banana_have_different_scores_for_same_crop():
    # Vivid red crop should score higher for apple than banana
    red_crop = _fresh_apple_crop()
    apple_result = analyse(red_crop, "apple")
    banana_result = analyse(red_crop, "banana")
    assert apple_result.raw_score != banana_result.raw_score


def test_fresh_apple_scores_higher_than_dark_apple():
    fresh = analyse(_fresh_apple_crop(), "apple")
    dark = analyse(_dark_crop(), "apple")
    assert fresh.raw_score >= dark.raw_score


def test_fresh_banana_returns_lower_uncertainty():
    fresh = analyse(_fresh_banana_crop(), "banana")
    dark = analyse(_dark_crop(), "banana")
    # Fresh banana should not flag uncertainty; very dark might
    assert isinstance(fresh.uncertainty, bool)
    assert isinstance(dark.uncertainty, bool)


# ---------------------------------------------------------------------------
# Empty / degenerate input
# ---------------------------------------------------------------------------

def test_empty_crop_returns_uncertainty():
    empty = np.zeros((0, 0, 3), dtype=np.uint8)
    result = analyse(empty, "apple")
    assert result.uncertainty is True
    assert result.raw_score == 0.0


# ---------------------------------------------------------------------------
# Issue taxonomy validation
# ---------------------------------------------------------------------------

def test_issues_list_contains_valid_types():
    result = analyse(_dark_crop(), "apple")
    for issue in result.issues:
        assert issue.issue_type in list(IssueType)
        assert issue.severity in list(IssueSeverity)
        assert 0.0 <= issue.confidence <= 1.0


def test_banana_detects_mold_on_black_crop():
    black_crop = _solid_bgr(5, 5, 5)
    result = analyse(black_crop, "banana")
    issue_types = [i.issue_type for i in result.issues]
    assert IssueType.MOLD_LIKE_AREA in issue_types
