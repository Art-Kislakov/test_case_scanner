from __future__ import annotations

import os
import sys
import subprocess
from typing import List, Dict, Any, Optional, Union, Tuple

from app.scanner import TestCaseScanner
from app.config import TEST_CASE_FILES, ASK_TO_OPEN_FILE


def filename_only(path: str) -> str:
    """Return filename without full path."""
    return os.path.basename(path)


def format_columns(columns: List[str]) -> str:
    """Return columns in a human-readable format."""
    return " | ".join(col.strip() for col in columns)


def extract_excel_row(err: Union[Dict[str, Any], str]) -> Optional[int]:
    """Extract Excel row number from an error record (if present)."""
    if isinstance(err, str):
        return None

    for key in ("excel_row", "excelRow", "row", "Row", "excel"):
        if key in err and err[key] is not None:
            try:
                return int(err[key])
            except Exception:
                pass
    return None


def extract_message(err: Union[Dict[str, Any], str]) -> str:
    """Extract a human-readable message from an error record."""
    if isinstance(err, str):
        return err.strip()

    for key in ("message", "issue", "error", "msg", "details", "text", "Issue", "Error"):
        val = err.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()

    # Fallback: first non-empty string value
    for _, val in err.items():
        if isinstance(val, str) and val.strip():
            return val.strip()

    return ""


def extract_severity(err: Union[Dict[str, Any], str]) -> str:
    """
    Extract severity from an error record.
    Defaults to FAIL for backward compatibility with older rules.
    """
    if isinstance(err, str):
        return "FAIL"

    sev = err.get("severity") or err.get("level") or err.get("type")
    if isinstance(sev, str) and sev.strip():
        sev_norm = sev.strip().upper()
        if sev_norm in {"FAIL", "ERROR"}:
            return "FAIL"
        if sev_norm in {"WARNING", "WARN"}:
            return "WARNING"
        if sev_norm in {"INFO"}:
            return "INFO"

    return "FAIL"


def summarize_issues(errors: List[Union[Dict[str, Any], str]]) -> Tuple[int, int, int]:
    """Return (fail_count, warning_count, info_count)."""
    fail = warning = info = 0
    for e in errors:
        sev = extract_severity(e)
        if sev == "FAIL":
            fail += 1
        elif sev == "WARNING":
            warning += 1
        else:
            info += 1
    return fail, warning, info


def apply_strict_mode(
        errors: List[Union[Dict[str, Any], str]]
) -> List[Union[Dict[str, Any], str]]:
    """
    Strict mode:
      - Promote WARNING -> FAIL
      - Keep INFO as INFO
      - Keep FAIL as FAIL

    This is implemented in main.py so we do not need to touch scanner/rules.
    """
    strict_errors: List[Union[Dict[str, Any], str]] = []

    for e in errors:
        if isinstance(e, str):
            # Backward compatibility: strings are treated as FAIL
            strict_errors.append(e)
            continue

        sev = extract_severity(e)
        if sev == "WARNING":
            new_e = dict(e)
            new_e["severity"] = "FAIL"
            strict_errors.append(new_e)
        else:
            strict_errors.append(e)

    return strict_errors


def print_human_report(
        *,
        file_path: str,
        columns: List[str],
        steps_loaded: int,
        steps_scanned: int,
        errors: List[Union[Dict[str, Any], str]],
        header_suffix: str = "",
) -> None:
    """
    Print a human-readable QA/Jira-friendly report.
    This function is the ONLY place responsible for console output.
    """
    print(f"Loading test case file: {filename_only(file_path)}\n")

    print(f"Columns: {format_columns(columns)}")
    print(f"Steps loaded: {steps_loaded}\n")

    print("==============================")
    title = "TEST CASE SCAN REPORT" + (f" {header_suffix}" if header_suffix else "")
    print(title)
    print("==============================")
    print(f"Steps scanned: {steps_scanned}\n")

    fail_count, warning_count, info_count = summarize_issues(errors)
    issues_found = len(errors)

    if issues_found == 0:
        status = "PASS ✅"
    elif fail_count > 0:
        status = "FAIL ❌"
    else:
        status = "PASS (Warnings) ⚠️"

    print(f"Status: {status}")
    print(f"Issues found: {issues_found}")

    # Optional breakdown (kept minimal)
    if issues_found > 0:
        parts = []
        if fail_count:
            parts.append(f"FAIL={fail_count}")
        if warning_count:
            parts.append(f"WARNING={warning_count}")
        if info_count:
            parts.append(f"INFO={info_count}")
        print(f"Breakdown: {', '.join(parts)}")

    print()

    if issues_found == 0:
        return

    # Group issues by Excel row for clean output
    grouped: Dict[str, List[Union[Dict[str, Any], str]]] = {}
    for err in errors:
        row = extract_excel_row(err)
        group_key = f"Excel Row {row}" if row is not None else "Excel Row ?"
        grouped.setdefault(group_key, []).append(err)

    def sort_key(k: str) -> int:
        try:
            return int(k.replace("Excel Row", "").strip())
        except Exception:
            return 10**9

    for group in sorted(grouped.keys(), key=sort_key):
        print(f"{group}:")
        for err in grouped[group]:
            msg = extract_message(err)
            if not msg:
                continue

            sev = extract_severity(err)
            if sev == "FAIL":
                prefix = "FAIL"
            elif sev == "WARNING":
                prefix = "WARNING"
            else:
                prefix = "INFO"

            print(f"  {prefix}: {msg}")
        print()


def resolve_csv_path() -> str:
    """
    Resolve CSV path.
    Priority:
      1) CLI argument: python app/main.py path/to/file.csv
      2) First path from config.py (TEST_CASE_FILES[0])
      3) Default hardcoded path (your previous working behavior) - kept as-is on purpose
    """
    default_path = "/Users/artiomkisliakov/Desktop/test_case - 12345.csv"

    if len(sys.argv) >= 2 and sys.argv[1].strip():
        return sys.argv[1].strip()

    if TEST_CASE_FILES and isinstance(TEST_CASE_FILES[0], str) and TEST_CASE_FILES[0].strip():
        return TEST_CASE_FILES[0].strip()

    return default_path


def ask_yes_no(prompt: str) -> bool:
    """Return True if user answers 'y' (case-insensitive). Default is No."""
    ans = input(prompt).strip().lower()
    return ans == "y"


def open_file_with_default_app(file_path: str) -> None:
    """
    Open file with the OS default application.
    Works on macOS (open), Windows (start), Linux (xdg-open).
    """
    try:
        if sys.platform.startswith("darwin"):
            subprocess.run(["open", file_path], check=False)
        elif os.name == "nt":
            os.startfile(file_path)  # type: ignore[attr-defined]
        else:
            subprocess.run(["xdg-open", file_path], check=False)
    except Exception:
        # If opening fails, we do not crash the program.
        pass


def run_scan(csv_path: str) -> Dict[str, Any]:
    """Run scanner once and return result dict."""
    scanner = TestCaseScanner(csv_path)
    return scanner.scan()


def main() -> None:
    csv_path = resolve_csv_path()

    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    # 1) NORMAL scan
    result = run_scan(csv_path)
    columns = result.get("columns", [])
    steps_loaded = int(result.get("rows", 0))
    errors = result.get("errors", [])

    print_human_report(
        file_path=csv_path,
        columns=columns,
        steps_loaded=steps_loaded,
        steps_scanned=steps_loaded,
        errors=errors,
    )

    if len(errors) == 0:
        return

    # Ask to open the file (UI-like helper)
    if ASK_TO_OPEN_FILE and ask_yes_no("Open the file now? [y/N]: "):
        open_file_with_default_app(csv_path)
        print("File opened. Fix issues in Excel -> Save the file.\n")

    # 2) FINAL CHECK loop (strict scan)
    # Approved UX: Enter = run FINAL CHECK, 'q' = quit.
    while True:
        cmd = input("Press Enter to run FINAL CHECK (or type 'q' to quit): ").strip().lower()
        if cmd == "q":
            return

        result2 = run_scan(csv_path)
        columns2 = result2.get("columns", columns)
        steps_loaded2 = int(result2.get("rows", steps_loaded))
        errors2 = result2.get("errors", [])

        # Strict mode: promote WARNING -> FAIL
        strict_errors2 = apply_strict_mode(errors2)

        print()
        print_human_report(
            file_path=csv_path,
            columns=columns2,
            steps_loaded=steps_loaded2,
            steps_scanned=steps_loaded2,
            errors=strict_errors2,
            header_suffix="(FINAL CHECK)",
        )

        if len(strict_errors2) == 0:
            return

        # If still issues, offer to open the file again for quick fixing.
        if ASK_TO_OPEN_FILE and ask_yes_no("Open the file now? [y/N]: "):
            open_file_with_default_app(csv_path)
            print("File opened. Fix issues in Excel -> Save the file.\n")


if __name__ == "__main__":
    main()