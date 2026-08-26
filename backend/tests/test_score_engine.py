import pytest
from app.rules.scoring import compute_score, ScoringResult, _raw_to_integer, _product_label
from app.rules.templates import build_analysis
from app.inference.freshness import FreshnessResult
from app.cv.issues import DetectedIssue, IssueType, IssueSeverity
from app.core.config import settings


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _result(raw_score: float = 0.8, uncertainty: bool = False, issues: list = None) -> FreshnessResult:
    return FreshnessResult(
        fruit_type="apple",
        raw_score=raw_score,
        issues=issues or [],
        uncertainty=uncertainty,
    )


def _issue(severity: IssueSeverity = IssueSeverity.LOW, confidence: float = 0.9) -> DetectedIssue:
    return DetectedIssue(
        issue_type=IssueType.BROWN_SPOT,
        severity=severity,
        confidence=confidence,
    )


# ---------------------------------------------------------------------------
# Integer score mapping
# ---------------------------------------------------------------------------

def test_score_minimum_is_1():
    assert _raw_to_integer(0.0) == 1

def test_score_maximum_is_10():
    assert _raw_to_integer(1.0) == 10

def test_score_midpoint():
    score = _raw_to_integer(0.5)
    assert 1 <= score <= 10

def test_score_always_integer():
    for v in [0.0, 0.1, 0.33, 0.5, 0.75, 0.99, 1.0]:
        s = _raw_to_integer(v)
        assert isinstance(s, int)
        assert 1 <= s <= 10

def test_higher_raw_gives_higher_or_equal_score():
    assert _raw_to_integer(0.8) >= _raw_to_integer(0.4)


# ---------------------------------------------------------------------------
# Product label mapping
# ---------------------------------------------------------------------------

def test_label_score_10():
    assert _product_label(10) == "Fresh-looking"

def test_label_score_8():
    assert _product_label(8) == "Fresh-looking"

def test_label_score_6():
    assert _product_label(6) == "Generally fresh"

def test_label_score_5():
    assert _product_label(5) == "Moderate visible aging"

def test_label_score_1():
    assert _product_label(1) == "Severe deterioration"


# ---------------------------------------------------------------------------
# Uncertainty gate
# ---------------------------------------------------------------------------

def test_uncertainty_flag_triggers_uncertain_status():
    result = compute_score(_result(raw_score=0.5, uncertainty=True))
    assert result.status == "UNCERTAIN"
    assert result.score is None

def test_low_raw_score_triggers_uncertain_status():
    settings.SCORE_UNCERTAINTY_THRESHOLD = 0.10
    result = compute_score(_result(raw_score=0.05))
    assert result.status == "UNCERTAIN"

def test_good_input_gives_ok_status():
    settings.SCORE_UNCERTAINTY_THRESHOLD = 0.10
    result = compute_score(_result(raw_score=0.75))
    assert result.status == "OK"
    assert isinstance(result.score, int)
    assert 1 <= result.score <= 10

def test_uncertain_result_contains_standard_message():
    result = compute_score(_result(uncertainty=True))
    assert "not clear enough" in result.analysis.lower() or "reliable estimate" in result.analysis.lower()

def test_no_hallucinated_score_when_uncertain():
    result = compute_score(_result(raw_score=0.02))
    assert result.score is None
    assert result.label is None


# ---------------------------------------------------------------------------
# Deterministic analysis templates
# ---------------------------------------------------------------------------

def test_analysis_no_issues_high_score():
    text = build_analysis(9, [])
    assert "fresh" in text.lower()

def test_analysis_no_issues_low_score():
    text = build_analysis(2, [])
    assert len(text) > 0

def test_analysis_with_high_severity_issue():
    issues = [_issue(severity=IssueSeverity.HIGH, confidence=0.95)]
    text = build_analysis(3, issues)
    assert "inspect" in text.lower()

def test_analysis_text_is_string():
    text = build_analysis(7, [_issue()])
    assert isinstance(text, str)
    assert len(text) > 0

def test_analysis_does_not_contain_raw_score():
    # Template must not echo numeric raw scores
    for score in range(1, 11):
        text = build_analysis(score, [])
        assert str(score) not in text
