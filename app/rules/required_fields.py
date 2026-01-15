from typing import Any, Dict, List
import pandas as pd
from .common import is_empty_like, excel_row_number, is_blank_row, make_issue

RULE_ID = "REQUIRED_FIELDS"
SEVERITY = "FAIL"


def check_required_fields(df: pd.DataFrame) -> List[Dict[str, Any]]:
    issues: List[Dict[str, Any]] = []

    required_cols = {"Action", "Expected Results"}
    if not required_cols.issubset(df.columns):
        return issues

    for idx, row in df.iterrows():
        if is_blank_row(row):
            continue

        row_num = excel_row_number(idx)

        if is_empty_like(row.get("Action", "")):
            issues.append(
                make_issue(
                    row=row_num,
                    message="Action is empty",
                    rule=RULE_ID,
                    severity=SEVERITY,
                    field="Action",
                )
            )

        if is_empty_like(row.get("Expected Results", "")):
            issues.append(
                make_issue(
                    row=row_num,
                    message="Expected Results is empty",
                    rule=RULE_ID,
                    severity=SEVERITY,
                    field="Expected Results",
                )
            )

    return issues