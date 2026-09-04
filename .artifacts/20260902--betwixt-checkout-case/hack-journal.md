# Checkout case study

This journal records the documentation and executable example added for the checkout translation case.


## Overview

The change documents a coherent Pydantic API to SQLAlchemy checkout mapping using nested lines, aliases, runtime money
context, name expansion, and a persisted total.


## Intent

Show how Pydantic owns API validation and aliases, SQLAlchemy owns storage and relationships, and Betwixt owns the
translation between those boundaries without requiring a database session.


## Changes

- Added `examples/checkout.py` as the executable source example.
- Added `docs/source/cases/checkout.md` and linked it from the cases navigation and index.
- Added the checkout page to the documentation integration page list and examples teaching arc.
- Require recipient names to contain at least two non-whitespace tokens.
- Recalculate and validate the declared API total against every order line before persisting cents.
- Added `tests/optional/test_checkout_case.py` to execute the example and cover both invariants.


## Verification

- `uv run --no-sync --python 3.14 python -c "import runpy; runpy.run_path('examples/checkout.py')"`
- `uv run --no-sync --python 3.14 pytest -o addopts="" tests/optional/test_checkout_case.py`
- `uv run --no-sync --python 3.14 pytest -o addopts="" tests/integration/test_docs.py`
- `uv run --no-sync --python 3.14 zensical build --config-file docs/zensical.toml --clean`
- `git diff --check`


## Limitations

The example constructs SQLAlchemy objects in memory and does not exercise a database engine, session, or query eager
loading. A production query must eager-load the relationship before translation.
