---
name: reflection
description: Use when the user asks to reflect, or at natural workflow endpoints (after user confirms work is done, before committing/PR creation) — reviews session for patterns of correction, instruction conflicts, and opportunities to improve the coding agent ecosystem
---

# Reflection

## Overview

Correct once, never again. Review the current session for friction — corrections, instruction conflicts, repetitive toil — and improve ecosystem files so future sessions run smoother.

## When to Trigger

- User asks explicitly (`/reflect`, "reflect on this session")
- Natural workflow endpoints: user confirms mahi is complete, requests commit/PR
- **Never** mid-workflow — wait until the current task is done

## Process

### Phase 1: Session Analysis

Review the conversation for five signal types:

| Signal | Example |
|--------|---------|
| **Corrections** | User repeatedly corrected same behaviour (e.g. `grep` → `rg`) |
| **Instruction conflicts** | Instructions say X but practice/codebase does Y |
| **Repetitive toil** | Same manual steps performed 2+ times — candidate for new skill/tool |
| **Reorganisation** | Information to reprioritise, deduplicate, or remove |
| **Stale content** | Instructions now handled by skills, or outdated patterns |

### Phase 2: Three-Stage Filter

| Stage | Criteria | Action |
|-------|----------|--------|
| **1 — Discard** | One-off corrections, typos, task-specific misunderstandings, already covered by existing instructions | Drop — list briefly in report for transparency |
| **2 — Ask user** | Patterns seen 2-3 times but potentially context-specific; new skill/tool candidates with unclear ROI | Include in report, ask user to confirm |
| **3 — Always include** | Repeated corrections (3+) on same topic; direct contradictions between instructions and practice; clear instruction gaps causing repeated friction | Include automatically |

### Phase 3: Scope Assignment

For each improvement passing the filter, assign the correct scope:

- **User-level** (`~/.claude/CLAUDE.md`, `~/.claude/skills/`): Personal preferences, cross-project patterns (e.g. NZ English, alphabetise collections)
- **Project-level** (`.claude/CLAUDE.md`, `.claude/skills/`): Project-specific conventions (e.g. Vitest over Jest, linter config)
- **Ambiguous**: Ask the user via AskUserQuestion

### AGENTS.md Signal-to-Noise Rule

AGENTS.md must only contain information that a coding agent **cannot** get from its training data or by reading the code. Before adding anything, ask: "Would a skilled developer discover this by exploring the repo?" If yes, don't add it. AGENTS.md is for project-specific surprises, traps, and non-obvious conventions — not general knowledge.

### Phase 4: Report and Execute

1. Read all instruction/ecosystem files that would be modified
2. Output the reflection report (format below)
3. Use AskUserQuestion for Stage 2 items and ambiguous scope
4. After user confirmation, make the changes
5. Summarise what was changed

## Report Format

```
## Session Reflection Report

### Automatic improvements (Stage 3)
- **[file]**: [change] — [evidence from session]

### Proposed improvements (Stage 2 — needs your input)
- **[file]**: [change] — [question for user]

### Discarded (Stage 1)
- [what was filtered and why]

### New skill/tool candidates
- [repetitive pattern] — [proposed skill name and purpose]
```

## Self-Improvement

User answers to Stage 2 questions calibrate future reflections. If the user consistently promotes or demotes a category of improvement, update this skill to encode that preference (e.g. "Tool preference corrections are always Stage 3").
