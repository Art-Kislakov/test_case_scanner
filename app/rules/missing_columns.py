from typing import Any, Dict, List, Set
import pandas as pd
from .common import make_issue

RULE_ID = "MISSING_COLUMNS"
SEVERITY = "FAIL"


def check_missing_columns(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    FAIL check: required columns must exist in the input file.
    Returns one issue listing all missing columns.
    """
    issues: List[Dict[str, Any]] = []

    required: Set[str] = {"Action", "Expected Results"}
    missing = sorted(required - set(df.columns))

    if missing:
        issues.append(
            make_issue(
                row=None,
                message=f"Missing required columns: {', '.join(missing)}",
                rule=RULE_ID,
                severity=SEVERITY,
            )
        )

    return issues