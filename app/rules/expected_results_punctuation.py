from typing import Any, Dict, List
import pandas as pd

from .common import is_empty_like, excel_row_number, is_blank_row, make_issue

RULE_ID = "EXPECTED_RESULTS_PUNCTUATION"
SEVERITY = "WARNING"


def check_expected_results_punctuation(df: pd.DataFrame) -> List[Dict[str, Any]]:
    issues: List[Dict[str, Any]] = []

    if "Expected Results" not in df.columns:
        return issues

    for idx, row in df.iterrows():
        if is_blank_row(row):
            continue

        value = row.get("Expected Results", "")
        if is_empty_like(value):
            continue  # FAIL already handled elsewhere

        text = str(value).strip()
        if not text.endswith("."):
            issues.append(
                make_issue(
                    row=excel_row_number(idx),
                    message="Expected Results should end with a period (.)",
                    rule=RULE_ID,
                    severity=SEVERITY,
                    field="Expected Results",
                )
            )

    return issues