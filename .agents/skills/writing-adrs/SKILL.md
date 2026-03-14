---
name: writing-adrs
description: Use when making significant architectural, tooling, or design decisions that would benefit from documented rationale — before implementing the decision
---

# Writing Architecture Decision Records

ADRs record _why_ things are the way they are, so future contributors don't relitigate settled decisions. Use one when choosing between libraries, patterns, or conventions, or any time "why didn't we just use X?" is a likely future question.

## Format

File: `docs/adr/NNN-<slug>.md` (zero-padded, kebab-case)

```markdown
---
status: Accepted
date: YYYY-MM-DD
tags: [tag1, tag2, tag3]
summary: One sentence describing what was decided (not why).
---

# NNN: Title (Imperative Mood)

## Context

Why is this a problem? Why now? What forces are at play?

## Options

### Option 1: Do nothing

_Establishes the stakes — what happens if we decide nothing._

**Pros:** ...
**Cons:** ...
**Risks:** ...

### Option 2: [Chosen option] (Accepted)

**Pros:** ...
**Cons:** ...
**Risks:** ...

### Option 3: [Rejected alternative]

**Pros:** ...
**Cons:** ...
**Risks:** ...

## Decision

State the decision and summarise the key reasons.

## Consequences

What follows — positive and negative.
```

## Frontmatter Fields

- **`status`** — `Accepted`, `Deprecated`, or `Superseded`. Superseded ADRs are excluded from `docs/adr/INDEX.md` but remain in the repo for history.
- **`date`** — ISO date the ADR was written.
- **`tags`** — lowercase keywords an agent would use to locate this ADR (e.g. `[database, migrations, schema]`). Think: "what would I search for to find this decision?"
- **`summary`** — one sentence: what was decided, not why. This appears verbatim in the index.
- **`superseded-by`** — integer ADR number; omit unless status is `Superseded`.

## Conventions

- **Option 1 is always "Do nothing"** — sets the stakes
- **Option 2 is always the accepted option** — exception: for `Deprecated` ADRs, "Do nothing" (Option 1) is the accepted option, because the investigation concluded that no change was warranted. Rejected alternatives appear as Options 2, 3, etc. Trivial mitigations (e.g. adding a comment) are implementation details of the "do nothing" choice and do not warrant their own option.
- **Options must be mutually exclusive** — each must represent a fundamentally different approach. Test: could any two options be combined without contradiction? If yes, they aren't mutually exclusive. Two failure modes:
  - _Implementation details as options_ — if two options share the same core approach but differ in implementation, the variant belongs as a sub-heading within the parent option, not a top-level option
  - _Multi-dimensional problems_ — if what looks like a list of options is actually two separate decisions, structure around the primary; handle the secondary as a sub-question in the Decision section or write a follow-up ADR
- **Number sequentially** — never reuse or renumber
- **Supersede, don't edit** — new ADR for changed decisions; mark the old one superseded
- **Keep it concise** — enough to reconstruct the reasoning, not a thesis
- **Each section has a distinct job — don't let them overlap:**
  - _Context_ — the problem and forces; stop before proposing any remedy
  - _Options_ — approaches and trade-offs; don't restate what Context already said
  - _Decision_ — why this option over others; don't re-describe the chosen option (Options already did that)
  - _Consequences_ — what changes or must be managed downstream; not a restatement of the accepted option's pros/cons

## Supersession Workflow

When a new ADR overrides an existing one:

1. Write the new ADR referencing the old one in the Context section
2. In the **old** ADR, set `status: Superseded` and `superseded-by: NNN` (new ADR number)
3. Commit both files together

The index generator excludes superseded ADRs automatically — no manual index update needed.
