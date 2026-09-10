---
status: Accepted
date: 2026-09-10
scope: [docs/, .autohooks/, pyproject.toml]
summary: Add a docs_build autohooks plugin that runs sphinx-build -W on staged docs/docstring changes, matching ReadTheDocs' fail_on_warning rather than the CI docs job's lenient build.
---

# 006: Check the Docs Build in the Pre-Commit Hook

## Context

[`005`][] enabled `autosectionlabel` on a docs source that already had two
`duplicate label` collisions. Neither the pre-commit hooks nor CI caught
this before it reached a pull request: `.github/workflows/build.yml`'s
`docs` job runs plain `uv run make html`, with no `SPHINXOPTS=-W`, so it
only fails when Sphinx itself errors — a warning still exits 0. Verified by
re-running that exact job command against [`005`][]'s two collisions,
reproduced by reverting `docs/conf.py` and `docs/index.rst` to their
pre-005 state: it built the warnings and reported success. Only
`.readthedocs.yaml`'s
`fail_on_warning: true`, which governs the actual published build, would
have caught it — and that build runs after merge, not on the pull request.

So a docs change can pass every check this repo runs before merge and still
break the published docs, discovered only by whoever next visits
readthedocs.org. The autohooks pre-commit chain already runs mypy, ruff,
pytest and the ADR index generator, so it's the established place to add a
check that catches this before it leaves the developer's machine at all.

## Options

### Option 1: Do nothing

**Pros:** No new dependency on Sphinx succeeding at commit time, and no
risk of a network hiccup (e.g. `intersphinx`'s fetch of the Python
inventory) blocking an unrelated commit.
**Cons:** The gap [`005`][] fell into stays open — a docs change can pass
every pre-merge check and still break the published build, caught only
after merge.

### Option 2: Mirror the CI `docs` job (no `-W`)

Run `uv run make html` — the same command CI runs — as a new pre-commit
step.
**Pros:** Matches the existing CI check exactly, so there's one build
policy to reason about, not two.
**Cons:** Verified the same way as in Context — it still reports success on
005's two `duplicate label` warnings. It would not have caught the problem
this ADR exists to prevent.

### Option 3: Run `sphinx-build -W` on staged docs/docstring changes (Accepted)

Add a `docs_build` autohooks plugin, alongside the existing `adr_index`
one, that runs `sphinx-build -b html -W --keep-going` when a staged file
matches `docs/*.rst`, `docs/conf.py`, or `src/*.py` — the last because
autodoc pulls docstrings into the built API page, so a docstring change can
break the build the same way an `.rst` change can.
**Pros:** Verified the same way — `-W` turns both `duplicate label`
warnings into build failures, matching what `fail_on_warning: true` does on
ReadTheDocs. Scoping to staged
docs-affecting files, rather than running on every commit, keeps an
unrelated source change from paying for a Sphinx build it can't break.
**Cons:** A network hiccup fetching `intersphinx`'s Python inventory can
turn `-W` into a spurious failure on an otherwise-fine commit; Sphinx
caches that inventory for `intersphinx_cache_limit` days, so this bites at
most that often, not on every commit.
**Risks:** The include patterns (`docs/*.rst`, `docs/conf.py`, `src/*.py`)
are the same kind of allowlist as the existing `mypy` plugin's `include`
config — accurate today, but a future docs source outside those three
patterns (e.g. a generated `.rst` file, or docstrings under a second
package) would need the list extended by hand.

## Decision

Option 3. Option 2 reproduces the exact gap this ADR is closing — verified,
not assumed, by replaying it against 005's two collisions. Scoping the
check to staged docs-affecting files, rather than running it on
every commit like `mypy`/`ruff`/`pytest` already do, is deliberate: unlike
those checks, a Sphinx build can only be broken by changes under `docs/` or
by a docstring, so anything else pays nothing for this hook.

## Consequences

- `.autohooks/docs_build.py` is added, following `adr_index.py`'s pattern:
  an autohooks plugin that no-ops when nothing staged is relevant.
- `pyproject.toml`'s `[tool.autohooks]` `pre-commit` list gains
  `docs_build`.
- A docs or docstring change that would break the ReadTheDocs build is now
  caught at commit time, not discovered after merge.
- This pre-commit check and the CI `docs` job now enforce different
  policies (`-W` vs. not) on the same build. CI stays lenient rather than
  gaining `-W` itself, since `-W` failing there would duplicate what this
  hook already caught earlier, one commit before — the value of moving the
  check earlier, not a reason to also run it twice.
- A commit made offline, or during an `intersphinx` inventory cache miss,
  can fail this hook on a docs-affecting change for a reason unrelated to
  the change itself; `--no-verify` is the escape hatch for that case, as
  for any pre-commit check.

[`005`]: 005-enable-autosectionlabel-with-document-prefixed-labels.md
