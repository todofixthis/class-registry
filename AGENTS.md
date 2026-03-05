# AGENTS.md

This file provides guidance to coding agents working with code in this repository. Skills and other agent documentation live in `.agents/`.

## Writing for coding agents

- Do not document information that already exists in the coding agent's training data or could be easily discovered by reading the code.
- Do not list individual files; list high-level directories so the agent knows where to look.
- Aim for concise style that optimises token count without sacrificing clarity.

## Commands

```bash
# Install dev dependencies
uv sync --group=dev

# Run tests + type checking across all supported Python versions (3.12–3.14)
uv run tox -p

# Run tests only (current venv)
uv run pytest

# Run a single test file
uv run pytest test/test_class_registry.py

# Run a single test by name
uv run pytest test/test_class_registry.py::TestClassName::test_method_name

# Type checking only
uv run mypy src test

# Build docs
cd docs && uv run make html
```

Pre-commit hooks (black, mypy, pytest, ruff) are activated via autohooks. Always commit via `uv run git commit` so hooks run correctly.

## Architecture

The package is in `src/class_registry/`. The public API (`__init__.py`) exports only `ClassRegistry` and `RegistryKeyError`.

**Class hierarchy:**

- `base.BaseRegistry[T]` — read-only abstract base; defines `__getitem__`/`get`/`get_class`/`keys`/`classes`, plus extension points `gen_lookup_key` and `create_instance`.
- `base.BaseMutableRegistry[T]` — extends `BaseRegistry` with `register`/`unregister` (and deprecated `items`/`values`).
- `registry.ClassRegistry[T]` — the main concrete implementation; stores classes in a dict, supports `unique` mode to prevent key collisions.
- `registry.SortedClassRegistry[T]` — extends `ClassRegistry`; overrides `keys()` to sort by a `sort_key` attribute or callable.
- `entry_points.EntryPointClassRegistry[T]` — extends `BaseRegistry` (read-only); discovers classes via setuptools entry points, lazily cached.
- `cache.ClassRegistryInstanceCache[T]` — wraps a `ClassRegistry`, caching instantiated objects rather than classes (for service-registry use cases).
- `patcher.RegistryPatcher[T]` — context manager that temporarily patches a `BaseMutableRegistry`, then restores the original state on exit.

**`AutoRegister`:**
- `base.AutoRegister(registry)` — current API; returns a **base class** whose non-abstract subclasses auto-register. Requires `registry.attr_name` to be set.
- `auto_register.AutoRegister` — **deprecated** metaclass variant; kept for backwards compatibility only.

**Key design details:**
- `gen_lookup_key` is the hook for key normalisation (override in subclasses for aliases, case-folding, etc.).
- `BaseMutableRegistry._lookup_keys` maps human-readable keys → lookup keys, enabling correct iteration order and `unregister`.
- `RegistryKeyError` (subclass of `KeyError`) distinguishes registry misses from other `KeyError`s; `__missing__` is the override point for default-value behaviour.
