# Makefile for sentry-seer-types — mirrors CI so you can run the same steps locally.
#
# Usage:
#   make install-pydantic-v1    # Install with Pydantic v1 (same as CI v1 job)
#   make install-pydantic-v2    # Install with Pydantic v2 (same as CI v2 job)
#   make install                # Install with default deps (no Pydantic override)
#   make lint typecheck test    # Run lint, typecheck, tests
#   make build validate-install # Build wheel and validate install (set PYDANTIC_SPEC for venv)

PYDANTIC_SPEC ?=

.PHONY: install install-pydantic-v1 install-pydantic-v2 lint typecheck test build validate-install

install:
	python -m pip install --upgrade pip
ifdef PYDANTIC_SPEC
	pip install "$(PYDANTIC_SPEC)"
endif
	pip install -e ".[dev]"

install-pydantic-v1:
	$(MAKE) install PYDANTIC_SPEC="pydantic>=1.10.23,<2"

install-pydantic-v2:
	$(MAKE) install PYDANTIC_SPEC="pydantic>=2.6.4"

lint:
	ruff check src/ tests/

typecheck:
	mypy src/

test:
	pytest tests/

build:
	pip install build
	python -m build

# Validates that the built wheel (or editable install) can be installed and imports work.
# Set PYDANTIC_SPEC when calling from CI, e.g. make validate-install PYDANTIC_SPEC="pydantic>=1.10.23,<2"
validate-install:
	@python -m venv test-env && \
	. test-env/bin/activate && \
	(\
	  if [ -d "dist" ] && [ -n "$$(ls dist/*.whl 2>/dev/null)" ]; then \
	    [ -n "$(PYDANTIC_SPEC)" ] && pip install "$(PYDANTIC_SPEC)"; \
	    pip install dist/*.whl; \
	  else \
	    [ -n "$(PYDANTIC_SPEC)" ] && pip install "$(PYDANTIC_SPEC)"; \
	    pip install -e .; \
	  fi && \
	  python -c "from sentry_seer_shared_code import SeerCodeReviewTaskRequestForPrReview; print('✅ Default import successful')" && \
	  python -c "from sentry_seer_shared_code.v1 import SeerCodeReviewTaskRequestForPrReview; print('✅ v1 import successful')" && \
	  python -c "import sentry_seer_shared_code.v2; print('✅ v2 import successful')" \
	); \
	status=$$?; \
	deactivate 2>/dev/null; \
	rm -rf test-env; \
	exit $$status
