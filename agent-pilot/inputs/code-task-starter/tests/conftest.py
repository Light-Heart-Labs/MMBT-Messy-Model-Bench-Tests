"""Shared pytest fixtures."""
import sys
from pathlib import Path

# Make logalyzer importable when tests run from the project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
