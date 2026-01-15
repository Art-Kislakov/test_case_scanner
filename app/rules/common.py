from typing import Dict, Any, Optional
import pandas as pd

# Values treated as empty in test cases
EMPTY_LIKE_VALUES = {"", "-", "--", "n/a", "na", "none", "null", "nil", "empty"}


def is_empty_like(value: Any) -> bool:
    """Return True if a value should be treated as empty."""
    if value is None:
        return True
    try:
        if pd.isna(value):
            return True
    except Exception:
        pass

    text = str(value).strip()
    if text == "":
        return True
    return text.lower() in EMPTY_LIKE_VALUES


def excel_row_number(df_index: int) -> int:
    """
    Convert DataFrame index to Excel row number.
    Row 1 = header, first data row starts at row 2.
    """
    return df_index + 2


def is_blank_row(row: pd.Series) -> bool:
    """Treat row as blank if all known key columns are empty-like."""
    candidates = [
        row.get("Test Case ID", ""),
        row.get("Step #", ""),
        row.get("Action", ""),
        row.get("Input Data", ""),
        row.get("Data", ""),
        row.get("Expected Results", ""),
    ]
    return all(is_empty_like(v) for v in candidates)


def to_int_step(value: Any) -> Optional[int]:
    """Convert Step # to integer if possible."""
    if is_empty_like(value):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value) if value.is_integer() else None

    text = str(value).strip()
    try:
        f = float(text)
        return int(f) if f.is_integer() else None
    except ValueError:
        return None


def make_issue(
        *,
        row: Optional[int],
        message: str,
        rule: str,
        severity: str = "FAIL",
        field: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Standard issue factory for all rules.
    """
    issue: Dict[str, Any] = {
        "row": row,
        "message": message,
        "rule": rule,
        "severity": severity,
    }

    if field:
        issue["field"] = field

    return issue