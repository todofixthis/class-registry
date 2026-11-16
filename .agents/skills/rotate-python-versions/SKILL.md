---
name: rotate-python-versions
description: Use when adding or dropping Python version support, or when the python-policy CI check fails — re-answering python_version through copier so requires-python, tox environments, the CI test matrix and docs follow it, then removing compat code for dropped versions.
---

# Rotate Python Versions

The project supports three Python releases: `python_version` in `.copier-answers.yml`, the newest, and the two before it. The template `todofixthis/cookiecutter-py` derives `requires-python`, the classifiers, the tox environments, the CI matrix and the version lists in `README.rst` and `docs/` from that answer, so a rotation re-answers it through copier rather than editing those files by hand. The range always moves as a whole: dropping the oldest version means raising `python_version` by one, which also adds a version. When the user asks only to drop one, say so and confirm before going ahead.

The template sets the target: CI's `python-policy` job fails while `python_version` is behind the template's policy, which its `run:` step in `.github/workflows/python-policy.yml` names. Work on the branch that carries the template release raising the policy (its Renovate update PR, or the default branch once that has merged): elsewhere the job still shows the old policy. Rotate to the policy unless the user names another version. Renovate never moves Python (ADR 015 in todofixthis/cookiecutter-py), because a rotation also removes compat code, which only a session can do.

## Before changing anything

Add a version only once it has a final release. Run `uv python list X.Y --only-downloads`: if every match carries an `a`, `b` or `rc` suffix (e.g. `cpython-3.15.0rc2`), the version isn't final, so ask the user how to proceed. ReadTheDocs builds on the newest supported version too, so it must also list X.Y under `build.tools.python` in its [config-file reference](https://docs.readthedocs.io/en/stable/config-file/v2.html#build-tools-python); if it doesn't, ask the user, since docs builds would fail while CI stays green.

Branch protection requires only the `gate` job, whose name doesn't change with the matrix, so a rotation needs no ruleset change.

## Apply the new range through copier

Commit any local changes (`copier update` needs a clean working tree), then run:
```bash
uvx "copier>=9,<10" update --defaults --vcs-ref=:current: --data python_version=X.Y
```
`:current:` keeps the project on its current template version. copier can leave conflict markers or `.rej` files and still exit 0, so check `git status` for `.rej` files and run `rg -n '^(<{7}|>{7})' .` (exit 1 means none) before going on; resolve each by keeping this project's own changes and taking the template's side for the Python range.

Then run `uv lock` and commit `uv.lock` with the rest: a stale lock no longer matches `pyproject.toml`, so CI's `uv sync` silently re-resolves it and tests dependencies nobody committed (`uv lock --check` confirms it is current).

copier doesn't reach everything. Check by hand:
- **`pyproject.toml`** — `requires-python` changes only its lower bound and keeps the rest of the specifier (e.g. a `, <4` cap); use `>=X.Y`, never `~=X.Y` without a patch version, which is ambiguous and triggers a uv warning
- **`docs/` and `README.rst`** — any version list this project wrote itself (not ADRs under `docs/adr/`, which record the versions at the time of each decision)
- **`.agents/rules/project.md`** — any version range this project's own rules mention

## Remove compat code

When dropping a version, remove code that exists only to support it: version checks (`sys.version_info` comparisons), fallback imports (`try: import tomllib` / `except ImportError`), dependency markers that only match dropped versions (`; python_version < "3.12"`), and `typing_extensions` imports of names `typing` provides at the new floor. Search with:
```bash
rg -n "version_info|python_(full_)?version *[<>=!]|typing_extensions|except (ImportError|ModuleNotFoundError)" src test docs pyproject.toml
```
It exits 1 when nothing matches, which is not a failure. Adopt syntax the new floor allows only where ruff's `UP` rules flag it (`uv run ruff check --select UP --fix`); leave other modernisation for its own change.

## After editing

Search for stray references. `--hidden` is needed to reach `.github/workflows/`, so the `!` globs keep out the directories it would otherwise add:
```bash
rg -n "3\.\d{2}|py3\d{2}" . --hidden --glob "*.toml" --glob "*.yml" --glob "*.rst" --glob "*.md" --glob "!uv.lock" --glob "!docs/adr/**" --glob "!.git/**" --glob "!.venv/**" --glob "!.tox/**"
```

Expect noise from dependency pins (e.g. `pytest-mock>=3.15.1`) and from skill files that mention versions in prose. When dropping a version, every remaining hit for it should be one of those.

Then run `uv run tox run-parallel` and confirm it exits 0. Dependencies can lack wheels for a new version even after its final release: if it fails while installing dependencies (a source build error) rather than in the tests themselves, stop and ask the user; don't install system packages to make the build pass.
