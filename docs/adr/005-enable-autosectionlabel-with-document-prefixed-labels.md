---
status: Accepted
date: 2026-09-10
scope: [docs/]
summary: Enable sphinx.ext.autosectionlabel with autosectionlabel_prefix_document = True, not its default unprefixed labels.
revisit-when: The section titles that currently collide with autosectionlabel's default unprefixed names (list in Context) are all renamed or removed, so prefixing no longer earns its verbosity.
---

# 005: Enable autosectionlabel with Document-Prefixed Labels

## Context

Only one section in the docs is currently reachable by `:ref:` —
`overriding-lookup-keys`, cited from [`upgrading_to_v6.rst`][] — and it needs
a hand-placed `.. _overriding-lookup-keys:` anchor above its heading to work.
[`autosectionlabel`][] removes that step: it registers a label for every
section automatically, from the section's own title.

Whether that label is the bare title or the title prefixed with the
document's name is a real choice, not a formality. Built with the bare
(default) form, [`index.rst`][] produces two `duplicate label` warnings:

- `ClassRegistry`, from [`index.rst`][] against itself — the file opens with
  a `ClassRegistry` heading purely to hold the top-level `toctree`, then
  repeats the same heading immediately below it to introduce the actual
  page content.
- `getting started`, from [`index.rst`][]'s "Getting Started" subsection
  against the document title of [`getting_started.rst`][].

`.readthedocs.yaml` sets `fail_on_warning: true`, and `CLAUDE.md` states the
same policy for this project, so either warning breaks the published build.

## Options

### Option 1: Do nothing

**Pros:** No risk of introducing the warnings above.
**Cons:** Every section a future page wants to cross-reference still needs
its own hand-placed anchor, the way `overriding-lookup-keys` does today —
`autosectionlabel` exists precisely to remove that step.

### Option 2: Enable with default (unprefixed) labels

**Pros:** A label is just the section title, so an author who already knows
the heading can guess the `:ref:` target without checking.
**Cons:** Verified by building the docs with the extension enabled — this
breaks the build immediately on the two collisions described in Context.
**Risks:** A future document choosing a title that already exists elsewhere
(e.g. another "Getting Started" section) reintroduces the same failure,
with no warning until someone builds the docs.

### Option 3: Enable with `autosectionlabel_prefix_document = True` (Accepted)

**Pros:** Verified by building the docs with this setting — it resolves the
"getting started" collision, since the two labels become
`index:Getting Started` and `getting_started:Getting Started`. It leaves
`overriding-lookup-keys` untouched, since prefixing only applies to labels
`autosectionlabel` generates, not to hand-placed anchors.
**Cons:** A `:ref:` target now needs the document name as well as the
title, which is more to type and to get right than a bare title. It also
couples the target to the document's filename stem, so renaming an `.rst`
file silently breaks every `:ref:` built on its old prefix, with nothing
catching the break until the next docs build.
**Risks:** Prefixing disambiguates *across* documents, not within one, so
it does nothing for the `ClassRegistry`-against-itself collision — that one
is a documentation bug regardless of which option is chosen here.

## Decision

Option 3. Prefixing is what keeps the build green against a same-titled
heading in a different document — the actual failure mode measured here —
without disturbing `overriding-lookup-keys`, the one hand-placed anchor the
docs already depend on.

The `ClassRegistry`-against-itself collision that Option 3 leaves standing
is fixed directly: [`index.rst`][] drops its second, redundant
`ClassRegistry` heading, so the `toctree` and the introductory prose share
the page's one title instead of each opening their own.

## Consequences

- **This decision does not guard against two sections sharing an identical
  title *within the same document*** — prefixing disambiguates across
  documents, not within one, so that case still produces a `duplicate label`
  warning. [`index.rst`][]'s instance is fixed by this ADR; a future
  document must avoid repeating a heading for the same reason.
- `docs/conf.py` gains `sphinx.ext.autosectionlabel` and
  `autosectionlabel_prefix_document = True`.
- Every section is now reachable via `` :ref:`\<docname\>:\<Section Title\>` ``
  without adding an anchor — e.g. `` :ref:`getting_started:Typed Registries` ``
  — while `overriding-lookup-keys` keeps working exactly as before.
- Renaming an `.rst` file changes every prefixed label it generates, so any
  `:ref:` built on its old filename stem breaks silently until the next
  docs build.

[`getting_started.rst`]: ../getting_started.rst
[`index.rst`]: ../index.rst
[`autosectionlabel`]: https://www.sphinx-doc.org/en/master/usage/extensions/autosectionlabel.html
[`upgrading_to_v6.rst`]: ../upgrading_to_v6.rst
