## Architecture

The package is in `src/class_registry/`. The public API (`__init__.py`) exports only `ClassRegistry` and `RegistryKeyError`.

**Class hierarchy:**

- `base.BaseRegistry[ValueType, KeyType]` — read-only abstract base; defines `__getitem__`/`get`/`get_class`/`keys`/`classes`, plus extension points `gen_lookup_key` and `create_instance`.
- `base.BaseMutableRegistry[ValueType, KeyType]` — extends `BaseRegistry` with `register`/`unregister` (and deprecated `items`/`values`).
- `registry.ClassRegistry[ValueType, KeyType]` — the main concrete implementation; stores classes in a dict, supports `unique` mode to prevent key collisions.
- `registry.SortedClassRegistry[ValueType, KeyType]` — extends `ClassRegistry`; overrides `keys()` to sort by a `sort_key` attribute or callable.
- `entry_points.EntryPointClassRegistry[ValueType]` — extends `BaseRegistry`, pinning its key type to `str` (read-only); discovers classes via setuptools entry points, lazily cached.
- `cache.ClassRegistryInstanceCache[ValueType, KeyType]` — wraps a `ClassRegistry`, caching instantiated objects rather than classes (for service-registry use cases).
- `patcher.RegistryPatcher[ValueType, KeyType]` — context manager that temporarily patches a `BaseMutableRegistry`, then restores the original state on exit.

**`AutoRegister`:**
- `base.AutoRegister(registry)` — current API; returns a **base class** whose non-abstract subclasses auto-register. Requires `registry.attr_name` to be set.
- `auto_register.AutoRegister` — **deprecated** metaclass variant; kept for backwards compatibility only.

**Key design details:**
- `gen_lookup_key` is the hook for key normalisation (override in subclasses for aliases, case-folding, etc.).
- `BaseMutableRegistry._lookup_keys` maps human-readable keys → lookup keys, enabling correct iteration order and `unregister`.
- `RegistryKeyError` (subclass of `KeyError`) distinguishes registry misses from other `KeyError`s; `__missing__` is the override point for default-value behaviour.
