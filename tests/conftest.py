"""Shared test configuration and fixtures."""

import sys
import os

# Ensure the project root is on the Python path so tests can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
