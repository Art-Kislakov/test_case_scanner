import pandas as pd

from app.rules.required_fields import check_required_fields
from app.rules.blank_rows import check_blank_rows
from app.rules.step_numbering import check_step_numbering
from app.rules.data_required import check_data_required_for_actions
from app.rules.missing_columns import check_missing_columns
from app.rules.expected_results_punctuation import check_expected_results_punctuation
from app.rules.generic_expected_results import check_generic_expected_results

# Core Steps (new feature)
from app import config as cfg
from app.core_steps import CORE_STEPS, steps_match

RULES = [
    check_missing_columns,
    check_required_fields,
    check_blank_rows,
    check_data_required_for_actions,
    check_expected_results_punctuation,
    check_generic_expected_results,
]

CONDITIONAL_RULES = [
    ({"Test Case ID", "Step #"}, check_step_numbering),
]


def _safe_getattr(name: str, default):
    """Safely read config values without crashing if a setting is missing."""
    return getattr(cfg, name, default)


def check_core_steps_enforcement(df: pd.DataFrame) -> list:
    """
    Enforce "Core Steps" for standard CAPRI test cases.

    Detection (standard case):
      - We compare Actions for anchor steps: 3, 4, 5, 8 (1-based)
      - If at least MIN matches (default: 2) are found -> standard case detected

    Enforcement:
      - Once detected, enforce the first CORE_STEPS_COUNT steps (default: 8)
      - Strict match with whitespace normalization (trim + multiple spaces -> one)
      - Adds WARNING issues (does not FAIL on the first scan)
    """
    # Feature toggle
    if not _safe_getattr("ENABLE_CORE_STEPS", False):
        return []

    # Required columns for this feature
    if "Action" not in df.columns or "Expected Results" not in df.columns:
        return []

    # Read anchor configs (defaults are safe; if missing, detection will likely fail gracefully)
    anchor_step_map = {
        3: _safe_getattr("CORE_ANCHOR_STEP_3_ACTION", ""),
        4: _safe_getattr("CORE_ANCHOR_STEP_4_ACTION", ""),
        5: _safe_getattr("CORE_ANCHOR_STEP_5_ACTION", ""),
        8: _safe_getattr("CORE_ANCHOR_STEP_8_ACTION", ""),
    }
    min_matches = int(_safe_getattr("CORE_ANCHOR_MIN_MATCHES", 2))
    core_steps_count = int(_safe_getattr("CORE_STEPS_COUNT", 8))

    # Build "steps" list from the DataFrame (row order == step order)
    steps = []
    for _, row in df.iterrows():
        steps.append(
            {
                "action": "" if pd.isna(row.get("Action")) else str(row.get("Action")),
                "expected": "" if pd.isna(row.get("Expected Results")) else str(row.get("Expected Results")),
            }
        )

    # Not enough steps to even check anchors
    if len(steps) < max(anchor_step_map.keys()):
        return []

    # Count how many anchor actions match
    match_count = 0
    for step_num, expected_action in anchor_step_map.items():
        if not expected_action:
            continue
        idx = step_num - 1  # convert 1-based -> 0-based
        found_action = steps[idx].get("action", "")
        if steps_match(found_action, expected_action):
            match_count += 1

    # If this is not a standard case, do not enforce core steps at all
    if match_count < min_matches:
        return []

    # Enforce core steps (first N steps)
    issues = []
    enforce_n = min(core_steps_count, len(CORE_STEPS), len(steps))

    for i in range(enforce_n):
        expected_action = CORE_STEPS[i].action
        expected_expected = CORE_STEPS[i].expected

        found_action = steps[i].get("action", "")
        found_expected = steps[i].get("expected", "")

        # Excel row number:
        # Row 1 = headers, first data row is Excel row 2
        excel_row = i + 2

        # Action mismatch
        if not steps_match(found_action, expected_action):
            issues.append(
                {
                    "severity": "WARNING",
                    "excel_row": excel_row,
                    "message": (
                        f'Core Step {i + 1} Action mismatch. '
                        f'Expected: "{expected_action}" | Found: "{found_action}".'
                    ),
                }
            )

        # Expected Results mismatch
        if not steps_match(found_expected, expected_expected):
            issues.append(
                {
                    "severity": "WARNING",
                    "excel_row": excel_row,
                    "message": (
                        f'Core Step {i + 1} Expected Results mismatch. '
                        f'Expected: "{expected_expected}" | Found: "{found_expected}".'
                    ),
                }
            )

    return issues


class TestCaseScanner:
    """
    Scans a CSV file with test cases and applies validation rules.
    """

    def __init__(self, csv_path: str):
        self.csv_path = csv_path
        self.df = None

    def load_csv(self) -> pd.DataFrame:
        """
        Load CSV file into a pandas DataFrame.
        NOTE: No printing/logging here. Output is handled by main.py only.
        """
        try:
            self.df = pd.read_csv(self.csv_path)
            return self.df
        except Exception as e:
            raise RuntimeError(f"Failed to load CSV file: {e}")

    def scan(self) -> dict:
        """
        Run validation rules and return structured results.
        NOTE: No printing/logging here. Output is handled by main.py only.
        """
        df = self.load_csv()

        errors = []

        # STEP 1: PRE-FLIGHT CHECK (schema / columns)
        errors.extend(check_missing_columns(df))

        # If required columns are missing, stop early
        if errors:
            return {
                "rows": len(df),
                "columns": list(df.columns),
                "errors": errors,
            }

        # STEP 2: REGULAR RULES
        for rule in RULES:
            errors.extend(rule(df))

        # STEP 2.5: CORE STEPS (optional feature, adds WARNINGs)
        errors.extend(check_core_steps_enforcement(df))

        # STEP 3: CONDITIONAL RULES
        for required_columns, rule in CONDITIONAL_RULES:
            if required_columns.issubset(df.columns):
                errors.extend(rule(df))

        return {
            "rows": len(df),
            "columns": list(df.columns),
            "errors": errors,
        }