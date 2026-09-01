# Implementation Plan Review: Betwixt core mapping layer, integrations, documentation, and delivery

This re-review checks the implementation plan against implementation-review--09.md, the approved design plan, and the
requested Pydantic package boundary, dependency variants, native adapters, commands, documentation, naming, and context
contracts.

**Iteration 10**


## Source Artifact

```text
/home/dusktreader/src/dusktreader/betwixt/.worktrees/feat/NO-TICKET--build-betwixt/.artifacts/20260812--build-betwixt/implementation-plan.md
```


## Overview

The review found no Critical or Trivial findings and identified three Significant findings:

- **Critical**: 0
- **Significant**: 3
- **Trivial**: 0


## Prior Review Resolution

- `implementation-review--09.md` was clean and introduced no finding requiring resolution.
- `implementation-review--08.md` S01 ✓: Task 06 still requires `derive(outer_context)` with exactly one positional
  argument, no `ctx=...` injection, both directions, selector variants, reuse, and per-boundary call counts.
- `implementation-review--07.md` S01 ✓: Task 04 still covers declaration-time validation for map, reduce, project, and
  nested inner callables in both directions, accepts only a final keyword-only `ctx`, injects it as `ctx=...`, and
  rejects both positional forms.
- `implementation-review--07.md` S02 ✓: Tasks 05 and 06 still require the exact positional derivation call, positional-
  only selectors, omitted and explicit-`None` derivations, identity derivation, both directions, reuse, and call counts.
- `implementation-review--06.md` S03 ✓: Partial operations still accept context, use `ctx=...` only for direct
  context-aware producers, and cover nested derivation reuse and boundary counts.
- `implementation-review--04.md` S01-S03 ✓: The independent nested pairwise contract, projection failure ownership,
  and sole `Betwixt` class/module ownership remain explicit.
- `implementation-review--01.md` C01-C02, S01-S04, S06-S12, and T01-T02 ✓: The required heading hierarchy exception,
  command inventory, construct and overlap rules, staged exports, variant command table, demo smoke, adapter fixtures,
  alias matrix, documentation inventory, CI and release gates, lockfile scope, resolved unknowns, task-level checks, and
  package metadata distinction remain present.
- `implementation-review--01.md` S05 ⚠: Marker names, import-safe collection, and four selectors remain documented, but
  the selectors still collect absent-extra modules in environments where their target optional packages are installed.
  The residual contradiction is detailed as S02 below.


## Findings

### Summary

| Finding ID | Title                                                       | Outcome |
| ---------- | ----------------------------------------------------------- | ------- |
| S01        | Zensical configuration and serve instructions are invalid   |         |
| S02        | Absent-extra tests run in variants with the extra installed |         |
| S03        | Public operation context is not required to be keyword-only |         |


### Significant

#### S01: Zensical configuration and serve instructions are invalid

##### Where

Execution — Task 10 — AC01 and Steps 2–3, approximately lines 627–656; Project Commands — Serve the documentation,
approximately lines 147–157.


##### Issue

The plan tells the executor to write `theme = "material"` and `plugins = ["mkdocstrings"]` into `zensical.toml`, but
Zensical 0.0.13 uses the `[project]` scope, selects the Material-compatible appearance with
`[project.theme]` and `variant = "classic"`, and configures the Python handler under
`[project.plugins.mkdocstrings.handlers.python]`. The plan also expects `http://localhost:10000` while instructing the
executor to run only `zensical serve`; without `dev_addr`, Zensical serves at its default address of `localhost:8000`.


##### Impact

The generated configuration may fail validation or omit the API plugin, so `make docs/build` cannot reliably produce the
required API page. `make docs/serve` also does not provide the documented endpoint, making the documented local workflow
non-reproducible.


##### Suggestion

Specify the valid TOML structure and the address explicitly. Require `[project]` settings for `site_name`, `docs_dir =
"docs/source"`, `site_dir = "docs/site"`, `dev_addr = "localhost:10000"`, and `nav`; require
`[project.theme] variant = "classic"`; and configure the Python handler under
`[project.plugins.mkdocstrings.handlers.python]` with `paths = ["src"]` and the required options. Keep
`zensical build --clean` and `zensical serve` as the Make recipes after those settings are defined.


##### Outcome

Accepted and applied: the plan now specifies the valid `[project]`, theme, plugin, source/output, and `dev_addr` settings for Zensical and requires the documented build and serve commands to use them.

#### S02: Absent-extra tests run in variants with the extra installed

##### Where

Execution — Task 07 — marker and selector rules, approximately lines 525–531; Task 08 absent-extra tests, approximately
lines 557–573; Exact CI and final-verification command table, approximately lines 793–810.


##### Issue

The plan says the base selector collects both `test_pydantic_absent.py` and `test_sqlalchemy_absent.py`, while the
Pydantic selector excludes only `optional_sqlalchemy`, the SQLAlchemy selector excludes only `optional_pydantic`, and
the
combined selector collects all tests. Therefore each absent-extra module is also collected in variants where its package
is installed. The prescribed `subprocess.run([sys.executable, "-c", ...])` inherits that installed environment and does
not make the dependency absent. The plan supplies no isolation or skip rule to resolve this.


##### Impact

The Pydantic and SQLAlchemy variants can fail their own absent-dependency tests, or those tests can skip and leave the
base package-install boundary unverified. The twelve-job matrix then does not coherently prove the four dependency
variants or the missing-optional-dependency behavior required by the native adapters.


##### Suggestion

Make absent-extra checks base-only, or run each in a genuinely isolated environment that lacks the target distribution.
For the base-only approach, register an `absent_extra` marker, include it in the base command, exclude it from the
Pydantic, SQLAlchemy, and combined selectors, and update the command table and Task 07/08 steps accordingly. Keep the
child-process assertion that core import succeeds and the target adapter declaration raises the actionable missing-extra
error.


##### Outcome

Accepted and applied: absent-extra tests are now explicitly base-only, while Pydantic, SQLAlchemy, and combined selectors exclude them and retain the isolated subprocess checks.

#### S03: Public operation context is not required to be keyword-only

##### Where

Design Plan — AC01, approximately lines 27–31; Execution — Task 04 — AC01, approximately lines 371–375, and Task 06 —
AC06, approximately lines 464–468.


##### Issue

The plan precisely requires the final callable parameter `ctx` to be keyword-only, but it only says that the public
`rightward`, `leftward`, `rightward_partial`, and `leftward_partial` methods accept `context`. It never requires the
operation signatures to reject positional context. An implementation can therefore satisfy the stated callable tests
while exposing a public API that accepts `rightward(value, context)` contrary to the approved
`rightward(value, *, context=None, defaults=None)` contract.


##### Impact

Callers can use an API shape that differs from the approved public contract, and full and partial operations can expose
different positional-binding behavior. The keyword-only context guarantee is consequently enforced for inner callables
but not at the operation boundary.


##### Suggestion

Add signature acceptance criteria and tests for `rightward(value, *, context=None, defaults=None)` and
`leftward(value, *, context=None, defaults=None)`. Require partial-operation `context` to be keyword-only as well, and
assert that positional `context` (and positional `defaults` on full operations) raises `TypeError`. Keep the existing
final keyword-only `ctx` tests separate from this public-operation signature matrix.


##### Outcome

Accepted and applied: full and partial public operations now require keyword-only `context` and `defaults` where applicable, and positional arguments are covered by `TypeError` tests.

## Notes

Task 07 AC01 explicitly places `pydantic>=2.7,<3` only in the optional `pydantic` extra and keeps it out of the base
package's required dependencies. The base commands omit that extra, while the Pydantic and combined commands request it;
the package-build expectation distinguishes the three optional extras from the four adapter variants. Native Pydantic
alias, validation, default, and coercion behavior and the native SQLAlchemy loaded-state, canonical-name, and
no-persistence boundaries remain aligned with the approved design.

The plan still names the sole public class `Betwixt` in `src/betwixt/betwixt.py` and contains no public `Twixt` or
`twixt`
symbol. Direct context-aware callables and nested derivations also retain the required distinction: final keyword-only
`ctx` with `ctx=...` for the former, and exactly one positional `derive(outer_context)` call for the latter.

The Markdown checker reports the required level-five task technical-note heading at line 288 of the implementation plan.
That is an intentional exception required by the implementation-plan artifact definition. The finding-field headings in
this review likewise use level five because the implementation-review artifact definition requires them.
