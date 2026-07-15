---
status: Accepted
date: 2026-06-27
tags: [typing, generics, api-design, developer-experience, registry-keys]
summary: Default the registry key TypeVar to str, not Hashable (which stays available as an opt-in), prioritising developer experience over maximal type permissiveness.
---

# 002: Default the Registry Key Type to `str`

## Context

Registry keys have always been typed `typing.Hashable`. Issue #100 introduces a
generic key type parameter `K` (`bound=Hashable`) so callers can declare their
key type instead of casting to satisfy type checkers. `K` parametrises the
*public* key — the values passed to `get`/`__getitem__`/`register` and returned
by `keys()`/iteration; the internal lookup key produced by `gen_lookup_key` stays
`Hashable` and is deliberately not parametrised, because that hook may change the
key's type (e.g. case-folding, or wrapping in a tuple).

A type parameter with a default needs a chosen default, and that default is what
bare subscription resolves to. `ClassRegistry[Foo]` already binds the *value* type
`T`, and PEP 696 requires a defaulted type parameter to follow non-defaulted ones,
so `K` is necessarily the second argument — bare subscription keeps meaning
`T=Foo` with `K` defaulted, which is what preserves back-compat.

In practice, registry keys are almost always `str`. Under the `Hashable` typing,
the friction is on output: `keys()` and iteration return `Iterable[Hashable]`, so
callers who want `str` back must cast (passing a `str` *in* already type-checks,
since `str` is `Hashable`). The default chosen here also sets a precedent for how
this library weighs ergonomics against maximal permissiveness in its typing.

Concretely, the friction is on output. Under the historical `Hashable` typing:

```python
registry: ClassRegistry[Pokemon, Hashable] = ClassRegistry("element")
key = next(iter(registry.keys()))   # inferred type: Hashable
name: str = str(key)                # explicit cast required
```

With `str` as the default key type, the common case needs no cast:

```python
registry: ClassRegistry[Pokemon] = ClassRegistry("element")
name: str = next(iter(registry.keys()))   # inferred type: str
```

## Options

### Option 1: Do nothing — default `K` to `Hashable`

Keep the historical key type as the default.

**Pros:** Fully backwards-compatible for type checkers; maximally permissive, so
any hashable key type-checks.
**Cons:** The common case (str keys) still needs an output cast unless the caller
opts in with `ClassRegistry[Foo, str]`; the friction issue #100 set out to remove
remains by default.
**Risks:** Callers keep adding `str(...)`/casts or never discover the opt-in, so
the feature underdelivers.

### Option 2: Default `K` to `str` (Accepted)

Resolve bare subscription to `str` keys; non-str callers opt in explicitly.

**Pros:** The overwhelmingly common case needs no annotation and no coercion.
**Cons:** A type-checker-visible narrowing — existing code using non-str keys
under bare `ClassRegistry[Foo]` now type-errors until annotated.
**Risks:** Surprising type errors for a minority of existing callers on upgrade.

### Option 3: Require an explicit key type (no default)

Give `K` no default, forcing every subscription to name a key type.

**Pros:** No implicit behaviour; every key type is a conscious choice.
**Cons:** Verbose — every `ClassRegistry[Foo]` becomes `ClassRegistry[Foo, str]`,
breaking all existing single-argument subscriptions and defeating the ergonomic
goal.
**Risks:** Widespread breakage and boilerplate; poor adoption.

## Decision

Default `K` to `str`. Keys are `str` in the overwhelming majority of real usage,
so the ergonomic default serves the most code with the least ceremony — exactly
issue #100's intent. The codebase already leans on this assumption (the sorter
notes keys are "in the vast majority of cases" `str`), so `str` codifies the
de-facto contract. `str` satisfies the `bound=Hashable`, and non-str callers opt
in explicitly with `ClassRegistry[Foo, Hashable]` (or a concrete key type).

The cost over Option 1 is a type-checker-visible narrowing for the minority using
non-str keys without annotation; we accept it because runtime behaviour is
unchanged and the fix is a one-line annotation. Option 3's conscious-choice
benefit is not worth breaking every existing subscription. We accept that this
prioritises developer experience over maximal type permissiveness, and adopt that
as the guiding precedent for typing decisions in this library.

## Consequences

- `ClassRegistry[Foo]` resolves keys to `str`; non-str keys require an explicit
  `K`, e.g. `ClassRegistry[Foo, Hashable]`.
- The benefit only materialises once the key-facing method signatures
  (`get`/`__getitem__`/`register`/`unregister`/`keys`/`__iter__`/`__contains__`)
  are retyped from `Hashable` to `K`; that retyping is part of the #100 work.
- Only code that *both* subscripts a registry *and* uses non-str keys is affected.
  Callers that never subscript (`ClassRegistry()` — the common runtime style) see
  no change, and runtime behaviour is unchanged everywhere (the sole runtime touch
  is the `typing_extensions` import on 3.12, covered by ADR 001). Flag the
  type-only break in the release notes.
- The type-checker-visible narrowing (shared by Options 2 and 3) is mitigated
  by shipping this change in a new **major version** (targeted 6.0.0): the
  narrowing and its one-line fix are called out in the release notes and in the
  migration note in `docs/iterating_over_registries.rst`.
- `K` is invariant — it appears in both input (`get(key: K)`) and output
  (`keys() -> Iterable[K]`) positions. So `ClassRegistry[Foo]` (`K=str`) is *not*
  assignable to `ClassRegistry[Foo, Hashable]`; helpers typed against the
  permissive form must accept the relevant key type (or use `Any`).
- `EntryPointClassRegistry` keys are always entry-point names (`str`), so it
  should pin `K=str` rather than expose a free key type; other subclasses
  (`SortedClassRegistry`) inherit `K` unchanged.
- Sets the precedent: favour the ergonomic common case over maximal
  permissiveness when choosing typing defaults, and document the escape hatch.
