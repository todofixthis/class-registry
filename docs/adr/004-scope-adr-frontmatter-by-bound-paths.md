---
status: Accepted
date: 2026-08-29
scope: [docs/adr/, scripts/adr/generate_index.py]
summary: Replace ADR frontmatter's tags field with scope — the exact paths and directory prefixes a decision binds — validated by the index generator.
---

# 004: Scope ADR Frontmatter by the Paths a Decision Binds

## Context

ADRs 001–003 each carry a `tags` field: free-text keywords such as `typing`,
`api-design`, `registry-keys`. `tags` helps a reader who already suspects a
decision exists search for it, but gives no way to go the other direction —
from a file someone is editing back to the decisions governing it — since
keywords don't name locations.

[`phx:writing-adrs`][], this project's ADR skill (see `CLAUDE.md`), now
specifies a `scope` field instead: the exact files and directory prefixes
where a breach of the decision would be authored. It also specifies
frontmatter rules our generator (`scripts/adr/generate_index.py`) does not
yet enforce: `Archived` and `Superseded` each require a field naming why
(`archived-because`, `superseded-by`), and a `revisit-when` trigger can be
marked spent via `revisit-discharged-by`. A companion script in
`todofixthis/phx-claude-siat` — the skill's source repository — is the
canonical implementation of a generator enforcing this contract, including a
`--for <path>` mode that reports the decisions scoping a given path.

## Options

### Option 1: Do nothing — keep `tags`

Leave the three existing ADRs and the generator as they are.

**Pros:** No migration effort.
**Cons:** Diverges from `phx:writing-adrs`, so a new ADR written to the
skill's current spec won't validate against this repo's generator, and a
reviewer following the skill has to guess whether this repo is an
exception; keyword search is the only way to find a decision, so a
directory rename or file move can silently orphan an ADR's frontmatter.
**Risks:** The gap between skill and repo widens with every ADR added
under the old convention.

### Option 2: Rename `tags` to `scope`, without path or status validation

Migrate the field name and its values to paths, but skip the generator
checks that a scope entry still exists on disk, that `Archived`/`Superseded`
carry their required field, and that a `revisit-discharged-by` names a live
`revisit-when`.

**Pros:** Smaller diff to the generator than Option 3.
**Cons:** An unchecked `scope` rots the same way `tags` did — a moved file
silently drops out of coverage — and a status changed without its paired
field (e.g. `Archived` with no `archived-because`) passes silently, which is
exactly the drift `phx:writing-adrs` calls out as a real failure mode.
**Risks:** The field reads as validated, because the sibling fields are, and
that impression is false.

### Option 3: Rename `tags` to `scope`, with full validation (Accepted)

Migrate the field and port the canonical generator's checks: `scope` is
required (or explicitly `[]`), its entries must resolve to real paths (no
globs, directories need a trailing `/`), `Archived`/`Superseded` require
their paired field and no other status may carry it, and
`revisit-discharged-by` requires a `revisit-when` to spend. Add the `--for`
lookup mode.

**Pros:** Matches `phx:writing-adrs` exactly, including its failure modes —
a stale scope entry or an orphaned status field fails the pre-commit hook
instead of rotting unnoticed; `--for` answers "what governs this file?" for
an agent or reviewer who never thought to check `INDEX.md`.
**Cons:** Larger change to `scripts/adr/generate_index.py` than Option 2,
and requires authoring a `scope` for each existing ADR by reading what it
actually binds, rather than a mechanical rename.
**Risks:** An authored `scope` is a judgement call per ADR, not a lookup —
a `scope` drawn too narrow leaves the decision unreachable from files it
governs; too wide, and it stops meaning anything.

## Decision

Option 3. `phx:writing-adrs` is this project's standing convention for ADR
frontmatter (`CLAUDE.md`), so Option 1 leaves the project non-compliant with
its own tooling, and Option 2 keeps exactly the silent-drift problem the
skill's validation exists to catch — accepting stale metadata to save a
smaller diff isn't a real saving once the metadata is untrustworthy.

`scripts/adr/generate_index.py` now ports the canonical script's parsing and
validation rules — status vocabulary, the `archived-because`/`superseded-by`
pairing, the `revisit-when`/`revisit-discharged-by` pairing, `scope`
requiredness and path-existence checking, and `--for` — with one deliberate
difference: it keeps parsing frontmatter with PyYAML (already a dev
dependency here) rather than adopting the canonical script's hand-rolled,
stdlib-only line parser. That parser exists because
`todofixthis/phx-claude-siat` has no Python project root and cannot take a
PyYAML dependency; neither constraint applies to this repository, and a real
YAML parser has no truncation bug to guard against, so porting the
workaround would add complexity without a matching problem.

`scope` for each of ADRs 001–003 was authored by reading what each decision
actually binds, not derived mechanically from `tags`:

- ADR 001 (Python version support policy): `pyproject.toml` and
  `.github/workflows/build.yml` carry the supported-version declarations,
  and `src/class_registry/base.py` carries the `typing_extensions` import
  shim the policy requires.
- ADR 002 (default key type): `src/class_registry/base.py`, where the
  `KeyType` TypeVar's default is declared.
- ADR 003 (centralised TypeVars): `src/class_registry/`, since the
  decision binds every module in the package that could redefine a TypeVar
  instead of importing it from `base.py`.

## Consequences

- A new ADR must declare `scope` (or `scope: []`); the pre-commit hook and
  CI now reject one that still uses `tags`, is missing `scope`, or pairs a
  status with the wrong field.
- `uv run python scripts/adr/generate_index.py --for <path>` reports which
  ADRs bind a given file, for a contributor who never thought to check
  `INDEX.md`.
- `docs/adr/INDEX.md` gains a Scope column and drops Tags; a Revisit column
  surfaces any live `revisit-when` trigger.
- A future ADR that adds a fourth frontmatter field maintained by
  `phx:writing-adrs` should extend `scripts/adr/generate_index.py` to match,
  the same way this one did.

[`phx:writing-adrs`]: https://github.com/todofixthis/phx-claude-siat/blob/develop/skills/writing-adrs/SKILL.md
