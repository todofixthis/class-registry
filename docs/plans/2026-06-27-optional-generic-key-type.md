# Optional Generic Key Type Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Worktree:** `/Users/phx/Documents/class-registry/.agents/worktrees/issue-100-generic-key-type` (branch: `worktree-issue-100-generic-key-type`)

**Goal:** Add an optional generic key type parameter `K` to the registry hierarchy (GitHub issue #100), defaulting to `str`, so callers stop casting registry keys to satisfy type checkers.

**Architecture:** Introduce a PEP 696 `TypeVar` `K` (`bound=Hashable`, `default=str`) defined once in `base.py` via a version-gated import (`typing` on 3.13+, `typing_extensions` on 3.12). Thread `K` through the *public* key-facing signatures of `BaseRegistry`/`BaseMutableRegistry`/`ClassRegistry`/`SortedClassRegistry`. Internal *lookup* keys (output of `gen_lookup_key`, the `_registry`/`_lookup_keys`/`__missing__`/`_register`/`_unregister` surfaces) stay `Hashable`. `EntryPointClassRegistry` pins `K=str`; `ClassRegistryInstanceCache` and `RegistryPatcher` widen their wrapped-registry type to `Any` rather than threading `K`.

**Tech Stack:** Python 3.12–3.14, `typing_extensions` (runtime, 3.12 only), mypy `--strict`, pytest, hatchling, uv, tox, Sphinx.

## Global Constraints

- Supported Python: 3.12, 3.13, 3.14 — `requires-python = ">=3.12"` unchanged (ADR 001). Do NOT drop 3.12.
- `typing_extensions>=4.6` is a runtime dependency **only** on `python_version < '3.13'` (ADR 001).
- Default key type is `str` (ADR 002). `K` is invariant; `bound=Hashable`.
- `K` parametrises the public key only; lookup keys (`gen_lookup_key` output, internal dicts, `__missing__`, `_register`, `_unregister`) stay `typing.Hashable`.
- Runtime behaviour must be unchanged — this is a typing-only feature. Existing 36 tests must keep passing.
- mypy `--strict` must pass on `src` and `test` (and via autohooks pre-commit) under the running interpreter; tox exercises 3.12/3.13/3.14.
- Conventions: NZ English; "Initialises" not "Initializes"; comments on the line preceding code; Google/Napoleon docstrings ≤80 chars; alphabetised collections.
- Commit with the `creative-commits` skill; commit via `uv run git commit`; `git push` after each commit.

> **Why the source edits are one atomic task:** the `str` default is global the
> moment `base.py` changes — a bare `ClassRegistry[T]` then means `K=str`, so
> every downstream module that passes `Hashable` keys goes red until it too is
> edited. There is no ordering that keeps `mypy src test` green mid-way, so all
> five source modules change together in Task 1; the full type check runs once,
> after they are all done.

---

## File Map

- **Modify** `src/class_registry/base.py` — version-gated `TypeVar` import; define `K`; `BaseRegistry[T, K]`, `BaseMutableRegistry[T, K]` (incl. `register` cast); `AutoRegister` widened. Owns `K`/`T`; exports them for `registry.py`.
- **Modify** `src/class_registry/registry.py` — import `K`, `T` from `base`; `ClassRegistry[T, K]`, `SortedClassRegistry[T, K]`.
- **Modify** `src/class_registry/entry_points.py` — `EntryPointClassRegistry(BaseRegistry[T, str])`; key annotations `str`.
- **Modify** `src/class_registry/cache.py` — wrapped registry typed `ClassRegistry[T, typing.Any]`; keys stay `Hashable`.
- **Modify** `src/class_registry/patcher.py` — wrapped registry typed `BaseMutableRegistry[T, typing.Any]`.
- **Modify** `pyproject.toml` — add `[project.dependencies]` with the gated `typing_extensions`.
- **Create** `test/test_typing.py` — `typing.assert_type` tests (validated by mypy, run harmlessly by pytest).
- **Modify** `test/test_gen_lookup_key.py`, `test/test_sorted_class_registry.py` — convert the `gen_lookup_key` overrides from `@staticmethod` to instance methods.
- **Modify** `docs/iterating_over_registries.rst` — document the optional key type and the removal of `str()` coercion.

---

## Task 1: Implement the generic key type across all registries

Atomic type-level change: dependency, `K`, and every registry/wrapper edited together so the repository ends green. TDD via `typing.assert_type` tests that mypy validates.

**Files:**
- Modify: `pyproject.toml`, `src/class_registry/base.py`, `registry.py`, `entry_points.py`, `cache.py`, `patcher.py`, `test/test_gen_lookup_key.py`, `test/test_sorted_class_registry.py`
- Create: `test/test_typing.py`

**Interfaces (produced):**
- `base.T = TypeVar("T")`; `base.K = TypeVar("K", bound=typing.Hashable, default=str)`.
- `BaseRegistry[T, K]`, `BaseMutableRegistry[T, K]` — public key methods typed `K`; `gen_lookup_key(self, key: K) -> Hashable` (now an instance method) bridges public key → lookup key; lookup-key surfaces (`__missing__(key: Hashable)`, `_register`/`_unregister(key: Hashable)`, `_registry: dict[Hashable, Type[T]]`, `_lookup_keys: dict[K, Hashable]`) stay `Hashable`.
- `ClassRegistry[T, K]`, `SortedClassRegistry[T, K]`.
- `EntryPointClassRegistry(BaseRegistry[T, str])`.
- `ClassRegistryInstanceCache` (still `Mapping[Hashable, T]`) constructor accepts `ClassRegistry[T, typing.Any]`.
- `RegistryPatcher` constructor accepts `BaseMutableRegistry[T, typing.Any]`.

- [ ] **Step 1: Add the gated runtime dependency**

Run (confirm `pwd` is the worktree first):
```bash
uv add "typing_extensions>=4.6,<5; python_version < '3.13'"
```
Expected: a `dependencies` array is added under `[project]` in `pyproject.toml`
containing `"typing_extensions>=4.6,<5 ; python_version < '3.13'"`, and `uv.lock`
updates.

- [ ] **Step 2: Write the failing typing tests**

Create `test/test_typing.py`:
```python
"""Type-level assertions for the optional generic key type (issue #100).

Validated by mypy (which runs over ``test``); ``typing.assert_type`` is a
runtime no-op, so each test also executes harmlessly under pytest. Every test
registers a concrete class so the lookups it asserts on succeed at runtime.
"""

import typing

from class_registry import ClassRegistry
from class_registry.base import BaseMutableRegistry
from class_registry.cache import ClassRegistryInstanceCache
from class_registry.entry_points import EntryPointClassRegistry
from class_registry.patcher import RegistryPatcher
from class_registry.registry import SortedClassRegistry


class Widget:
    pass


def test_class_registry_defaults_keys_to_str() -> None:
    registry: ClassRegistry[Widget] = ClassRegistry()

    @registry.register("custom")
    class Custom(Widget):
        pass

    typing.assert_type(registry["custom"], Widget)
    typing.assert_type(next(iter(registry.keys())), str)
    for key in registry:
        typing.assert_type(key, str)


def test_class_registry_accepts_explicit_key_type() -> None:
    registry: ClassRegistry[Widget, int] = ClassRegistry()

    @registry.register(42)
    class Custom(Widget):
        pass

    typing.assert_type(registry[42], Widget)
    typing.assert_type(next(iter(registry.keys())), int)


def test_sorted_class_registry_defaults_keys_to_str() -> None:
    registry: SortedClassRegistry[Widget] = SortedClassRegistry(sort_key="weight")

    @registry.register("a")
    class A(Widget):
        weight = 1

    typing.assert_type(next(iter(registry.keys())), str)


def test_entry_point_registry_keys_are_str() -> None:
    registry: EntryPointClassRegistry[Widget] = EntryPointClassRegistry("dummy.group")
    typing.assert_type(registry.keys(), typing.Iterable[str])


def test_instance_cache_accepts_non_str_key_registry() -> None:
    registry: ClassRegistry[Widget, int] = ClassRegistry()

    @registry.register(7)
    class Seven(Widget):
        pass

    cache: ClassRegistryInstanceCache[Widget] = ClassRegistryInstanceCache(registry)
    typing.assert_type(cache[7], Widget)


def test_patcher_accepts_non_str_key_registry() -> None:
    registry: ClassRegistry[Widget, int] = ClassRegistry(attr_name="key")
    patcher: RegistryPatcher[Widget] = RegistryPatcher(registry)
    typing.assert_type(patcher.target, BaseMutableRegistry[Widget, typing.Any])
```

- [ ] **Step 3: Run mypy to verify the typing tests fail**

Run: `uv run mypy test/test_typing.py`
Expected: FAIL. Several errors are expected and correct at this point — they land
in `test_typing.py` itself: "too many type arguments" for the 2-arg subscriptions
(`ClassRegistry[Widget, int]`) and `assert_type` mismatches (`Hashable` vs `str`).
Any failure is the red state; the implementation steps below clear them all.

- [ ] **Step 4: Add the version-gated `TypeVar` import and `K`/`T`/`D` to `base.py`**

In `src/class_registry/base.py`, add `import sys` and the gated import, and define
the TypeVars with the imported `TypeVar`:
```python
import sys
import typing
from abc import ABC, abstractmethod as abstract_method
from inspect import isabstract as is_abstract, isclass as is_class
from warnings import warn

# PEP 696 ``TypeVar`` defaults are native to ``typing`` in 3.13+; on 3.12 they
# come from ``typing_extensions`` (see docs/adr/001).
if sys.version_info >= (3, 13):
    from typing import TypeVar
else:
    from typing_extensions import TypeVar
```
Then (leave `RegistryKeyError` where it is) define:
```python
T = TypeVar("T")

# ``K`` parametrises the public/human-readable key. Lookup keys (produced by
# ``gen_lookup_key``) stay ``Hashable`` — see docs/adr/002.
K = TypeVar("K", bound=typing.Hashable, default=str)

# [#53] Fix incorrect return type from ``register``
D = TypeVar("D", bound=typing.Callable[..., typing.Any])
```

- [ ] **Step 5: Thread `K` through `BaseRegistry`**

`class BaseRegistry(typing.Generic[T, K], ABC):` and update these signatures
(public key → `K`; lookup key / `__missing__` stay `Hashable`):
```python
def __contains__(self, key: K) -> bool:
def __getitem__(self, key: K) -> T:
def __iter__(self) -> typing.Iterator[K]:
def __missing__(self, key: typing.Hashable) -> typing.Type[T]:
def get_class(self, key: K) -> typing.Type[T]:            # abstract
def get(self, key: K, *args: typing.Any, **kwargs: typing.Any) -> T:
def keys(self) -> typing.Iterable[K]:                     # abstract

def gen_lookup_key(self, key: K) -> typing.Hashable:
```
Leave `classes()` and `create_instance()` unchanged. Do NOT change `__missing__`
to `K` — `ClassRegistry.get_class` calls it with a lookup key (`Hashable`).

`gen_lookup_key` changes from a `@staticmethod` to an instance method (drop the
`@staticmethod` decorator, add `self`) so its `K` binds to the registry's key
type, uniform with the other key-facing methods. It is always invoked via an
instance, so this is behaviour-preserving; existing `@staticmethod` overrides
remain valid at runtime and under mypy (verified). `create_instance` stays a
`staticmethod` — it does not involve `K`.

- [ ] **Step 6: Thread `K` through `BaseMutableRegistry` (incl. the `register` cast) and `AutoRegister`**

- `class BaseMutableRegistry(BaseRegistry[T, K], ABC):`
- `self._lookup_keys: dict[K, typing.Hashable] = {}`
- `def keys(self) -> typing.Iterable[K]:`
- `def items(self) -> typing.Iterable[tuple[K, typing.Type[T]]]:`
- `register` second overload and impl signature change `typing.Hashable` → `K`
  (leave the bare-decorator overload `def register(self, key: D, /) -> D` as-is):
  ```python
  @typing.overload
  def register(self, key: K) -> typing.Callable[[D], D]: ...

  def register(self, key: typing.Union[D, K]) -> typing.Union[
      D,
      typing.Callable[[D], D],
  ]:
  ```
- In the decorator-factory (`else`) branch, `key` is inferred as `D | K`; cast it
  to `K` once before use, or `gen_lookup_key(key)` and `_lookup_keys[key]` fail
  to type-check:
  ```python
  else:
      # ``@register('some_attr')`` usage:
      def _decorator(cls: D) -> D:
          key_ = typing.cast(K, key)
          lookup_key_ = self.gen_lookup_key(key_)

          self._register(lookup_key_, typing.cast(typing.Type[T], cls))
          self._lookup_keys[key_] = lookup_key_

          return cls

      return _decorator
  ```
  (The `is_class(key)` branch is unchanged — `attr_key` is `Any`.)
- `def unregister(self, key: K) -> typing.Type[T]:`
- Leave `_register(self, key: typing.Hashable, ...)` and
  `_unregister(self, key: typing.Hashable)` as `Hashable`.
- `AutoRegister`: widen the parameter to accept any key type:
  ```python
  def AutoRegister(registry: BaseMutableRegistry[T, typing.Any]) -> type:
  ```

- [ ] **Step 7: Thread `K` through `registry.py`**

- Replace `T = typing.TypeVar("T")` with an alphabetised import from base:
  ```python
  from .base import BaseMutableRegistry, K, RegistryKeyError, T
  ```
- `class ClassRegistry(BaseMutableRegistry[T, K]):`
- `def get_class(self, key: K) -> typing.Type[T]:`
- Leave `self._registry: dict[typing.Hashable, typing.Type[T]]`,
  `_register(self, key: typing.Hashable, ...)`, `_unregister(self, key: typing.Hashable)`
  as `Hashable`.
- `class SortedClassRegistry(ClassRegistry[T, K]):`
- `def keys(self) -> typing.Iterable[K]:`
- In `create_sorter`, type the comparator tuples as
  `typing.Tuple[K, typing.Type[T], typing.Hashable]`:
  ```python
  def sorter(
      a: typing.Tuple[K, typing.Type[T], typing.Hashable],
      b: typing.Tuple[K, typing.Type[T], typing.Hashable],
  ) -> int:
  ```

- [ ] **Step 8: Pin `K=str` in `entry_points.py`**

- `class EntryPointClassRegistry(BaseRegistry[T, str]):`
- `def get(self, key: str, *args: typing.Any, **kwargs: typing.Any) -> T:`
- `def get_class(self, key: str) -> typing.Type[T]:`
- `def keys(self) -> typing.Iterable[str]:`
- `self._cache: typing.Optional[dict[str, typing.Type[T]]] = None`
- `def _get_cache(self) -> dict[str, typing.Type[T]]:`

- [ ] **Step 9: Widen the wrapped-registry type in `cache.py`**

Change every `ClassRegistry[T]` to `ClassRegistry[T, typing.Any]`:
- `def __init__(self, class_registry: ClassRegistry[T, typing.Any], ...) -> None:`
- `self._registry: ClassRegistry[T, typing.Any] = class_registry`
- `def registry(self) -> ClassRegistry[T, typing.Any]:`

Leave the key-facing methods (`__getitem__`, `get_instance_key`, `get_class_key`,
`warm_cache`) typed `typing.Hashable` and the base
`typing.Mapping[typing.Hashable, T]` unchanged (see Intentional Decisions).

- [ ] **Step 10: Widen the wrapped-registry type in `patcher.py`**

- `def __init__(self, registry: BaseMutableRegistry[T, typing.Any], *args: typing.Type[T], **kwargs: typing.Type[T]) -> None:`
- `self.target: BaseMutableRegistry[T, typing.Any] = registry`

Leave `_new_values: dict[str, typing.Type[T]]`, `_prev_values`, and the
`_get_value`/`_set_value`/`_del_value` `Hashable` parameters unchanged.

- [ ] **Step 11: Convert the `gen_lookup_key` test overrides to instance methods**

In `test/test_gen_lookup_key.py` (two overrides) and
`test/test_sorted_class_registry.py` (one override), change each
`@staticmethod`-decorated `gen_lookup_key` override to an instance method: remove
the `@staticmethod` decorator and add `self` as the first parameter, keeping the
`key: typing.Hashable` parameter and the body unchanged. Example:
```python
def gen_lookup_key(self, key: typing.Hashable) -> typing.Hashable:
    ...  # body unchanged
```

- [ ] **Step 12: Run mypy to verify everything passes**

Run: `uv run mypy src test`
Expected: `Success: no issues found`.

- [ ] **Step 13: Run the full test suite and confirm no runtime regression**

Run: `uv run pytest -q`
Expected: all tests pass (36 existing + 6 new = 42).

- [ ] **Step 14: Commit**

Run `git status` to catch any related unstaged or untracked files (e.g. `uv.lock`
after the dependency change), then use the `creative-commits` skill.

---

## Task 2: Documentation and full cross-version verification

Documents the feature and verifies the whole change across all supported Pythons and the docs build.

**Files:**
- Modify: `docs/iterating_over_registries.rst`

- [ ] **Step 1: Document the optional key type**

In `docs/iterating_over_registries.rst`, add a short subsection explaining that
registry keys default to `str` (so `for key in registry` and `registry.keys()`
yield `str` with no `str()` coercion), and that a different key type can be
declared via `ClassRegistry[ValueType, KeyType]` (e.g.
`ClassRegistry[MyBase, Hashable]` to retain the old permissive behaviour). Use
reStructuredText consistent with the existing file; keep lines ≤80 chars; do not
introduce Sphinx warnings.

- [ ] **Step 2: Build the docs and check for warnings**

Run: `uv run make -C docs clean && uv run make -C docs html`
Expected: build succeeds with no warnings (ReadTheDocs treats warnings as errors).

- [ ] **Step 3: Confirm the test count increased**

Run: `uv run pytest --collect-only -q | tail -1`
Expected: `42 tests collected` (36 baseline + 6 new).

- [ ] **Step 4: Run the full type check and test suite**

Run: `uv run mypy src test && uv run pytest -q`
Expected: mypy `Success`; all tests pass.

- [ ] **Step 5: Run tox across all supported Python versions**

Run: `uv run tox -p`
Expected: `py312`, `py313`, `py314` all pass (each runs `pytest` and `mypy`).
This is the critical check that the `typing_extensions` 3.12 branch works.

- [ ] **Step 6: Commit**

Run `git status` first, then use the `creative-commits` skill.

---

## Release Note (for the eventual `release` skill — not this plan)

ADR 002 requires flagging the `str`-default narrowing at release time: existing
code using non-str keys under a bare `ClassRegistry[Foo]` will see new
type-check errors (runtime unchanged); the fix is `ClassRegistry[Foo, Hashable]`.
There is no `CHANGELOG` file — release notes live on GitHub via the `release`
skill, so this is recorded here as a reminder rather than a plan step.

---

## Intentional Decisions

*(Populated during review — reviewers must not re-raise these)*

- **All source edits are one task** (not split per module). The `str` default is
  global once `base.py` changes, so no split ordering keeps `mypy src test` green
  mid-way; splitting would only create transient red states.
- **`K` defaults to `str`, not `Hashable`** (ADR 002). The type-checker-visible
  narrowing for existing non-str-key callers is accepted; runtime is unchanged.
- **`K` parametrises only the public key.** Lookup keys (`gen_lookup_key` output,
  `_registry`/`_lookup_keys` values, `__missing__`, `_register`, `_unregister`)
  stay `Hashable` because `gen_lookup_key` may change the key's type (ADR 002).
- **`__missing__(key: typing.Hashable)` is not `K`.** `ClassRegistry.get_class`
  invokes it with the *lookup* key, so `Hashable` is correct.
- **`register`'s `else` branch casts `key` to `K`.** There `key` is inferred as
  `D | K`; without the cast, `gen_lookup_key(key)` and `_lookup_keys[key]` reject
  it. The current code only survives because those surfaces were `Hashable`.
- **`gen_lookup_key` becomes an instance method** (converted from `@staticmethod`).
  It is always called via an instance, binds `K` to the registry's key type, and
  is uniform with the other key-facing methods; behaviour-preserving, and existing
  `@staticmethod` overrides stay valid at runtime and under mypy (verified).
  `create_instance` stays a `staticmethod` — it does not involve `K`.
- **`ClassRegistryInstanceCache` is not parametrised by `K`.** It stays
  `Mapping[typing.Hashable, T]` and accepts `ClassRegistry[T, typing.Any]`.
  Reason: its `__iter__` deliberately yields cached *instances* (`T`), which is
  incompatible with `Mapping[K, T]`'s required `Iterator[K]` (verified: mypy
  rejects `Generator[T]` vs `Iterator[K]`); and it passes lookup keys to
  `registry.get` internally. `Hashable` keys already accept any input, so there
  is no DX loss.
- **`RegistryPatcher` is not parametrised by `K`.** Its `**kwargs` API is
  inherently `str`-keyed; widening the wrapped registry to
  `BaseMutableRegistry[T, typing.Any]` is enough to accept any registry.
- **`EntryPointClassRegistry` pins `K=str`** (ADR 002) — entry-point names are
  always `str`.
- **`typing_extensions` floor is `>=4.6`** (ADR 001) — tracks the finalised PEP
  696 spec.

## Self-Review Checklist

- [x] Does the plan header include a `**Worktree:**` field? Yes.
- [x] Does every commit step remind the agent to run `git status` first? Yes (Tasks 1–2).
- [x] Does the plan include an Intentional Decisions section? Yes.
- [x] **Spec coverage:** issue #100 (optional key type defaulting to `str`) → Task 1; ADR 001 (typing_extensions/3.12) → Task 1 Step 1 + Task 2 Step 5; ADR 002 (str default, K scope, EntryPoint pin, release note) → Task 1 + Release Note section; docs → Task 2.
- [x] **Placeholder scan:** no TBD/TODO; all code shown.
- [x] **Type consistency:** `K`/`T`, `Mapping[Hashable, T]`, `BaseMutableRegistry[T, typing.Any]`, `ClassRegistry[T, typing.Any]`, the `register` cast, and the `from .base import BaseMutableRegistry, K, RegistryKeyError, T` import are consistent across steps and the Interfaces block.
