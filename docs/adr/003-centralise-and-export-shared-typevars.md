---
status: Accepted
date: 2026-07-15
scope: [src/class_registry/]
summary: Define the shared value and key TypeVars once in base.py as exported ValueType/KeyType, not as per-module T/K redefinitions.
---

# 003: Centralise and Export Shared TypeVars

## Context

Issue #100 introduced generic `T` (value type) and `K` (key type) TypeVars.
`base.py` is already their de-facto home: `registry.py` imports both from it,
and `entry_points.py` imports `T` while pinning its key type positionally as
ADR 002 prescribes. `cache.py` and `patcher.py` are the holdouts, each still
redefining their own `T = typing.TypeVar("T")`. Review of PR #101 flagged the
drift this invites: nothing stops a redefined `T` from diverging in bound or
default from `base.py`'s, and a bare `K` gives callers reading a signature like
`ClassRegistry[Foo, K]` no clue what the parameter means without opening
`base.py`.

`K`'s role — the public key type, distinct from the internal lookup key
produced by `gen_lookup_key` — is established in ADR 002. That distinction is
easy to lose when the type parameter carrying it is a single unexported
letter.

## Options

### Option 1: Do nothing — per-module `T`, terse unexported `K`

Keep redefining `T` in each module that needs it, and leave `K` as-is.

**Pros:** No change required.
**Cons:** Redefinitions can drift (different bound or default per module);
`K` is not in `base.__all__`, so autodoc gives it no documented entry of its
own and no resolvable cross-reference target — it renders in signatures as a
bare letter pointing nowhere — and depending on it is unsupported, leaving
downstream code that wants to name the key type in its own signatures no
supported way to do so short of defining its own equivalent TypeVar.
**Risks:** A future edit updates `base.T`'s bound or default and misses the
copies in `cache.py`/`patcher.py`, silently reintroducing inconsistent
generics.

### Option 2: Define once in `base.py`, export as `ValueType`/`KeyType` (Accepted)

Move both TypeVars to `base.py`, rename to self-documenting names, add them to
`base.__all__`, and have every other module import rather than redefine them.

**Pros:** Single source of truth for bound/default; descriptive names read as
documentation in signatures such as `ClassRegistry[ValueType, KeyType]`;
becomes public, named, and supported for downstream code that wants to reuse
the same TypeVars, rather than merely importable as an unsupported
implementation detail.
**Cons:** Touches every module that defines or imports `T`/`K`.
**Risks:** Anyone already importing `base.T`/`base.K` by name, rather than
subscripting, breaks on the rename — and we treat that as unsupported, since
neither is in `base.__all__` today.

### Option 3: Extract a dedicated `_typevars.py` module

Define `ValueType`/`KeyType` in a new private module imported by `base.py`
and siblings alike.

**Pros:** Decouples the TypeVar definitions from `base.py`'s other contents.
**Cons:** Two symbols do not justify a new module; `base.py` already owns the
base abstractions these TypeVars parametrise, so it is their natural home; an
extra import hop buys no discoverability gain over Option 2.
**Risks:** Same by-name import break as Option 2, since this option renames
`T`/`K` too.

## Decision

Option 2. `ValueType` and `KeyType` are defined once in `base.py`, exported
via `base.__all__`, and imported — never redefined — by every other module.
Unlike Option 1, this removes the possibility of the copies drifting, since
there is only one definition to edit; unlike Option 3, `base.py` already hosts
the abstractions (`BaseRegistry`, `BaseMutableRegistry`) these TypeVars
parametrise, so it is their natural home rather than a new module. `KeyType`
keeps `K`'s existing `bound=Hashable, default=str` from ADR 002 — this ADR
renames and centralises, it does not revisit that bound or default.

## Consequences

- Renaming `T`→`ValueType` and `K`→`KeyType` is a source-level rename only:
  TypeVars are matched positionally in subscription, so call sites like
  `ClassRegistry[Foo, int]` are unaffected. `base.T`/`base.K` are not in
  `base.__all__` today, but nothing stops downstream code importing them by
  name, and any code that does breaks on the rename; this is called out here
  since `__all__` never gated it.
- `ValueType` and `KeyType` become public API — autodoc gives each a documented
  entry of its own that signatures can cross-reference, and they are supported
  imports from `class_registry.base` — so future changes to their bound or
  default are a compatibility-sensitive edit, not a private refactor.
- Establishes the precedent: a TypeVar shared across modules is defined once,
  in the module that owns the base abstraction it parametrises, and imported
  everywhere else — not redefined per module. `base.py`'s `D` (the decorator
  TypeVar for `BaseMutableRegistry.register`) is unrelated in purpose and out
  of scope here.
- The rename itself (updating `cache.py`, `patcher.py`, `registry.py`, and any
  other importers) is implementation work for a follow-up task, not this ADR.
