# Sentry-Seer Types

Shared Pydantic models for validating payloads between Sentry and Seer code review integration.

## Purpose

This package provides type-safe validation for code review requests sent from Sentry to Seer. By sharing the same Pydantic models between both services:

- **Tests catch schema mismatches** - No more discovering payload errors in production
- **Runtime validation** - Invalid payloads are rejected before being sent to Seer
- **Type safety** - IDEs provide autocomplete and type checking
- **Single source of truth** - Schema changes are immediately visible to both services

## Installation

```bash
pip install sentry-seer-types
```

## Usage

### Validating Payloads in Sentry

```python
from sentry_seer_types import CodeReviewTaskRequest
from pydantic import ValidationError

# Validate payload before sending to Seer
payload = {
    "request_type": "pr-review",
    "external_owner_id": "12345",
    "data": {...}
}

try:
    validated = CodeReviewTaskRequest.model_validate(payload)
    # Send to Seer
except ValidationError as e:
    logger.error("Invalid payload", extra={"errors": e.errors()})
```

### In Tests

```python
from sentry_seer_types import CodeReviewTaskRequest

def test_webhook_creates_valid_payload():
    # ... trigger webhook ...
    payload = mock_seer.call_args[1]["payload"]
    
    # Validate against Seer's schema
    validated = CodeReviewTaskRequest.model_validate(payload)
    assert validated.request_type == "pr-review"
    assert validated.data.repo.name == "my-repo"
```

## Development

### Quick Start

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests with coverage
pytest

# Type checking
mypy src/

# Linting
ruff check src/ tests/
```

### Building and Validating the Package Locally

Follow these steps to build and validate the Python package locally, ensuring it's production-ready.

#### Prerequisites

- Python 3.11+ installed
- `pip` and `venv` available

#### Step 1: Setup Development Environment

```bash
# Clone the repository
git clone git@github.com:getsentry/sentry-seer-types.git
cd sentry-seer-types

# Create and activate virtual environment (optional but recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install package in editable mode with dev dependencies
pip install -e ".[dev]"
```

#### Step 2: Run Quality Checks

Run all quality checks to ensure code meets standards:

```bash
# Linting
ruff check src/ tests/

# Type checking
mypy src/

# Tests with coverage
pytest tests/

# All checks together
ruff check src/ tests/ && mypy src/ && pytest tests/
```

**Expected Results:**
- ✅ Ruff: No linting errors
- ✅ Mypy: No type errors
- ✅ Pytest: 49 tests passing, 97% coverage

#### Step 3: Build the Package

Install build tools and create distribution packages:

```bash
# Install build tool
pip install build

# Build both wheel and source distribution
python -m build
```

**Output:** Two files in `dist/`:
- `sentry_seer_types-VERSION-py3-none-any.whl` (~10KB wheel)
- `sentry_seer_types-VERSION.tar.gz` (~14KB source distribution)

#### Step 4: Validate Package Installation

Test that the built package installs and works correctly:

```bash
# Create a clean test environment
python -m venv test-env
source test-env/bin/activate

# Install the built wheel
pip install dist/sentry_seer_types-*.whl

# Test imports
python -c "from sentry_seer_types import CodeReviewTaskRequest; print('✅ Top-level import works')"
python -c "from sentry_seer_types.codegen import CodeReviewTaskRequest; print('✅ Submodule import works')"

# Test validation
python -c "
from sentry_seer_types import CodeReviewTaskRequest
payload = {
    'request_type': 'pr-review',
    'external_owner_id': '123',
    'data': {
        'repo': {'name': 'test', 'owner': 'owner', 'provider': 'github', 'external_id': '123'},
        'pr_id': 1
    }
}
req = CodeReviewTaskRequest.model_validate(payload)
print(f'✅ Validation works: {req.request_type}')
"

# Cleanup
deactivate
rm -rf test-env
```

**Expected Results:**
- ✅ Top-level import works
- ✅ Submodule import works
- ✅ Validation works: pr-review

#### Complete Validation Script

Run everything in one command:

```bash
# Clean previous builds
rm -rf dist/ build/ src/*.egg-info

# Run quality checks
echo "Running quality checks..." && \
ruff check src/ tests/ && \
mypy src/ && \
pytest tests/ -q && \

# Build package
echo "Building package..." && \
python -m build && \

# Validate installation
echo "Validating installation..." && \
python -m venv test-env && \
source test-env/bin/activate && \
pip install -q dist/*.whl && \
python -c "from sentry_seer_types import CodeReviewTaskRequest; print('✅ Package validated successfully')" && \
deactivate && \
rm -rf test-env && \

echo "✅ All validation steps passed!"
```

## Versioning

This package follows semantic versioning:

- **Major version** - Breaking changes to model structure
- **Minor version** - New optional fields (backward compatible)
- **Patch version** - Bug fixes, documentation

Both Sentry and Seer must use compatible versions of this package.

## License

This project is licensed under the Functional Source License, Version 1.1, Apache 2.0 Future License. See the [LICENSE.md](LICENSE.md) file for details.

The FSL allows you to use, copy, modify, and redistribute the software for any purpose except competing uses. After two years from the release date, the license automatically converts to Apache 2.0.
