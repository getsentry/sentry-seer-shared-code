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

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests with coverage
pytest

# Type checking
mypy src tests

# Linting and formatting
ruff check .
ruff format .
```

## Versioning

This package follows semantic versioning:

- **Major version** - Breaking changes to model structure
- **Minor version** - New optional fields (backward compatible)
- **Patch version** - Bug fixes, documentation

Both Sentry and Seer must use compatible versions of this package.
