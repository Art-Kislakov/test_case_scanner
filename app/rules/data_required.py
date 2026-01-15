from typing import Any, Dict, List
import pandas as pd
from .common import excel_row_number, is_blank_row, is_empty_like, make_issue

RULE_ID = "DATA_REQUIRED"

def check_data_required_for_actions(df: pd.DataFrame) -> List[Dict[str, Any]]:
    issues: List[Dict[str, Any]] = []

    if not {"Action", "Data"}.issubset(df.columns):
        return issues

    target_action = "search for patient using name or ssn"

    for idx, row in df.iterrows():
        if is_blank_row(row):
            continue

        action = str(row.get("Action", "")).strip().lower()
        data = row.get("Data", "")

        if action == target_action and is_empty_like(data):
            issues.append(make_issue(
                row=excel_row_number(idx),
                message="Data is required for this Action (provide patient name or SSN)",
                rule=RULE_ID,
                severity="FAIL",
                field="Data",
            ))

    return issues