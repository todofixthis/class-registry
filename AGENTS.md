## Getting Started

Before writing code, check:

- `docs/adr/INDEX.md` — prior decisions (don't re-litigate)
- `docs/superpowers/plans/` — current implementation plan, if one exists
- `.agents/rules/` — further rules, some scoped to particular paths. `project.md` there holds this project's own conventions; it may add to, narrow or override a rule in this file or another file in `.agents/rules/`, and wins where the two conflict

## Template-owned files

This project is generated from the copier template `todofixthis/cookiecutter-py`; `.copier-answers.yml` records which release, and each release reaches this project as a Renovate PR running `copier update` (that repo's ADR 008). Before changing any file, check whether `.agents/rules/template-owned.md` lists it, and if so follow that rule. Claude Code loads the rule when you read a listed file; in another harness, read it yourself.

## Architecture Decision Records

When making significant decisions — choosing between libraries, patterns, tools, or conventions — you **must** write an ADR before implementing the decision. Use the `phx:writing-adrs` skill (from the phx plugin, which `.claude/settings.json` enables) for the format, conventions and tooling: its `adr.py` allocates the number, generates `docs/adr/INDEX.md` and validates the corpus. Where the skill isn't available (outside Claude Code, or the plugin isn't loaded), read the [skill](https://github.com/todofixthis/phx-claude-siat/blob/8.1.0/skills/writing-adrs/SKILL.md) and run the same tool as `phx-adr` (see Commands). Don't hand-edit the index, or add a repo-local ADR script, pre-commit hook or vendored copy of the tool. ADRs live in `docs/adr/`.

If you find yourself about to establish a new cross-cutting pattern (something that will affect multiple domains or files, e.g. a testing convention, a shared utility, an error-handling approach), stop and write an ADR first even if the immediate task feels local. A pattern adopted once becomes the template for everything that follows.

## Commands

```bash
# Install the pre-commit hook (once per clone)
uv run autohooks activate --mode=pythonpath
# Always use instead of git commit (runs autohooks)
uv run git commit
# Sync deps after pulling
uv sync --group=dev
# Add a runtime dependency at its latest version
uv add --bounds major <package>
# Add a dev dependency at its latest version
uv add --bounds major --group dev <package>
# Run tests (current Python)
uv run pytest
# Count tests: note it before adding behaviour, and check it has grown after
uv run pytest --collect-only -q
# Run tests (all supported versions)
uv run tox -p
# Type check
uv run mypy src test
# Lint
uv run ruff check
# Check formatting (the pre-commit hook reformats; CI only checks)
uv run black --check .
# Build docs
uv run make -C docs clean && uv run make -C docs html
```

uv resolves only releases at least 3 days old (`exclude-newer` under `[tool.uv]` in `pyproject.toml`), so "latest" above means the latest that old. To take a newer release of one package, exempt it there with `exclude-newer-package = { <package> = false }`, and remove the exemption once the release is 3 days old.

**In a worktree:** the shell can silently reset to the main checkout, so always prefix state-mutating commands (`uv add`/`sync`/`run`) with `cd <worktree> &&` to ensure they hit the worktree.

The phx plugin's ADR tool, for use where the skill isn't available. Renovate bumps these pins and the `adrs` CI job's together, matching each on its trailing `# X.Y.Z` comment (ADR 009 in todofixthis/cookiecutter-py) — keep that comment on the same line, despite the Code Comments rule below; moved or dropped, that pin silently stops being bumped.

```bash
# Scaffold the next ADR
uvx --from 'git+https://github.com/todofixthis/phx-claude-siat@0725567cec6bab6a227c2a3d569e64c226c33a4e#subdirectory=skills/writing-adrs' phx-adr new "Title" --summary "…" --scope path/ # 8.1.0
# List the decisions binding a path, before changing it
uvx --from 'git+https://github.com/todofixthis/phx-claude-siat@0725567cec6bab6a227c2a3d569e64c226c33a4e#subdirectory=skills/writing-adrs' phx-adr for path/to/file # 8.1.0
# Mark an ADR superseded
uvx --from 'git+https://github.com/todofixthis/phx-claude-siat@0725567cec6bab6a227c2a3d569e64c226c33a4e#subdirectory=skills/writing-adrs' phx-adr supersede OLD --by NEW # 8.1.0
# Regenerate docs/adr/INDEX.md
uvx --from 'git+https://github.com/todofixthis/phx-claude-siat@0725567cec6bab6a227c2a3d569e64c226c33a4e#subdirectory=skills/writing-adrs' phx-adr index # 8.1.0
# Validate, as CI does
uvx --from 'git+https://github.com/todofixthis/phx-claude-siat@0725567cec6bab6a227c2a3d569e64c226c33a4e#subdirectory=skills/writing-adrs' phx-adr check # 8.1.0
```

If CI reports a stale index the session's own tool can't reproduce, the installed plugin (which tracks phx-claude-siat's `main`) and the pinned release differ. Compare the two versions: if the installed one is newer, merge Renovate's pending bump, or bump by hand: each pin to the release's commit, and its comment and the skill link above to the release's version. The commit is the `refs/tags/<version>^{}` line of `git ls-remote --tags https://github.com/todofixthis/phx-claude-siat`, not the tag object above it. Otherwise update the plugin.

## Docstrings

Google/Napoleon format (`Args:`, `Returns:`, `Note:`) — not Sphinx `:param:` style. Max 80 chars per line. Escape backslashes (e.g. `'\\n'` not `'\n'`). Blank line before lists inside `Args:` sections to avoid Sphinx indentation warnings. ReadTheDocs treats all Sphinx warnings as errors — resolve them before pushing.

## Code Comments

Place comments on the line preceding the code they document, not as trailing
comments.

Write or update each comment — including one that describes code you move
or change, wherever it sits — for a reader who never saw the diff: name what
it refers to rather than pointing at the change ("now", "no longer", or
"here" once the code has moved). Why the code is as it is belongs, whether a
constraint it works around or an alternative it rejected; a narrative of
earlier versions belongs in the commit message. Where history carries a
reason, keep the reason and state it in the present tense: "raises rather
than ignoring `None`, which hid an accidental `None`", not "used to be a
no-op".

**Exception: `# type: ignore[...]` and `# pyright: ignore[...]`.** Each
checker applies a trailing suppression only to the line it sits on, so it
must trail the line the checker reports — usually the `def`, but mypy
reports `override` on an overloaded method at its first `@overload`. A
misplaced ignore leaves the error standing and is itself reported unused.
Keep these two forms trailing.

**Exception: version pins.** A pin's `# X.Y.Z` (`uses: …@<SHA> # v7.0.1`,
or the `phx-adr` pins in Commands) trails the line it pins, because
Renovate reads the version from that line. Keep these trailing too.

`# noinspection` comments stay leading, and unlike the forms above have
no checker behind them: when you change or remove the code one covers (the
next statement, or a whole function or class when it sits above one),
re-check that it still applies, and delete it if not.

## Language and Style

- NZ English; incorporate Te Reo Māori where natural (e.g. "mahi", "kaupapa")
- Use "Initialises" not "Initializes"

## Branches

- `main` — releases only; merge from `develop` via PR
- `develop` — main development branch
- Feature branches off `develop` for all new work

## Git Worktrees

Use the `using-git-worktrees` skill; it creates worktrees via the native `EnterWorktree` tool under `.claude/worktrees/` (gitignored). Don't hand-roll `git worktree add` when the native tool is available. Keep `.claude/` a real directory (only `.claude/skills` and `.claude/rules` are symlinks, into `.agents/`) — the native tool refuses to run if `.claude` itself is a symlink.

After creating a worktree, install its pre-commit hook (see the autohooks activate command in Commands). A fresh worktree has no per-worktree hooks directory, so create it first:

```bash
mkdir -p "$(git rev-parse --git-dir)/hooks"
```
