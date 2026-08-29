---
status: Accepted
date: 2026-06-27
scope: [pyproject.toml, .github/workflows/build.yml, src/class_registry/base.py]
summary: Support the three most recent Python minor releases, backporting newer typing features via typing_extensions rather than dropping the oldest early.
---

# 001: Support the Three Most Recent Python Minor Releases

## Context

The library supports Python 3.12, 3.13, and 3.14 (`requires-python = ">=3.12"`;
tox runs py312/py313/py314). No written policy states how many releases we
commit to, or what to do when a desired feature postdates the oldest one.

Issue #100 (an optional generic key type) needs PEP 696 `TypeVar` defaults.
These are native to `typing` in 3.13+ but absent from 3.12's standard library,
which forces a choice between shipping the feature and keeping 3.12. Python 3.15
is slated for October 2026; once it lands, 3.12 falls outside a "three most
recent" window regardless.

## Options

### Option 1: Do nothing

Adopt only language and stdlib features available in the oldest supported
release.

**Pros:** No extra dependencies; simplest mental model.
**Cons:** Blocks otherwise-ready features behind a version drop; couples feature
timing to version-drop timing.
**Risks:** Contributors relitigate "can we use X yet?" for every feature gated
on a newer stdlib.

### Option 2: Support the three most recent releases, backport via `typing_extensions` (Accepted)

Commit to the three most recent Python minor releases, and backport newer typing
features through `typing_extensions` (gated on `python_version < '3.13'`) until
the oldest supported release ages out of that window.

**Pros:** Features land immediately; explicit, predictable support window;
`typing_extensions` is the canonical backport channel maintained by the typing
team.
**Cons:** A conditional runtime dependency plus version-gated import branches to
maintain.
**Risks:** Forgetting to remove the shim when a version is dropped.

### Option 3: Drop Python 3.12 now

Drop 3.12 immediately and use the stdlib-native features.

**Pros:** No backport dependency or conditional imports.
**Cons:** Retires a still-supported, widely-used release roughly four months
before 3.15 would retire it anyway.
**Risks:** Premature breakage for downstream users still on 3.12.

## Decision

Adopt a standing policy of supporting the three most recent Python minor
releases (today: 3.12, 3.13, 3.14), and use `typing_extensions` to backport
typing features that are only native in releases newer than the oldest we
support.

This unblocks issue #100 without dropping 3.12 prematurely. `typing_extensions`
is purpose-built for exactly this gap, so the cost is a single conditional
dependency plus a localised import shim — removed when 3.12 is dropped, expected
shortly after Python 3.15's October 2026 release. The shim's removal is bounded
and predictable, which the "do nothing" and "drop 3.12 now" options trade away
for either blocked features or premature breakage.

This is the library's first runtime dependency: `pyproject.toml` currently has no
`[project.dependencies]` table, and `typing_extensions` is otherwise present only
transitively via dev tooling. The footprint stays conditional — it installs only
on 3.12 — which keeps the zero-to-one cost proportionate to the benefit.

## Consequences

- A runtime dependency `typing_extensions>=4.6 ; python_version < '3.13'`. The
  `default=` parameter first appeared in 4.4; the `>=4.6` floor is chosen so PEP
  696 `TypeVar` defaults track the finalised spec.
- The packaging marker (`python_version < '3.13'`, in `pyproject.toml`) and the
  runtime import guard are distinct mechanisms: the latter branches on
  `sys.version_info >= (3, 13)` in code, not on the environment marker.
- Newer typing constructs are imported through a single version-gated shim, so
  the removal site is obvious. tox already runs mypy and pytest on py312/py313/
  py314, exercising both branches and guarding against a stale shim.
- When 3.12 is dropped (after Python 3.15 ships), the `rotate-python-versions`
  workflow must also remove the `typing_extensions` gate and the shim.
- The support window is intentionally tighter than CPython's upstream EOL (3.12
  receives upstream security fixes into 2028): "three most recent" is a
  deliberate maintenance-scope choice, not EOL tracking.
- Establishes the precedent: a typing feature newer than our oldest supported
  release is backported via `typing_extensions`, not a reason to drop a version
  early.
