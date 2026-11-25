---
status: Accepted
date: 2026-11-25
scope: [.agents/skills/, .autohooks/, .claude/settings.json, .github/workflows/build.yml, AGENTS.md, docs/adr/, pyproject.toml, renovate.json]
summary: "This project relies on the phx plugin for ADR tooling as cookiecutter-py ADR 019 decides for every generated project, with the adrs CI job and its Renovate-bumped pin as cookiecutter-py ADR 018 decides, restating neither here: never a repo-local generator, vendored copy of the tool or pre-commit hook running ADR tooling."
revisit-when: A cookiecutter-py release supersedes its ADR 018 or 019 with a decision that no longer covers plugin reliance or the adrs job; a condition in cookiecutter-py ADR 018's or 019's revisit-when arises in this project.
---

# 009: Defer ADR Tooling to cookiecutter-py

## Context

[ADR 007][] decided that this project indexes, validates and looks up ADRs
with the phx plugin's tool, never a repo-local one. [ADR 008][] deferred
other decisions to the copier template, but kept 007 in force with a revisit
condition: "a cookiecutter-py ADR decides reliance on the phx plugin, so 007
can give way to it".

That condition has fired. [cookiecutter-py ADR 019][], first released in
template 1.3.2, decides plugin reliance for the template and every generated
project, and [cookiecutter-py ADR 018][] decides the `adrs` CI job and its
pin. This project's `.copier-answers.yml` records 1.6.0, and the
template-owned AGENTS.md already cites both.

Compared in full, 007 decides nothing those two don't. Its decision, its
`scope`-not-`tags` convention and all three of its revisit conditions
reappear in 019, worded for every generated project; 019 also rejects a
pre-commit hook running the plugin's own tool, which 007 never weighed. Where
007 differs, the template has moved on: its pin is bumped by hand where
`renovate.json` now bumps it, its links pin phx-claude-siat 8.1.0 where the
pins name 9.1.0, and it says `adrs` is no required check where build.yml's
`gate`, which 018 makes the required check, now needs it.

## Options

### Option 1: Do nothing

**Cons:** Two records of one decision, in two repositories, and this
project's is already out of date.
**Risks:** A reader follows 007's hand-bump instruction, or trusts its claim
that a red `adrs` run blocks no merge.

### Option 2: Defer to cookiecutter-py ADRs 018 and 019 (Accepted)

Supersede 007 with this ADR, which names the template ADRs that hold the
decision.

**Cons:** 007's revisit conditions are watched only in cookiecutter-py's
index, which no one working here loads; one arising here first, such as ADRs
routinely authored outside Claude Code, reaches a reader of this project's
index only through this ADR's pointer to them. The reasoning lives in another
repository. This ADR names template ADRs by number, which goes stale if the
template supersedes or renumbers one.

### Option 3: Rewrite 007 to match the template

**Pros:** The reasoning stays readable here.
**Cons:** Every template change to ADR tooling needs a matching edit here,
which nothing prompts; 007 drifted that way once already.

## Decision

Option 2, for the reason 008 deferred 005 and 006: the template owns the
files that implement this decision, so it owns the decision. Nothing in 007
is this project's own, so nothing is restated here.

## Consequences

- [ADR 004][], superseded by 007, now resolves through 007 to this ADR.
- This ADR discharges 008's plugin-reliance condition; 008's other
  conditions stay live.
- Diverging from cookiecutter-py's ADR tooling on purpose needs an ADR here
  naming 019 or 018, as 008 requires of any template decision.
- 007's history, the ported generator that fought the plugin over the index,
  stays in 007 and in 019's Context.

[ADR 004]: 004-scope-adr-frontmatter-by-bound-paths.md
[ADR 007]: 007-rely-on-the-phx-plugin-for-adr-tooling.md
[ADR 008]: 008-defer-to-cookiecutter-py-s-template-decisions.md
[cookiecutter-py ADR 018]: https://github.com/todofixthis/cookiecutter-py/blob/1.6.0/docs/adr/018-require-gate-everywhere-and-the-release-check-on-main.md
[cookiecutter-py ADR 019]: https://github.com/todofixthis/cookiecutter-py/blob/1.6.0/docs/adr/019-rely-on-the-phx-plugin-for-adr-tooling.md
