# Betwixt features tone

This journal records the documentation-only rewrite of the Betwixt features guide.


## Intent

Make `docs/source/features.md` friendlier and easier to scan for readers learning Betwixt, without changing code
examples or technical behavior.


## Changes

- Reworked feature introductions and headings around the practical problem each feature solves.
- Replaced dense or jargon-heavy explanations with conversational technical prose.
- Clarified partial reductions, directional versus pairwise mappings, context handling, and diagnostic remedies.
- Replaced imperative headings and instructions with descriptive or conversational wording.
- Preserved feature order, code blocks, API names, semantics, caveats, and error names.


## Verification

- Formatted `features.md` and this journal with `markdown_format`.
- `uv run --no-sync --python 3.14 pytest -o addopts="" tests/integration/test_docs.py` passed: 4 tests after the final
  prose changes.
- `uv run --no-sync --python 3.14 zensical build --config-file docs/zensical.toml --clean` passed.
- `git diff --check` passed, and a comparison confirmed all 28 code blocks remain unchanged.


## Limitations

No Python or shell behavior was changed. This change does not add new documentation examples or alter the documented
API.
