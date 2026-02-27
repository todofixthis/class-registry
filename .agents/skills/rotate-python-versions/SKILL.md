---
name: rotate-python-versions
description: Use when adding or dropping Python version support — updating requires-python, tox environments, CI matrix, and docs to reflect a new set of supported versions.
---

# Rotate Python Versions

Update all version references consistently when adding or dropping Python support.

## Locations to update

- **`pyproject.toml`** — `requires-python` constraint and tox `env_list`
- **`.github/workflows/`** — CI matrix `python-version` list
- **`docs/` and `README.rst`** — requirements/compatibility version list
- **`CLAUDE.md`** — any version range mentioned in comments

## Key detail

Use `>=X.Y` for `requires-python`, not `~=X.Y` without a patch version — the tilde specifier without a patch (e.g. `~=3.12`) is ambiguous and triggers a uv warning.

## After editing

Search for stray references:
```bash
rg "3\.\d{2}|py3\d{2}" --glob "*.toml" --glob "*.yml" --glob "*.rst" --glob "*.md"
```

Then verify all environments pass:
```bash
uv run tox -p
```
