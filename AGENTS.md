# Agent Instructions

- When running ad-hoc or temporary Python snippets/scripts, create `.py` files in `/tmp/` and execute them using `uv run` (e.g., `uv run python /tmp/script.py`) instead of passing inline code via `python -c`. Do not remove temporary scripts in `/tmp/` afterward.
- Run `uv run ruff check` and `uv run ty check` to lint and type-check Python code changes.
