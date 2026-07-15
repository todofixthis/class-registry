---
status: Accepted
date: 2026-07-15
tags: [api-design, generics, public-api, registry-keys, typing]
summary: Define the shared value and key TypeVars once in base.py as exported ValueType/KeyType, not as per-module T/K redefinitions.
---

# 003: Centralise and Export Shared TypeVars

## Context

Issue #100 introduced generic `T` (value type) and `K` (key type) TypeVars.
Rather than a single shared definition, `base.py` defines its own `T` and `K`,
while `cache.py` and `patcher.py` each redefine `T = typing.TypeVar("T")`
independently; `registry.py` previously did the same before switching to an
import. Review of PR #101 flagged the drift this invites: nothing stops two
modules' `T`s from diverging in bound or default, and a bare `K` gives callers
reading a signature like `ClassRegistry[Foo, K]` no clue what the parameter
means without opening `base.py`.

`K`'s role — the public key type, distinct from the internal lookup key
produced by `gen_lookup_key` — is established in ADR 002. That distinction is
easy to lose when the type parameter carrying it is a single unexported
letter.

## Options

### Option 1: Do nothing — per-module `T`, terse unexported `K`

Keep redefining `T` in each module that needs it, and leave `K` as-is.

**Pros:** No change required.
**Cons:** Redefinitions can drift (different bound or default per module);
`K` is not importable, so downstream code that wants to name the key type in
its own signatures must define its own equivalent TypeVar.
**Risks:** A future edit updates `base.T`'s bound or default and misses the
copies in `cache.py`/`patcher.py`, silently reintroducing inconsistent
generics.

### Option 2: Define once in `base.py`, export as `ValueType`/`KeyType` (Accepted)

Move both TypeVars to `base.py`, rename to self-documenting names, add them to
`base.__all__`, and have every other module import rather than redefine them.

**Pros:** Single source of truth for bound/default; descriptive names read as
documentation in signatures such as `ClassRegistry[ValueType, KeyType]`;
importable by downstream code that wants to reuse the same TypeVars.
**Cons:** Touches every module that currently defines its own `T`.
**Risks:** None beyond the mechanical rename; TypeVars are matched
positionally in subscription, not by name, so the rename has no runtime or
subscription-site effect.

### Option 3: Extract a dedicated `_typevars.py` module

Define `ValueType`/`KeyType` in a new private module imported by `base.py`
and siblings alike.

**Pros:** Decouples the TypeVar definitions from `base.py`'s other contents.
**Cons:** Two symbols do not justify a new module; `base.py` already owns the
base abstractions these TypeVars parametrise, so it is their natural home.
**Risks:** An extra import hop for no discoverability gain over Option 2.

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
  `base.__all__` today but remain importable by name, so any downstream code
  importing them directly (rather than subscripting) breaks on the rename;
  this is called out here since it isn't otherwise enforced by `__all__`.
- `ValueType` and `KeyType` become public API — they appear in rendered
  signatures and are importable from `class_registry.base` — so future changes
  to their bound or default are a compatibility-sensitive edit, not a private
  refactor.
- Establishes the precedent: a TypeVar shared across modules is defined once,
  in the module that owns the base abstraction it parametrises, and imported
  everywhere else — not redefined per module. `base.py`'s `D` (the decorator
  TypeVar for `AutoRegister`) is unrelated in purpose and out of scope here.
- The rename itself (updating `cache.py`, `patcher.py`, `registry.py`, and any
  other importers) is implementation work for a follow-up task, not this ADR.
