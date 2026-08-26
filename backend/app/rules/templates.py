"""
Deterministic Analysis Template Generator

Constructs short, user-facing analysis text exclusively from validated
structured issue objects. Does NOT invent or hallucinate findings.

DISCLAIMER: Describes visible external condition only.
"""

from app.cv.issues import DetectedIssue, IssueSeverity, IssueType

# Friendly label per issue type
_ISSUE_LABELS: dict[IssueType, str] = {
    IssueType.BROWN_SPOT:       "visible brown spotting",
    IssueType.BRUISE_LIKE_AREA: "bruise-like areas",
    IssueType.WRINKLING:        "surface wrinkling",
    IssueType.MOLD_LIKE_AREA:   "mold-like patches",
    IssueType.SURFACE_DAMAGE:   "surface damage",
    IssueType.DISCOLORATION:    "colour discoloration",
    IssueType.OVERRIPENING_LIKE:"signs of overripening",
    IssueType.DRYING_SHRIVELING:"drying or shriveling",
}


def _top_issues(issues: list[DetectedIssue], max_n: int = 2) -> list[DetectedIssue]:
    """Return the most severe / highest confidence issues."""
    severity_rank = {IssueSeverity.HIGH: 3, IssueSeverity.MEDIUM: 2, IssueSeverity.LOW: 1}
    return sorted(issues, key=lambda i: (severity_rank[i.severity], i.confidence), reverse=True)[:max_n]


def build_analysis(score: int, issues: list[DetectedIssue]) -> str:
    """
    Build a deterministic, template-driven analysis sentence.

    Args:
        score:  Integer freshness score 1-10.
        issues: Validated detected issues from the inference engine.

    Returns:
        A short, factual analysis string derived only from structured evidence.
    """
    top = _top_issues(issues)
    issue_labels = [_ISSUE_LABELS.get(i.issue_type, i.issue_type.value) for i in top]

    if not issues:
        if score >= 8:
            return "Looks fresh overall with no visible surface issues detected."
        if score >= 6:
            return "Generally fresh-looking appearance with minimal visible aging."
        return "Some visible signs of aging, but no specific surface issues detected."

    label_str = " and ".join(issue_labels) if len(issue_labels) <= 2 else ", ".join(issue_labels[:-1]) + f", and {issue_labels[-1]}"

    high_issues = [i for i in issues if i.severity == IssueSeverity.HIGH]

    if high_issues or score <= 3:
        return f"Significant visible {label_str} observed. Inspect closely before consumption."
    if score <= 5:
        return f"Moderate visible aging with {label_str}. Inspect closely before eating."
    if score <= 7:
        return f"Minor {label_str} visible on the surface. Generally looks acceptable."
    return f"Looks fresh overall with minor visible {label_str}."
