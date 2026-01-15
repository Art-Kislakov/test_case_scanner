from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict


@dataclass(frozen=True)
class CoreStep:
    action: str
    expected: str


CORE_STEPS: List[CoreStep] = [
    CoreStep(
        action="Launch CAPRI application from desktop",
        expected="Windows Security Certificate Selection window pop-up displays.",
    ),
    CoreStep(
        action="Select appropriate PIV Card Certificate and select OK button",
        expected="ActivClient Login pin screen displays.",
    ),
    CoreStep(
        action="Enter PIN and hit Enter",
        expected="System Use Notification window displays.",
    ),
    CoreStep(
        action="Click OK button",
        expected="CAPRI News feed displays.",
    ),
    CoreStep(
        action="Click Close button",
        expected="CAPRI GUI version pop-up displays.",
    ),
    CoreStep(
        action="Click OK button",
        expected="CAPRI alerts screen displays.",
    ),
    CoreStep(
        action="Click Continue button",
        expected="CAPRI application loads. Patient Selector screen displays.",
    ),
    CoreStep(
        action="Search for Patient using Name or SSN",
        expected="Patient record is displayed.",
    ),
]


def normalize_spaces(text: str) -> str:
    """Trim and collapse multiple spaces into one. Keep punctuation unchanged."""
    if text is None:
        return ""
    return " ".join(str(text).strip().split())


def steps_match(a: str, b: str) -> bool:
    """Strict match with whitespace normalization."""
    return normalize_spaces(a) == normalize_spaces(b)


def is_standard_case(steps: List[Dict[str, str]], *, anchor3: str, anchor4: str) -> bool:
    """
    Detect standard CAPRI test case by checking two anchor actions:
    - step 3 action
    - step 4 action
    """
    if len(steps) < 4:
        return False

    s3 = normalize_spaces(steps[2].get("action", ""))  # step 3 (0-based index 2)
    s4 = normalize_spaces(steps[3].get("action", ""))  # step 4 (0-based index 3)

    return s3 == normalize_spaces(anchor3) and s4 == normalize_spaces(anchor4)