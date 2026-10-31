---
status: Accepted
date: 2026-10-31
scope: [.autohooks/, .readthedocs.yaml, docs/adr/, docs/conf.py, pyproject.toml]
summary: The template's ADRs 006 and 007 replace this project's ADRs 005 and 006, and its Python range comes from the template's recorded python_version answer rather than ADR 001; change one of these upstream in cookiecutter-py, or record a deliberate divergence here as an ADR naming the template ADR it departs from.
revisit-when: This project stops taking template updates; a cookiecutter-py ADR decides reliance on the phx plugin, so 007 can give way to it; the template supersedes or renumbers one of the ADRs named here; cookiecutter-py stops being readable to this project's readers.
---

# 008: Defer to cookiecutter-py's Template Decisions

## Context

This project now takes its tooling from [cookiecutter-py's copier template][],
recorded in `.copier-answers.yml`, and each template release arrives as a
Renovate PR running `copier update` ([cookiecutter-py ADR 008][]). The files
copier writes are template-owned: `.agents/rules/template-owned.md` lists them.

Several of this project's ADRs decided things the template now decides for
every library, in files it now owns:

- [005-enable-autosectionlabel-with-document-prefixed-labels.md][] sets
  `autosectionlabel_prefix_document` in `docs/conf.py`, as
  [cookiecutter-py ADR 006][] does.
- [006-check-the-docs-build-in-the-pre-commit-hook.md][] adds the `docs_build`
  autohooks plugin, as [cookiecutter-py ADR 007][] does.
- [001-support-three-most-recent-python-releases.md][] sets the supported
  range in `pyproject.toml` and the CI matrix. The template now sets both from
  its recorded `python_version` answer (cookiecutter-py ADR 008).

005 and 006 are archived on comments in those files. The template rewrote
those comments to cite its own ADRs, so the defence each names now points
elsewhere.

[007-rely-on-the-phx-plugin-for-adr-tooling.md][] overlaps the template only
in part: [cookiecutter-py ADR 009][] decides the CI job and its pin, but no
template ADR decides 007's core, relying on the phx plugin rather than a
repo-local or vendored tool.

## Options

### Option 1: Do nothing

**Pros:** No change to the record.
**Cons:** Two ADRs name a defence that no longer cites them, and each decision
has two records, in two repositories, that can drift apart.
**Risks:** A reader acts on this project's copy after the template's has moved
on.

### Option 2: Defer to the template's ADRs (Accepted)

Supersede 005 and 006 with this ADR, which names the template ADRs that now
hold each decision, and record which part of 001 the template now sets.

**Pros:** Each decision has one record, beside the file that implements it.
**Cons:** A reader follows a link to another repository to read the reasoning.
This ADR names template ADRs by number, which goes stale if the template
supersedes or renumbers one; the links pin the 1.1.0 tag, so they still lead to
the decision this project adopted.

### Option 3: Keep this project's ADRs and update them

Rewrite 005 and 006's `archived-because`, and keep both in force alongside the
template's ADRs.

**Pros:** The reasoning stays readable in this repository.
**Cons:** Every template change to one of these decisions needs a matching edit
here, which nothing prompts.

## Decision

Option 2. The template owns these files, so it owns the decisions about them;
a second copy here can only fall behind.

001 stays in force, since only its range clause moved: the range is set by
re-answering `python_version` through copier, never by hand, and 001's
backport of newer typing features through `typing_extensions` is this
project's own. 007 stays in force too, until a template ADR decides plugin
reliance.

005's `revisit-when` named this project's own colliding section titles. It does
not carry over: cookiecutter-py ADR 006 is template-wide, and its trigger asks
both that collisions occurred, which class-registry's docs already show, and
that prefixing proved not worth its verbosity.

## Consequences

- A change right for every generated project starts in cookiecutter-py, under
  its ADRs. A change right for this project only follows
  `.agents/rules/template-owned.md`.
- Diverging from a template decision on purpose needs its own ADR here, naming
  the template ADR it departs from.

[001-support-three-most-recent-python-releases.md]: 001-support-three-most-recent-python-releases.md
[005-enable-autosectionlabel-with-document-prefixed-labels.md]: 005-enable-autosectionlabel-with-document-prefixed-labels.md
[006-check-the-docs-build-in-the-pre-commit-hook.md]: 006-check-the-docs-build-in-the-pre-commit-hook.md
[007-rely-on-the-phx-plugin-for-adr-tooling.md]: 007-rely-on-the-phx-plugin-for-adr-tooling.md
[cookiecutter-py ADR 006]: https://github.com/todofixthis/cookiecutter-py/blob/1.1.0/docs/adr/006-enable-autosectionlabel-with-document-prefixed-labels.md
[cookiecutter-py ADR 007]: https://github.com/todofixthis/cookiecutter-py/blob/1.1.0/docs/adr/007-check-the-docs-build-in-the-pre-commit-hook.md
[cookiecutter-py ADR 008]: https://github.com/todofixthis/cookiecutter-py/blob/1.1.0/docs/adr/008-propagate-template-changes-with-copier-and-renovate.md
[cookiecutter-py ADR 009]: https://github.com/todofixthis/cookiecutter-py/blob/1.1.0/docs/adr/009-gate-adr-ci-and-the-phx-pin.md
[cookiecutter-py's copier template]: https://github.com/todofixthis/cookiecutter-py
