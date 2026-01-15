from typing import Any, Dict, List, Set
import pandas as pd

from .common import is_empty_like, excel_row_number, is_blank_row, make_issue

RULE_ID = "GENERIC_EXPECTED_RESULTS"
SEVERITY = "WARNING"

# Phrases that are considered too generic for Expected Results
GENERIC_PHRASES: Set[str] = {
    "ok",
    "okay",
    "works",
    "work",
    "done",
    "completed",
    "complete",
    "success",
    "successful",
    "pass",
    "passed",
    "correct",
    "correctly",
    "as expected",
}


def _normalize(text: Any) -> str:
    """Normalize text for comparison."""
    if text is None:
        return ""
    return str(text).strip().lower()


def check_generic_expected_results(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    WARNING rule:
    Expected Results should not be generic values like:
    ok / works / done / success.
    """
    issues: List[Dict[str, Any]] = []

    # Guard: if the column does not exist, do nothing
    if "Expected Results" not in df.columns:
        return issues

    for idx, row in df.iterrows():
        if is_blank_row(row):
            continue

        expected = row.get("Expected Results", "")
        if is_empty_like(expected):
            # Empty Expected Results are handled by REQUIRED_FIELDS (FAIL)
            continue

        expected_norm = _normalize(expected)

        # Case 1: exact match with a generic phrase
        if expected_norm in GENERIC_PHRASES:
            row_num = excel_row_number(idx)
            issues.append(
                make_issue(
                    row=row_num,
                    message=f'Expected Results is too generic ("{str(expected).strip()}")',
                    rule=RULE_ID,
                    severity=SEVERITY,
                    field="Expected Results",
                )
            )
            continue

        # Case 2: very short Expected Results (e.g. "ok.", "yes", "no")
        if len(expected_norm) <= 3:
            row_num = excel_row_number(idx)
            issues.append(
                make_issue(
                    row=row_num,
                    message=f'Expected Results is too short ("{str(expected).strip()}")',
                    rule=RULE_ID,
                    severity=SEVERITY,
                    field="Expected Results",
                )
            )

    return issues