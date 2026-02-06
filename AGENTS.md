# Sentry-Seer-Types Development Guide for AI Agents

## Overview

This repository contains shared Pydantic models for Sentry–Seer code review integration. The package supports Python 3.11+ and provides Pydantic v1– and v2–compatible types via the `v1` and `v2` namespaces under `sentry_seer_shared_code`.

## Project Structure

```
sentry-seer-types/
├── src/
│   └── sentry_seer_shared_code/   # Top-level package (py.typed)
│       ├── v1/
│       │   ├── code_review/       # Pydantic v1 code review models
│       │   └── seer/              # Pydantic v1 Seer shared models (e.g. repo definition)
│       └── v2/
│           └── code_review/       # Pydantic v2 code review models
├── tests/
├── Makefile
└── pyproject.toml
```

The package lives under `src/` and is discovered by setuptools from there (`[tool.setuptools.packages.find] where = ["src"]`).

## Command Execution Guide

Use the Makefile for all development commands (mirrors CI).

### Setup / install

- `make install` — Install with default deps (no Pydantic pin).
- `make install-pydantic-v1` — Install with Pydantic v1 (same as CI v1 job).
- `make install-pydantic-v2` — Install with Pydantic v2 (same as CI v2 job).

### Lint, typecheck, test, build

- **Lint**: `make lint` — Runs `ruff check src/ tests/`.
- **Typecheck**: `make typecheck` — Runs `mypy src/` (CI runs this only with Pydantic v2).
- **Tests**: `make test` — Runs `pytest tests/` (with coverage per pyproject.toml).
- **Build**: `make build` — Runs `pip install build` then `python -m build`.
- **Validate install**: `make validate-install` — Creates a temp venv, installs the built wheel or editable install, and checks imports. Set `PYDANTIC_SPEC` when validating a specific Pydantic version (e.g. `make validate-install PYDANTIC_SPEC="pydantic>=1.10.23,<2"`).

### Python / venv

- Run all commands from the **repo root**.
- If the project has a virtualenv (e.g. `.venv`), use that interpreter for any direct `pytest` / `mypy` / `ruff` calls so results match `make` and CI (e.g. `.venv/bin/pytest tests/` or `source .venv/bin/activate && make test`).
- No Django or database: do not run migrate/makemigrations.

## Running specific tests or files

- Full suite: `make test` or `pytest tests/`.
- Single file: `pytest tests/test_code_review.py` (use venv interpreter if present).
- Single test: `pytest tests/test_code_review.py -k "test_minimal_valid_repo"`.

## Linting and formatting (when invoking tools directly)

- Lint: `ruff check src/ tests/` (equivalent to `make lint`).
- Format: `ruff format src/ tests/` (pre-commit also runs this).
- Pre-commit: `pre-commit run --all-files` (ruff + ruff-format + mypy on `src/`).

## Agent-specific notes

- Use **Makefile targets** for lint, typecheck, test, and build so behavior matches CI (same install matrix, same steps).
- CI matrix: Python 3.11 and 3.12 × Pydantic v1 and v2; lint and build run only on one combination (3.11 + v2), but tests run on all four.
- First-party package for isort/ruff: `sentry_seer_shared_code` (see `[tool.ruff.lint.isort]` in pyproject.toml).
- All package code lives under `src/sentry_seer_shared_code/`; keep `__init__.py` in every package directory so setuptools includes them in the wheel.
