# Implementation Plan Review: Betwixt core mapping layer, integrations, documentation, and delivery

This re-review checks the updated implementation plan against implementation-review--11.md, the approved design plan,
and the requested Zensical, absent-extra, package, adapter, example, CI, lockfile, and context contracts.

**Iteration 12**


## Source Artifact

```text
/home/dusktreader/src/dusktreader/betwixt/.worktrees/feat/NO-TICKET--build-betwixt/.artifacts/20260812--build-betwixt/implementation-plan.md
```


## Overview

The revision fixes the Zensical hierarchy, theme variant, source/output paths, serve address, and Zensical-only
commands. It also registers `absent_extra` and states the intended selector exclusions. The exact command table still
omits those exclusions, and the mkdocstrings handler options remain unnamed.

- **Critical**: 2
- **Significant**: 0
- **Trivial**: 0


## Prior Review Resolution

- **C01** ⚠: The plan now specifies `[project]`, `[project.theme] variant = "classic"`, the Python handler path,
  `docs_dir`, `site_dir`, `dev_addr`, and `zensical build --clean`/`zensical serve`. It still refers only to “the
  required
  handler options” without naming their keys or values.
- **C02** ⚠: The plan now registers `absent_extra`, marks the absent modules, and states that installed-extra selectors
  exclude it. The Project Commands and exact CI command table still use selectors that collect those modules.
- **T01** ✓: The two reported task-step prose lines are wrapped within the 120-character limit without weakening the
  context requirements.
- **Earlier contracts** ✓: The Pydantic dependency remains only in the optional `pydantic` extra and is absent from the
  base requirements. The Betwixt public surface, dataclass behavior, construct and overlap rules, full/partial
  semantics, SQLAlchemy canonical-name and unloaded-relationship boundaries, native construction, examples, demo
  paths, CI and release gates, lockfile update, and full/partial context-call contracts remain present.


## Findings

### Summary

| Finding ID | Title                                              | Outcome |
| ---------- | -------------------------------------------------- | ------- |
| C01        | mkdocstrings handler options remain unspecified    |         |
| C02        | Exact variant selectors still collect absent tests |         |


### Critical

#### C01: mkdocstrings handler options remain unspecified

##### Where

Execution — Task 10 — AC01 and Step 2, approximately lines 635–663.


##### Issue

The revision fixes the required Zensical table hierarchy and values: `[project]`, `[project.theme]` with
`variant = "classic"`, `[project.plugins.mkdocstrings.handlers.python]`, `paths = ["src"]`, `docs_dir`, `site_dir`,
and `dev_addr`. However, Step 2 says only “the required handler options.” That is not an executable configuration
contract. The existing documentation configuration names `heading_level`, `show_root_heading`,
`separate_signature`, `show_signature_annotations`, `show_source`, and `docstring_style`, but the plan does not say
which of those options the Zensical configuration must preserve or what values they take.


##### Impact

An executor can omit or change API rendering options while satisfying the written plan. The generated API page can then
have different heading, signature, source-display, or docstring behavior, and the docs smoke test does not prove the
required handler configuration.


##### Suggestion

Name the complete TOML configuration under `[project.plugins.mkdocstrings.handlers.python]`, including
`paths = ["src"]` and an `options` table with `heading_level = 3`, `show_root_heading = true`,
`separate_signature = true`, `show_signature_annotations = true`, `show_source = false`, and
`docstring_style = "google"`. Add configuration assertions for each key and value, while retaining the `::: betwixt`
directive and the generated-page smoke test.


##### Outcome


#### C02: Exact variant selectors still collect absent tests

##### Where

Project Commands — the Pydantic, SQLAlchemy, and combined variant commands, approximately lines 95–131; Execution —
Task 07 selector rules, approximately lines 531–539; Technical Notes — exact CI and final-verification command table,
approximately lines 803–820.


##### Issue

The prose rule now says that `absent_extra` is excluded from installed-extra jobs, but the executable commands do not
implement that rule. The Pydantic selector is `not optional_sqlalchemy`, the SQLAlchemy selector is
`not optional_pydantic`, and the combined selector has no marker expression. The same omissions appear in every
corresponding row of the twelve-job command table. Only the base selector collects the absent-extra modules as required.


##### Impact

Pydantic, SQLAlchemy, and combined jobs still run missing-dependency subprocess tests in environments where one or both
target packages are installed. Those tests can pass for the wrong reason or fail contradictorily, so the matrix does not
prove a base-only absent-extra boundary.


##### Suggestion

Update every installed-extra command and matching CI table row to exclude `absent_extra`: use
`-m "not optional_sqlalchemy and not absent_extra"` for Pydantic, `-m "not optional_pydantic and not absent_extra"`
for SQLAlchemy, and `-m "not absent_extra"` for combined. Keep the base selector as the only selector that collects
both absent-extra modules, and require the same expressions in Task 11 and Task 12.


##### Outcome


## Notes

The Markdown checker reports only the required level-five `##### Declaration representation` heading at line 288 of the
implementation plan. That is an intentional exception required by the implementation-plan artifact definition, not a
new T01 finding.

The remaining Betwixt, SQLAlchemy, examples, demo, CI, release, lockfile, and context contracts show no regression in
this revision. The Pydantic adapter remains optional, and its alias, canonical-name, native-default, coercion, and
missing-extra boundaries remain explicit. The twelve-job matrix, artifact retention, guarded publishing, executable
examples, non-interactive demo paths, SQLAlchemy loaded-state checks, and direct-versus-derived context call forms all
remain covered. C01 and C02 must be resolved before the plan is executable without interpretation.
