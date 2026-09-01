# Implementation Plan Review: Betwixt core mapping layer, integrations, documentation, and delivery

**Iteration 16**

This re-review checks both plans after the deployment-trigger revision, rechecks implementation-review--15.md and the
full earlier finding history, and verifies the requested dependency, documentation, naming, context, example, CI, and
release contracts.


## Source Artifact

```text
/home/dusktreader/src/dusktreader/betwixt/.worktrees/feat/NO-TICKET--build-betwixt/.artifacts/20260812--build-betwixt/implementation-plan.md
```


## Overview

The deployment-trigger revision leaves one release-policy contradiction and one executable docs-trigger gap:

- **Critical**: 1
- **Significant**: 1
- **Trivial**: 0


## Prior Review Resolution

- `implementation-review--15.md` ✓: It contained no new findings. Its carried resolutions remain present, including the
  required structure and command inventory, 15-construct and overlap contracts, staged `Betwixt` exports, optional
  dependency and no-extras boundaries, adapter fixtures and aliases, Zensical configuration, Makefile conventions,
  executable examples and demo smoke paths, CI artifact and release topology, lockfile scope, and full/partial context
  contracts.
- `design-review--06.md` ✓: It was clean; no earlier design finding requires separate resolution. The deployment wording
  added since that review is assessed below.
- `implementation-review--14.md`: This artifact remains absent, as recorded by implementation-review--15.md; its
  findings
  cannot be independently rechecked beyond that review's summary.


## Findings

### Summary

| Finding ID | Title                                                   | Outcome |
| ---------- | ------------------------------------------------------- | ------- |
| C01        | Package publication still permits a manual release path |         |
| S01        | Docs merge-only deployment is not executable            |         |


### Critical

#### C01: Package publication still permits a manual release path

##### Where

Design Plan — Goal line 20, AC30 lines 475–476, and Documentation Architecture line 555; Implementation Plan — Goal
lines
16–22.


##### Issue

Both plans still say package or release publishing may use an “explicit manual approval” or an “explicitly approved
manual
workflow.” This contradicts the revised implementation-plan Task 11 AC04 and Step 5, which correctly require
`deploy.yml`
to have only a pushed `v*.*.*` tag trigger and no manual dispatch. The design plan therefore still authorizes a path
that
the requested contract forbids.


##### Impact

An executor can preserve or add `workflow_dispatch` or another manual publication path while satisfying the older Goal,
AC30, or Delivery wording. Package publication could then occur without the required pushed version tag, even though the
task-level release workflow appears to pass its tag-only check.


##### Suggestion

Remove every manual-publication alternative from both plans. State one consistent contract: package publication occurs
only
from `deploy.yml` after a pushed tag matching `v*.*.*` and successful `quality`, `examples`, `docs`, and `distributions`
gate outputs; the package workflow has no `workflow_dispatch`, branch-push, or other non-tag publication trigger.


##### Outcome

Accepted and applied: package publication is now tag-only, and documentation deployment is defined as a closed merged pull-request path targeting `main` with the documented path filters.

### Significant

#### S01: Docs merge-only deployment is not executable

##### Where

Design Plan — CI/CD Architecture lines 597–603; Implementation Plan — Task 11 AC05 lines 729–732 and Step 5 lines
753–755.


##### Issue

The plans require a push to `main` to “represent a merge,” but they do not define how `docs.yml` determines that
condition.
GitHub `push` branch and path filters can restrict the ref to `main` and the changed files to `docs/source/**` or
`zensical.toml`; they do not distinguish a direct push from a merge push. No event guard, repository policy assumption,
or
workflow-fixture test covers that distinction. A parent-count check would also need an explicit policy for squash and
rebase merges.


##### Impact

An implementation can deploy documentation after a direct docs change pushed to `main`, violating the merge-only
contract,
or can miss valid squash/rebase merges. The plan therefore cannot prove that unrelated branch pushes and non-merge main
pushes do not deploy.


##### Suggestion

Specify the concrete merge-only mechanism and its behavior for merge-commit, squash, and rebase strategies. For example,
use a merged pull-request event or an equivalent guard that requires a merged PR targeting `main`, restricts the changed
paths to `docs/source/**` or `zensical.toml`, and builds the resulting main revision. Add configuration or workflow
tests
for qualifying docs and Zensical merges, unrelated main merges, direct main pushes, feature-branch pushes, and tag
pushes;
assert that only the qualifying merge reaches the docs deployment job and that it publishes only `betwixt-site`.


##### Outcome

Accepted and applied: the plan now specifies the concrete `pull_request` `closed` event, `merged` and base-branch guards, supported merge strategies, and workflow tests for qualifying and excluded events.

## Notes

The optional adapters remain regular development dependencies while package metadata exposes them only through the
`pydantic` and `sqlalchemy` extras. The isolated no-extras command omits development groups and extras, and
installed-extra
selectors exclude `absent_extra`.

The Zensical hierarchy, handler options, source/output paths, and Zensical-only Make targets remain explicit. The
required
Makefile style, sole public `Betwixt` class, direct keyword-only `ctx` contract, positional nested derivations,
executable
examples, twelve-job CI matrix, artifact retention, and package/site separation show no regression. The
implementation-plan
Markdown check reports only the intentional level-five task technical-note heading required by its artifact definition.
