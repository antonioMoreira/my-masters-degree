"""
My Masters Degree - A Python project for my masters degree research.

This package contains the main modules and utilities for my masters degree project.
"""

try:
    from importlib.metadata import version
    __version__ = version("my-masters-degree")
except ImportError:
    # Fallback for development mode
    __version__ = "0.1.0"
