"""
My Masters Degree - A Python project for my masters degree research.

This package contains the main modules and utilities for my masters degree project.
"""

try:
    from importlib.metadata import version, PackageNotFoundError
    __version__ = version("my-masters-degree")
except (ImportError, PackageNotFoundError):
    # Fallback for development mode or when package is not installed
    __version__ = "0.1.0-dev"

