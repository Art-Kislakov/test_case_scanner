from typing import Any, Dict, List
import pandas as pd
from .common import excel_row_number, is_blank_row, make_issue

RULE_ID = "BLANK_ROW"

def check_blank_rows(df: pd.DataFrame) -> List[Dict[str, Any]]:
    issues: List[Dict[str, Any]] = []

    for idx, row in df.iterrows():
        if is_blank_row(row):
            issues.append(make_issue(
                row=excel_row_number(idx),
                message="Blank row",
                rule=RULE_ID,
                severity="WARNING",
            ))

    return issues