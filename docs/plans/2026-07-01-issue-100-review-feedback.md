# Issue #100 Review Feedback Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Incorporate the nine review comments on PR #101 (optional generic key type) — self-documenting TypeVars, key-type inference for the cache/patcher, richer docstrings, migration-framed docs, and an ADR for the TypeVar convention.

**Architecture:** The generic key type `K` and value type `T` are renamed to `KeyType`/`ValueType`, defined once in `base.py`, exported, and imported everywhere (no per-module redefinition). `ClassRegistryInstanceCache` and `RegistryPatcher` become generic over both, inferring `KeyType` from their wrapped registry (validated: mypy infers correctly; a few localised, documented `cast`s bridge the internal lookup-key boundary). The remaining comments are documentation: ADR/​docstring/​migration-note improvements plus a final audience-surrogate doc review.

**Tech Stack:** Python 3.12–3.14, mypy `--strict`, PEP 696 `TypeVar` defaults (native 3.13+, `typing_extensions` on 3.12), Sphinx/Napoleon docs, pytest.

## Global Constraints

- **TypeVar names:** `T` → `ValueType`, `K` → `KeyType` (decided). The decorator TypeVar `D` in `base.py` is internal and stays as-is.
- **Single definition:** `ValueType` and `KeyType` are defined once in `src/class_registry/base.py`, listed in its `__all__`, and imported from `.base` by every other module. No module redefines them.
- **`KeyType`** keeps `bound=typing.Hashable, default=str`; `ValueType` is unbounded. Internal **lookup** keys stay `typing.Hashable` (ADR 002).
- **Target version for migration docs:** `6.0.0` (educated guess — this is a type-only breaking change per ADR 002). **Do NOT bump `pyproject.toml`'s version**; the release process owns the bump.
- **Python floor stays 3.12** via the existing `sys.version_info`-gated `TypeVar` import (ADR 001) — unchanged by this work.
- mypy `--strict` clean on `src` + `test`; `pytest` green; `tox -p` green on py312/py313/py314; docs build with zero Sphinx warnings (ReadTheDocs treats warnings as errors).
- **Style:** NZ English; Google/Napoleon docstrings, ≤80 chars/line, blank line before lists inside `Args:`/description blocks; comments on the line *preceding* the code; escape backslashes in docstrings.
- **Worktree:** all work in `/Users/phx/Documents/class-registry/.agents/worktrees/issue-100-generic-key-type`. The shell can silently reset to the main checkout, so **prefix every state-mutating command with `cd <worktree> &&`** and run tooling via `uv run`.
- **Test count:** this PR adds no new test *functions* (only docstrings + two strengthened assertions), so `uv run pytest --collect-only` stays at **42**. Confirm it does not *drop*.
- **Subagent models (project memory):** implementer subagents use **Claude Sonnet**; reviewer / audience-surrogate subagents use **Opus**.

---

## Task 1: ADR 003 — Centralise and Export Shared TypeVars

**Files:**
- Create: `docs/adr/003-centralise-and-export-shared-typevars.md`
- Regenerated: `docs/adr/INDEX.md` (by the `adr_index` pre-commit hook — do not hand-edit)

**Interfaces:**
- Produces: the naming (`ValueType`/`KeyType`) and single-definition convention that Task 2 implements. Later tasks reference `docs/adr/003`.

- [ ] **Step 1: Write the ADR**

Use the `writing-adrs` skill for format. Content (fill the standard sections — Context / Options / Decision / Consequences):

- **Context:** Issue #100 introduced generic `T`/`K`, but each module (`cache.py`, `patcher.py`, previously `registry.py`) redefined its own `T = typing.TypeVar("T")`, and the key TypeVar `K` was terse and unexported. Review of PR #101 flagged the resulting drift: different modules could bind subtly different TypeVars, and the public generic parameters had no discoverable names.
- **Options:** (1) Do nothing — leave per-module TypeVars and single letters. (2) **Accepted:** define the shared TypeVars once in `base.py`, give them self-documenting names (`ValueType`, `KeyType`), export them via `base.__all__`, and import them everywhere. (3) A separate `_typevars.py` module — rejected as over-engineering for two symbols already at home in `base.py`.
- **Decision:** Option 2. `ValueType` and `KeyType` live in `base.py`, are exported, and are imported (never redefined) by sibling modules. Descriptive names double as documentation in signatures like `ClassRegistry[ValueType, KeyType]`.
- **Consequences:** Exporting the TypeVars makes them public API (they appear in rendered signatures and are importable); renaming `K`/`T` is a source-level change only (TypeVars are positional in subscription, so `ClassRegistry[Foo, int]` is unaffected). Establishes the precedent: shared TypeVars are defined once in the module that owns the base abstraction and imported elsewhere. Cross-references ADR 002.

Keep the `date:` frontmatter as `2026-07-01`, `status: Accepted`, and alphabetise the `tags`.

- [ ] **Step 2: Verify the hook regenerates the index**

Run: `cd <worktree> && uv run git add docs/adr/003-centralise-and-export-shared-typevars.md && uv run git commit -m "<creative-commits message>"`
Expected: the `adr_index` pre-commit hook runs and updates `docs/adr/INDEX.md` to include ADR 003. If the commit reports the index changed, `git add docs/adr/INDEX.md` and amend via `uv run git commit --amend --no-edit`.

- [ ] **Step 3: Push**

Run: `cd <worktree> && git push`

---

## Task 2: Rename, Centralise, and Export the Shared TypeVars

**Files:**
- Modify: `src/class_registry/base.py`
- Modify: `src/class_registry/registry.py`
- Modify: `src/class_registry/entry_points.py`
- Modify: `src/class_registry/cache.py`
- Modify: `src/class_registry/patcher.py`

**Interfaces:**
- Produces: `base.ValueType` (unbounded `TypeVar`), `base.KeyType` (`TypeVar(bound=Hashable, default=str)`), both in `base.__all__`. Every generic class header becomes `[...][ValueType, KeyType]` (or `[ValueType, str]` for `EntryPointClassRegistry`).
- Consumes: nothing (foundational).

This is an **atomic** rename — mypy will not be green partway through (the default-`str` `KeyType` is global), so do the whole task before running the final check, exactly as the original #100 source change was consolidated.

- [ ] **Step 1: Update `base.py` TypeVar definitions and `__all__`**

Replace the `__all__` line (alphabetised, adding the two exports):

```python
__all__ = [
    "AutoRegister",
    "BaseMutableRegistry",
    "BaseRegistry",
    "KeyType",
    "RegistryKeyError",
    "ValueType",
]
```

Replace the TypeVar block (currently `T = TypeVar("T")` / `K = TypeVar("K", ...)`):

```python
ValueType = TypeVar("ValueType")

# ``KeyType`` parametrises the public/human-readable key. Lookup keys (produced
# by ``gen_lookup_key``) stay ``Hashable`` — see docs/adr/002.
KeyType = TypeVar("KeyType", bound=typing.Hashable, default=str)

# [#53] Fix incorrect return type from ``register``
D = TypeVar("D", bound=typing.Callable[..., typing.Any])
```

- [ ] **Step 2: Rename usages in `base.py`**

Replace every standalone TypeVar reference `T` → `ValueType` and `K` → `KeyType` throughout `base.py` (whole-word; they occur only as TypeVar references, e.g. `Generic[T, K]`, `-> typing.Type[T]`, `key: K`, `dict[K, typing.Hashable]`, `BaseRegistry[T, K]`, `AutoRegister(registry: BaseMutableRegistry[T, typing.Any])` → `[ValueType, typing.Any]`). Leave `D`, `typing.Hashable`, and `typing.Any` untouched.

- [ ] **Step 3: Update the sibling modules to import (not redefine)**

`registry.py` — replace the import and rename usages:

```python
from .base import BaseMutableRegistry, KeyType, RegistryKeyError, ValueType
```
Then `T` → `ValueType`, `K` → `KeyType` throughout (`ClassRegistry(BaseMutableRegistry[T, K])` → `[ValueType, KeyType]`, `SortedClassRegistry(ClassRegistry[T, K])`, the sorter tuple types, etc.).

`entry_points.py` — it pins the key type to `str`, so it needs only `ValueType`:

```python
from .base import BaseRegistry, ValueType
```
Then `T` → `ValueType` throughout (`EntryPointClassRegistry(BaseRegistry[T, str])` → `[ValueType, str]`).

`cache.py` — delete the local `T = typing.TypeVar("T")` and import from base:

```python
from . import ClassRegistry
from .base import ValueType
```
Then `T` → `ValueType` throughout. Import **only** `ValueType` here — `KeyType` is unused until Task 3 introduces it, and importing it now would trip ruff's unused-import check. Leave the `typing.Any` key placeholders as-is.

`patcher.py` — delete the local `T = typing.TypeVar("T")` and import from base:

```python
from .base import BaseMutableRegistry, ValueType
```
Then `T` → `ValueType` throughout. As with `cache.py`, import only `ValueType`; Task 4 adds `KeyType`. Leave the `typing.Any` placeholders for now.

- [ ] **Step 4: Type-check and test**

Run: `cd <worktree> && uv run mypy src test && uv run pytest`
Expected: mypy clean (18 files), 42 passed. If mypy reports an unused `type: ignore` or an unused import, resolve it (these confirm the rename is complete).

- [ ] **Step 5: Commit and push**

```bash
cd <worktree> && uv run git commit -am "<creative-commits message>" && git push
```

---

## Task 3: `ClassRegistryInstanceCache` Infers `KeyType`

Validated experiment: making the cache `Generic[ValueType, KeyType]` and typing the constructor arg `ClassRegistry[ValueType, KeyType]` makes mypy infer `KeyType` from the wrapped registry (`Cache(int_reg)` → `Cache[Pokemon, int]`). Two internal calls pass **lookup** keys (`Hashable`) into the now-`KeyType`-typed `get`/`gen_lookup_key`; bridge each with a documented `typing.cast(KeyType, ...)` (mirroring the existing `cast(KeyType, key)` in `base.register`). The `Mapping` base stays `Mapping[Hashable, ValueType]` because `__iter__` yields values, not keys.

**Files:**
- Modify: `src/class_registry/cache.py`
- Test: `test/test_typing.py` (`test_instance_cache_accepts_non_str_key_registry`)

**Interfaces:**
- Consumes: `base.ValueType`, `base.KeyType`.
- Produces: `ClassRegistryInstanceCache(typing.Mapping[typing.Hashable, ValueType], typing.Generic[ValueType, KeyType])`; `.registry` property returns `ClassRegistry[ValueType, KeyType]`.

- [ ] **Step 1: Strengthen the typing test to require inference (failing)**

Replace the body of `test_instance_cache_accepts_non_str_key_registry` in `test/test_typing.py`:

```python
def test_instance_cache_infers_key_type_from_registry() -> None:
    registry: ClassRegistry[Widget, int] = ClassRegistry()

    @registry.register(7)
    class Seven(Widget):
        pass

    cache = ClassRegistryInstanceCache(registry)

    typing.assert_type(cache, ClassRegistryInstanceCache[Widget, int])
    typing.assert_type(cache.registry, ClassRegistry[Widget, int])
    typing.assert_type(cache[7], Widget)
```

- [ ] **Step 2: Run mypy to verify it fails**

Run: `cd <worktree> && uv run mypy test/test_typing.py`
Expected: FAIL — `assert_type` mismatch, because the cache is not yet generic over the key type (inferred `ClassRegistryInstanceCache[Widget]`, not `[Widget, int]`).

- [ ] **Step 3: Make the cache generic over `KeyType`**

In `cache.py`, add `KeyType` to the base import:

```python
from .base import KeyType, ValueType
```

Change the class header and the wrapped-registry annotations from `typing.Any` to `KeyType`:

```python
class ClassRegistryInstanceCache(
    typing.Mapping[typing.Hashable, ValueType],
    typing.Generic[ValueType, KeyType],
):
```
```python
        class_registry: ClassRegistry[ValueType, KeyType],
```
```python
        self._registry: ClassRegistry[ValueType, KeyType] = class_registry
```
```python
    @property
    def registry(self) -> ClassRegistry[ValueType, KeyType]:
```

Bridge the two lookup-key boundary calls with documented casts:

```python
            # ``class_key`` is a lookup key (``Hashable``); the wrapped
            # registry's ``get`` is typed against the public ``KeyType``. The
            # cast is runtime-erased — see docs/adr/002.
            self._cache[instance_key] = self._registry.get(
                typing.cast(KeyType, class_key),
                *self._template_args,
                **self._template_kwargs,
            )
```
```python
    def get_class_key(self, key: typing.Hashable) -> typing.Hashable:
        """
        ...unchanged docstring...
        """
        # ``key`` arrives as ``Hashable`` (the ``Mapping`` contract); the
        # registry's ``gen_lookup_key`` is typed against ``KeyType``.
        return self._registry.gen_lookup_key(typing.cast(KeyType, key))
```

Leave `__getitem__`, `get_instance_key`, `get_class_key`, `_cache`, and `_key_map` keyed on `typing.Hashable` (the `Mapping` contract and the lookup-key level).

- [ ] **Step 4: Run mypy + pytest to verify pass**

Run: `cd <worktree> && uv run mypy src test && uv run pytest`
Expected: mypy clean, 42 passed.

- [ ] **Step 5: Commit and push**

```bash
cd <worktree> && uv run git commit -am "<creative-commits message>" && git push
```

---

## Task 4: `RegistryPatcher` Infers `KeyType`

Validated experiment: making the patcher `Generic[ValueType, KeyType]` and typing `registry: BaseMutableRegistry[ValueType, KeyType]` infers `KeyType` (`Patcher(int_reg)` → `Patcher[Pokemon, int]`). Three internal helpers pass `Hashable` keys into the now-`KeyType`-typed `get_class`/`register`/`unregister`; bridge each with a documented `typing.cast`. The patcher's *added* keys remain `str` (kwargs) / `Hashable`; inference precisely types `.target` (removing the `Any` leak) while the casts bridge the internal calls.

**Files:**
- Modify: `src/class_registry/patcher.py`
- Test: `test/test_typing.py` (`test_patcher_accepts_non_str_key_registry`)

**Interfaces:**
- Consumes: `base.ValueType`, `base.KeyType`.
- Produces: `RegistryPatcher(typing.Generic[ValueType, KeyType])`; `.target` typed `BaseMutableRegistry[ValueType, KeyType]`.

- [ ] **Step 1: Strengthen the typing test to require inference (failing)**

Replace the body of `test_patcher_accepts_non_str_key_registry` in `test/test_typing.py`:

```python
def test_patcher_infers_key_type_from_registry() -> None:
    registry: ClassRegistry[Widget, int] = ClassRegistry(attr_name="key")

    patcher = RegistryPatcher(registry)

    typing.assert_type(patcher, RegistryPatcher[Widget, int])
    typing.assert_type(patcher.target, BaseMutableRegistry[Widget, int])
```

- [ ] **Step 2: Run mypy to verify it fails**

Run: `cd <worktree> && uv run mypy test/test_typing.py`
Expected: FAIL — inferred `RegistryPatcher[Widget]` / `.target` is `BaseMutableRegistry[Widget, Any]`, not `[Widget, int]`.

- [ ] **Step 3: Make the patcher generic over `KeyType`**

In `patcher.py`, add `KeyType` to the base import:

```python
from .base import BaseMutableRegistry, KeyType, ValueType
```

Change the class header and `registry`/`target` annotations from `typing.Any` to `KeyType`:

```python
class RegistryPatcher(typing.Generic[ValueType, KeyType]):
```
```python
        registry: BaseMutableRegistry[ValueType, KeyType],
```
```python
        self.target: BaseMutableRegistry[ValueType, KeyType] = registry
```

Bridge the three internal calls (keys are `Hashable`/`str`; the target's API is now `KeyType`-typed):

```python
    def _get_value(
        self,
        key: typing.Hashable,
        default: typing.Any = None,
    ) -> typing.Any:
        try:
            # ``key`` is ``Hashable`` at this layer; ``target`` is typed against
            # ``KeyType``. The cast is runtime-erased — see docs/adr/002.
            return self.target.get_class(typing.cast(KeyType, key))
        except RegistryKeyError:
            return default

    def _set_value(self, key: typing.Hashable, value: typing.Type[ValueType]) -> None:
        self.target.register(typing.cast(KeyType, key))(value)

    def _del_value(self, key: typing.Hashable) -> None:
        try:
            self.target.unregister(typing.cast(KeyType, key))
        except RegistryKeyError:
            pass
```

Leave `_new_values`/`_prev_values` and the helper param types as-is (`str`/`Hashable`).

- [ ] **Step 4: Run mypy + pytest to verify pass**

Run: `cd <worktree> && uv run mypy src test && uv run pytest`
Expected: mypy clean, 42 passed.

- [ ] **Step 5: Commit and push**

```bash
cd <worktree> && uv run git commit -am "<creative-commits message>" && git push
```

---

## Task 5: Document `ValueType`/`KeyType` and the `gen_lookup_key` Return Type

Review comments: extend `BaseRegistry`'s docstring to document the type parameters (the signature is getting complicated); add a note to `gen_lookup_key` explaining why it returns `Hashable` rather than `KeyType`.

**Files:**
- Modify: `src/class_registry/base.py` (`BaseRegistry` class docstring; `gen_lookup_key` docstring)

**Interfaces:** none (docs only).

- [ ] **Step 1: Expand the `BaseRegistry` class docstring**

Replace the current one-line docstring:

```python
class BaseRegistry(typing.Generic[ValueType, KeyType], ABC):
    """
    Base functionality for registries.

    The two type parameters are:

    - ``ValueType`` — the registered class, and the instance that
      :py:meth:`get` returns.
    - ``KeyType`` — the public key used to look a class up (passed to
      :py:meth:`get`/:py:meth:`register` and returned by :py:meth:`keys`).
      Defaults to :py:class:`str`.  The *internal* lookup key produced by
      :py:meth:`gen_lookup_key` is always
      :py:class:`~collections.abc.Hashable` and is deliberately not
      parametrised (see docs/adr/002).
    """
```
(Blank line before the bulleted list to avoid Sphinx indentation warnings.)

- [ ] **Step 2: Add the `gen_lookup_key` return-type note**

Append a `Note:` section to the `gen_lookup_key` docstring, after `Returns:`:

```python
        Returns:
            The registry key, used to look up the corresponding class.

        Note:
            The return type is :py:class:`~collections.abc.Hashable` rather
            than ``KeyType``.  This hook may change the key's type — e.g.
            case-folding, or wrapping the key in a tuple — so the lookup key
            it produces can differ from the public key.  See docs/adr/002.
```

- [ ] **Step 3: Build the docs to verify no Sphinx warnings**

Run: `cd <worktree> && uv run make -C docs clean && uv run make -C docs html`
Expected: build succeeds, zero warnings.

- [ ] **Step 4: Type-check (docstrings shouldn't change types) and commit**

```bash
cd <worktree> && uv run mypy src test && uv run git commit -am "<creative-commits message>" && git push
```

---

## Task 6: Improve ADR 002 (Example Code + Major-Version Mitigation)

Review comments on `docs/adr/002-default-registry-key-type-to-str.md`: the Context paragraphs are dense — add example code; note that the type-only break (Options 2 and 3) is mitigated by a new major version with migration instructions, in the Consequences section.

**Files:**
- Modify: `docs/adr/002-default-registry-key-type-to-str.md`

**Interfaces:** none (docs only).

- [ ] **Step 1: Add before/after example code to the Context**

After the paragraph describing the output-cast friction ("...callers who want `str` back must cast..."), insert:

````markdown
Concretely, the friction is on output. Under the historical `Hashable` typing::

    registry: ClassRegistry[Pokemon] = ClassRegistry("element")
    key = next(iter(registry.keys()))   # inferred type: Hashable
    name: str = str(key)                # explicit cast required

With `str` as the default key type, the common case needs no cast::

    registry: ClassRegistry[Pokemon] = ClassRegistry("element")
    name: str = next(iter(registry.keys()))   # inferred type: str
````

- [ ] **Step 2: Add the major-version mitigation to Consequences**

Add a bullet to the Consequences section:

```markdown
- The type-checker-visible narrowing (shared by Options 2 and 3) is mitigated
  by shipping this change in a new **major version** (targeted 6.0.0): the
  narrowing and its one-line fix are called out in the release notes and in the
  migration note in `docs/iterating_over_registries.rst`.
```

- [ ] **Step 3: Build docs (ADRs are Markdown, but confirm nothing breaks) and commit**

```bash
cd <worktree> && uv run git commit -am "<creative-commits message>" && git push
```

---

## Task 7: Migration-Framed Docs + `docs/*.rst` Sweep

Review comments: reframe the `iterating_over_registries.rst` note as **migration instructions for v6.0.0** using the real mypy error (captured: `Argument 1 to "get_class" of "ClassRegistry" has incompatible type "int"; expected "str"  [arg-type]`); and (from the TypeVar-drift comment) review all `docs/*.rst` so a developer needs no prior knowledge of `phx-class-registry` internals. Use the `writing-clearly-and-concisely` skill for prose.

**Files:**
- Modify: `docs/iterating_over_registries.rst` (the `.. note::` block, lines ~75–80)
- Review, modify as needed: the other `docs/*.rst` (`getting_started`, `index`, `advanced_topics`, `service_registries`, `entry_points`, `api`, `upgrading_to_v5`)

**Interfaces:** none (docs only).

- [ ] **Step 1: Rewrite the migration note**

Replace the existing `.. note::` block in `iterating_over_registries.rst`:

```rst
.. note::

   **Migrating to v6.0.0.**  Registry keys now default to :py:class:`str`.  If
   you have existing code that uses non-:py:class:`str` keys under a bare
   ``ClassRegistry[Foo]``, your type checker will report an error such as:

   .. code-block:: text

      error: Argument 1 to "get_class" of "ClassRegistry" has incompatible
      type "int"; expected "str"  [arg-type]

   Runtime behaviour is unchanged.  To fix it, declare the key type
   explicitly::

      pokedex: ClassRegistry[Pokemon, int] = ClassRegistry('pokedex_id')

   To keep the previous permissive behaviour (any
   :py:class:`~collections.abc.Hashable` key), use::

      from collections.abc import Hashable

      pokedex: ClassRegistry[Pokemon, Hashable] = ClassRegistry('element')
```

- [ ] **Step 2: Sweep the remaining `docs/*.rst`**

Using the `writing-clearly-and-concisely` skill, read each `docs/*.rst` and check, fixing in place where needed:

- The key-type feature is discoverable (getting_started / index should at least point to the "Specifying the Key Type" section).
- No prose relies on undocumented internals; where `ValueType`/`KeyType` now surface in rendered signatures (`api.rst` autodoc), ensure surrounding text explains them or links to the `BaseRegistry` docstring.
- Terminology is consistent with ADR 002 ("public key" vs "lookup key").

Keep edits minimal and focused; do not restructure documents.

- [ ] **Step 3: Build docs to verify zero warnings**

Run: `cd <worktree> && uv run make -C docs clean && uv run make -C docs html`
Expected: build succeeds, zero warnings.

- [ ] **Step 4: Commit and push**

```bash
cd <worktree> && uv run git commit -am "<creative-commits message>" && git push
```

---

## Task 8: Test Docstrings + AGENTS.md Convention

Review comment: add a docstring to every test in `test_typing.py` explaining its purpose, and document the convention in AGENTS.md. Scope (decided): the new typing tests only; existing suite backfilled later.

**Files:**
- Modify: `test/test_typing.py` (all 6 test functions)
- Modify: `AGENTS.md` (add a Tests convention)

**Interfaces:** none.

- [ ] **Step 1: Add a one-line docstring to each test**

Add a docstring as the first line of each of the six test bodies (names reflect Tasks 3/4's renames). Suggested text:

```python
def test_class_registry_defaults_keys_to_str() -> None:
    """Bare ``ClassRegistry[Widget]`` types its keys as ``str``."""

def test_class_registry_accepts_explicit_key_type() -> None:
    """``ClassRegistry[Widget, int]`` types its keys as ``int``."""

def test_sorted_class_registry_defaults_keys_to_str() -> None:
    """``SortedClassRegistry`` inherits the default ``str`` key type."""

def test_entry_point_registry_keys_are_str() -> None:
    """``EntryPointClassRegistry`` keys are always ``str``."""

def test_instance_cache_infers_key_type_from_registry() -> None:
    """The instance cache infers its key type from the wrapped registry."""

def test_patcher_infers_key_type_from_registry() -> None:
    """The patcher infers its key type from the registry it patches."""
```

- [ ] **Step 2: Document the convention in AGENTS.md**

Add a new `## Tests` section (place it after the `## Docstrings` section):

```markdown
## Tests

Every test function has a one-line docstring stating the behaviour it verifies.
```

- [ ] **Step 3: Verify + commit**

Run: `cd <worktree> && uv run pytest --collect-only` (expect 42) `&& uv run pytest && uv run mypy src test`
Then:
```bash
cd <worktree> && uv run git commit -am "<creative-commits message>" && git push
```

---

## Task 9: Audience-Surrogate Documentation Review

Review comment: after updating the documentation, dispatch an audience-surrogate subagent to review the doc updates and address any feedback.

**Files:**
- Potentially modify: any `docs/*.rst` or ADR based on findings.

**Interfaces:** none.

- [ ] **Step 1: Dispatch the audience-surrogate reviewer (Opus)**

Dispatch a subagent (Opus) with this brief:

> You are a Python developer who has **never used `phx-class-registry`** and does not know its internals. Read only the rendered/​source documentation in `docs/` (the `.rst` files and `docs/adr/`) in the worktree at `/Users/phx/Documents/class-registry/.agents/worktrees/issue-100-generic-key-type`. Your goal: could you adopt the library — including the optional generic key type and the v6.0.0 migration — using the docs alone? Report every place where the docs assume knowledge you don't have, use an unexplained term (`ValueType`, `KeyType`, "lookup key" vs "public key", `gen_lookup_key`), or leave a question unanswered. Return a concise, prioritised list of concrete gaps with file + line references. Do not edit anything.

- [ ] **Step 2: Triage and address feedback**

For each finding, either fix the doc in place (using `writing-clearly-and-concisely`) or record why it's out of scope. Rebuild docs:

Run: `cd <worktree> && uv run make -C docs clean && uv run make -C docs html`
Expected: zero warnings.

- [ ] **Step 3: Commit and push (if any changes)**

```bash
cd <worktree> && uv run git commit -am "<creative-commits message>" && git push
```

---

## Final Verification

- [ ] **Step 1: Full local gate**

Run each and confirm:
```bash
cd <worktree> && uv run pytest --collect-only    # 42
cd <worktree> && uv run pytest                    # 42 passed
cd <worktree> && uv run mypy src test             # clean (18 files)
cd <worktree> && uv run ruff check                # clean
cd <worktree> && uv run make -C docs clean && uv run make -C docs html   # zero warnings
```

- [ ] **Step 2: Cross-version gate**

Run: `cd <worktree> && uv run tox -p`
Expected: py312 / py313 / py314 all green (exercises the 3.12 `typing_extensions` branch).

- [ ] **Step 3: Confirm the branch is pushed**

Run: `cd <worktree> && git status && git log --oneline origin/feature/issue-100-generic-key-type..HEAD`
Expected: clean working tree; no unpushed commits. PR #101 updates automatically.

---

## Self-Review

**Spec coverage** — every PR review comment maps to a task:

| Review comment | Task |
| --- | --- |
| ADR 002 dense Context — add example code | 6 |
| ADR 002 — note major-version mitigation in Consequences | 6 |
| `iterating_over_registries.rst` — reframe as v6.0.0 migration instructions with real mypy error | 7 |
| `base.py` `BaseRegistry` — document `T`/`K` | 5 |
| `base.py` `gen_lookup_key` — note why return is `Hashable` not `K` | 5 |
| `cache.py` — infer `K` from `class_registry` | 3 |
| `patcher.py` — infer `K` from `registry` | 4 |
| `base.py` TypeVar drift — rename, `__all__`, consistent imports, docs sweep, audience-surrogate review | 1 (ADR), 2 (rename/export/import), 7 (docs sweep), 9 (surrogate) |
| `test_typing.py` — docstring every test + document convention in AGENTS.md | 8 |

**Type consistency:** `ValueType`/`KeyType` are defined once (Task 2), used identically in Tasks 3–5; cache/patcher headers are `Generic[ValueType, KeyType]`; test assertions target `ClassRegistryInstanceCache[Widget, int]` / `RegistryPatcher[Widget, int]` / `BaseMutableRegistry[Widget, int]`, matching the inferred types validated in the experiments.

**Placeholder scan:** none — every code step shows the exact replacement; the one non-code judgement step (Task 7 Step 2 docs sweep) is bounded by an explicit checklist.
