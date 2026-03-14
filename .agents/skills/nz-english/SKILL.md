---
name: nz-english
description: Use when scanning for or correcting US English spellings in a codebase — comments, docstrings, docs, and string literals, but not API identifiers.
---

# NZ English Conversion

Convert US English spellings to NZ English in human-readable text.

## Scope

**Convert:** comments, docstrings, `.rst`/`.md` docs, string literals, error messages, test function names.

**Do NOT convert:** public API identifiers (parameter names, method names, class names), external library identifiers, URLs. When prose describes a US-spelled API (e.g. `normalize=True`), convert the prose but leave the identifier.

## Substitutions

| US | NZ |
|----|----|
| `-ize` / `-ization` | `-ise` / `-isation` (normalise, initialise, serialise, parametrise) |
| `-or` endings | `-our` (colour, behaviour, honour, flavour, favourite) |
| `-er` endings (root words) | `-re` (centre, fibre, theatre) — not all `-er`; "filter" stays |
| `-og` endings | `-ogue` (catalogue, dialogue, analogue) |
| `-eled` / `-eling` | `-elled` / `-elling` (travelled, labelled, modelling) |
| `gray` | `grey` |
| `defense` / `offense` | `defence` / `offence` |
| `license` (noun) | `licence` |
| `practice` (verb) | `practise` |
| `program` | `programme` — not in computing contexts ("program code") |
| `initializer` | `initialiser` |
| `aluminum` / `artifact` / `aging` | `aluminium` / `artefact` / `ageing` |
| `fulfillment` / `enrollment` | `fulfilment` / `enrolment` |

## Search

Run across `.py`, `.rst`, and `.md` files — docs directories are easy to miss:

```
rg -in "ization|normaliz|initializ|recogniz|organiz|serializ|parametriz|quantiz"
rg -in "\bcolor\b|\bbehavior\b|\bhonor\b|\bflavor\b|\bfavorit"
rg -in "\bcenter\b|\bfiber\b|\btheater\b|\bliter\b|\bmeter\b"
rg -in "\bgray\b|\bdefense\b|\boffense\b|\baluminum\b|\bartifact\b"
rg -in "initializer|fulfillment|enrollment|aging\b|traveling|labeling"
```

## Triage

For each hit: **prose or API identifier?**

- In a function/class signature, or as `param=value` → **skip**
- Grep `src/` for the term — if it's a callable parameter or attribute → **skip**
- In a docstring, comment, or string literal → **convert**

A term can appear in both contexts in the same file — edit only the prose occurrences.

## Verify

Run the test suite after edits. Renamed test functions (e.g. `test_foo_normalisation`) are fine — they're internal.
