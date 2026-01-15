from typing import Any, Dict, List
import pandas as pd

from .common import excel_row_number, is_blank_row, is_empty_like, to_int_step


def check_step_numbering(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Optional rule (only if columns exist): validate Step # numbering per Test Case ID.
    If the file doesn't contain "Test Case ID" and "Step #", the rule is skipped.
    """
    if not {"Test Case ID", "Step #"}.issubset(df.columns):
        return []

    errors: List[Dict[str, Any]] = []

    working_df = df.copy()
    working_df = working_df[~working_df.apply(is_blank_row, axis=1)]
    working_df = working_df[~working_df["Test Case ID"].apply(is_empty_like)]

    if working_df.empty:
        return errors

    grouped = working_df.groupby("Test Case ID", dropna=False)

    for tc_id, group in grouped:
        steps_in_order: List[tuple[int, int]] = []
        step_to_rows: Dict[int, List[int]] = {}
        group_rows: List[int] = []

        for idx, row in group.iterrows():
            row_num = excel_row_number(idx)
            group_rows.append(row_num)

            raw = row.get("Step #", "")
            step_int = to_int_step(raw)

            if step_int is None:
                if is_empty_like(raw):
                    errors.append({"row": row_num, "error": f"Step # is empty (Test Case ID: {tc_id})"})
                else:
                    errors.append({"row": row_num, "error": f'Step # is not a number: "{str(raw).strip()}" (Test Case ID: {tc_id})'})
                continue

            steps_in_order.append((row_num, step_int))
            step_to_rows.setdefault(step_int, []).append(row_num)

        if not steps_in_order:
            continue

        for step, rows in step_to_rows.items():
            if len(rows) > 1:
                for r in rows:
                    errors.append({"row": r, "error": f"Duplicate Step # {step} in Test Case ID {tc_id}"})

        valid_steps = sorted(step_to_rows.keys())
        max_step = max(valid_steps)
        missing = sorted(set(range(1, max_step + 1)) - set(valid_steps))
        if missing:
            first_row = min(group_rows)
            errors.append({"row": first_row, "error": f"Missing Step # in Test Case ID {tc_id}: {', '.join(map(str, missing))}"})

        ordered = [s for (_, s) in steps_in_order]
        for i in range(1, len(ordered)):
            if ordered[i] < ordered[i - 1]:
                bad_row = steps_in_order[i][0]
                errors.append({"row": bad_row, "error": "Step # is out of order in Test Case ID {tc_id} (expected ascending order)"})
                break

    return errors