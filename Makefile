PACKAGE_TARGET:=src/betwixt
UV_PROJECT_ENVIRONMENT?=$(CURDIR)/.venv
export UV_PROJECT_ENVIRONMENT
UV_RUN:=uv run
NO_EXTRAS_TESTS:=tests/integration/test_no_extras.py tests/unit
NO_EXTRAS_COVERAGE:=--cov=betwixt.annotations --cov=betwixt.adapters.base --cov=betwixt.adapters.dataclass --cov=betwixt.adapters.registry --cov=betwixt.adapters.typeddict --cov=betwixt.betwixt --cov=betwixt.compiler --cov=betwixt.constants --cov=betwixt.constructs --cov=betwixt.errors --cov=betwixt.refs --cov=betwixt.types
NO_EXTRAS_PYTEST:=-m pytest -o addopts="" --junitxml=.junit.xml $(NO_EXTRAS_COVERAGE) --cov-report=term-missing --cov-report=xml:.coverage.xml --cov-fail-under=100

default: help


## ==== Quality Control ================================================================================================

qa: qa/full  ## Shortcut for qa/full

qa/test:  ## Run all tests (unit + integration)
	@$(UV_RUN) pytest

qa/test/unit:  ## Run unit tests only
	@$(UV_RUN) pytest --cov-fail-under=0 -m unit tests/unit

qa/test/integration:  ## Run integration tests only
	@$(UV_RUN) pytest --cov-fail-under=0 -m integration tests/integration

qa/test/no-extras:  ## Run the complete dependency-free core gate against the installed package
	@set -euo pipefail; \
	wheel_dir=$$(mktemp -d); \
	build_cache_dir=$$(mktemp -d); \
	venv_dir=$$(mktemp -d); \
	trap 'rm -rf "$$wheel_dir" "$$build_cache_dir" "$$venv_dir"' EXIT; \
	env -u UV_PROJECT_ENVIRONMENT UV_CACHE_DIR="$$build_cache_dir" uv build --clear --wheel --out-dir "$$wheel_dir" >/dev/null; \
	wheel=$$(printf '%s\n' "$$wheel_dir"/*.whl); \
	uv venv "$$venv_dir" >/dev/null; \
	uv pip install --python "$$venv_dir/bin/python" --no-cache --reinstall --no-deps "$$wheel" >/dev/null; \
	uv pip install --python "$$venv_dir/bin/python" --no-cache --reinstall py-buzz pytest pytest-cov >/dev/null; \
	"$$venv_dir/bin/python" $(NO_EXTRAS_PYTEST) $(NO_EXTRAS_TESTS)

qa/types:  ## Run static type checks
	@$(UV_RUN) ty check ${PACKAGE_TARGET} tests src/betwixt_demo

qa/lint:  ## Run linters
	@$(UV_RUN) ruff check ${PACKAGE_TARGET} tests src/betwixt_demo examples
	@$(UV_RUN) typos ${PACKAGE_TARGET} tests src/betwixt_demo docs/source

qa/full: qa/test qa/lint qa/types  ## Run the full set of quality checks
	@echo "All quality checks pass!"

qa/format:  ## Run code formatter
	@$(UV_RUN) ruff check --select I --fix ${PACKAGE_TARGET} tests src/betwixt_demo examples
	@$(UV_RUN) ruff format ${PACKAGE_TARGET} tests src/betwixt_demo examples


## ==== Documentation ==================================================================================================

docs: docs/serve  ## Shortcut for docs/serve

docs/build:  ## Build the documentation
	@$(UV_RUN) zensical build --config-file docs/zensical.toml --clean

docs/serve:  ## Build the docs and start a local dev server
	@$(UV_RUN) zensical serve --config-file docs/zensical.toml



## ==== Demo ===========================================================================================================

demo: demo/run  ## Shortcut for demo/run

demo/run:  ## Run the demo application
	@$(UV_RUN) betwixt-demo

demo/debug:  ## Run the demo application in debug mode
	@$(UV_RUN) debugpy --listen localhost:5678 --wait-for-client betwixt-demo



## ==== Other Commands =================================================================================================

## ==== Helpers ========================================================================================================

hooks:  ## Install/update pre-commit hooks
	@$(UV_RUN) pre-commit install --hook-type=pre-commit --hook-type=pre-push

clean:  ## Clean up build artifacts and other junk
	@rm -rf .venv
	@uv run --isolated --no-project --with pyclean pyclean . --debris
	@rm -rf dist
	@rm -rf .ruff_cache
	@rm -rf .pytest_cache
	@rm -f .coverage*
	@rm -f .junit.xml

help:  ## Show help message
	@awk "$$PRINT_HELP_PREAMBLE" $(MAKEFILE_LIST)


# ..... Make configuration .............................................................................................

.ONESHELL:
SHELL:=/bin/bash
.PHONY: qa qa/test qa/test/unit qa/test/integration qa/test/no-extras qa/types qa/lint qa/full qa/format \
	docs docs/build docs/serve \
	demo demo/run demo/debug \
	hooks clean help


# ..... Color table for pretty printing ................................................................................

RED    := \033[31m
GREEN  := \033[32m
YELLOW := \033[33m
BLUE   := \033[34m
TEAL   := \033[36m
GRAY   := \033[90m
CLEAR  := \033[0m
ITALIC := \033[3m


# ..... Help printer ...................................................................................................

define PRINT_HELP_PREAMBLE
BEGIN {
	print "Usage: $(YELLOW)make <target>$(CLEAR)"
	print
	print "Targets:"
}
/^## =+ .+( =+)?/ {
    s = $$0
    sub(/^## =+ /, "", s)
    sub(/ =+/, "", s)
	printf("\n  %s:\n", s)
}
/^## -+ .+( -+)?/ {
    s = $$0
    sub(/^## -+ /, "", s)
    sub(/ -+/, "", s)
	printf("\n    $(TEAL)> %s$(CLEAR)\n", s)
}
/^[$$()% 0-9a-zA-Z_\/-]+(\\:[$$()% 0-9a-zA-Z_\/-]+)*:.*?##/ {
    t = $$0
    sub(/:.*/, "", t)
    h = $$0
    sub(/.?*##/, "", h)
    printf("    $(YELLOW)%-19s$(CLEAR) $(GRAY)$(ITALIC)%s$(CLEAR)\n", t, h)
}
endef
export PRINT_HELP_PREAMBLE
