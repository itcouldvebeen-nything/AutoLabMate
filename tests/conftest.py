"""
Pytest configuration and shared fixtures
"""

import pytest
import os
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

# Set test environment variables
os.environ["MOCK_MODE"] = "true"
os.environ["LOG_LEVEL"] = "DEBUG"
os.environ["USE_SQLITE"] = "true"

