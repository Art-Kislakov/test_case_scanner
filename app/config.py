from __future__ import annotations

# Central place for user-specific settings (paths, flags).
# Keep hardcoded file paths OUT of main.py.

# Add as many CSV paths as you want here.
TEST_CASE_FILES = [
     "/Users/artiomkisliakov/Desktop/test_case - 12345.csv",
     # "/Users/artiomkisliakov/Desktop/test_case .csv",
]

# If True, the scanner will ask to open the file when issues are found.
ASK_TO_OPEN_FILE = True

# --- Core Steps enforcement (standard CAPRI test cases only) ---
ENABLE_CORE_STEPS = True

# Anchor actions (1-based step numbers)
CORE_ANCHOR_STEP_3_ACTION = "Enter PIN and hit Enter"
CORE_ANCHOR_STEP_4_ACTION = "Click OK button"
CORE_ANCHOR_STEP_5_ACTION = "Click OK button"
CORE_ANCHOR_STEP_8_ACTION = "Click Continue button"

# Minimum required anchor matches out of 4
CORE_ANCHOR_MIN_MATCHES = 2

# How many core steps we enforce once it's detected as standard
CORE_STEPS_COUNT = 8