"""
Configuration for test suite
"""

import os
import sys
from pathlib import Path

# Add the parent directory to the Python path so we can import our modules
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Test data paths
TEST_DATA_DIR = PROJECT_ROOT / "tests" / "test_data"
SAMPLE_PDF_PATH = PROJECT_ROOT / "input" / "table.pdf"

# Expected test results
EXPECTED_CATEGORIES = ["Blind", "Low Vision", "Dexterity", "Mobility"]
EXPECTED_COLUMNS = ["Disability Category", "Participants", "Ballots Completed"]

# Test configuration
DEEPEVAL_MODEL = "gpt-3.5-turbo"  # You can change this to your preferred model