"""
Pytest configuration and fixtures for the Gelateria ERP test suite.
Uses an in-process SQLite-backed database via psycopg2-compatible mocks
so tests run without a real PostgreSQL server.
"""
import os
import sys

# Ensure the project root is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
