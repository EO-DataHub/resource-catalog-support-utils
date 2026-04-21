"""
Pytest configuration and fixtures for tests.

This file ensures the project root is in the Python path so tests can import
the app module.
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
