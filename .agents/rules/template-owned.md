---
paths:
  - ".agents/rules/docs-admonitions.md"
  - ".agents/rules/template-owned.md"
  - ".agents/rules/testing.md"
  - ".agents/skills/release/SKILL.md"
  - ".agents/skills/rotate-python-versions/SKILL.md"
  - ".autohooks/docs_build.py"
  - ".claude/rules/docs-admonitions.md"
  - ".claude/rules/template-owned.md"
  - ".claude/rules/testing.md"
  - ".claude/settings.json"
  - ".claude/skills/release/SKILL.md"
  - ".claude/skills/rotate-python-versions/SKILL.md"
  - ".copier-answers.yml"
  - ".github/workflows/build.yml"
  - ".github/workflows/python-policy.yml"
  - ".gitignore"
  - ".readthedocs.yaml"
  - "AGENTS.md"
  - "CLAUDE.md"
  - "LICENCE.txt"
  - "docs/Makefile"
  - "docs/conf.py"
  - "infra/github/main.tf"
  - "pyproject.toml"
  - "renovate.json"
  - "src/class_registry/py.typed"
---


# Template-owned files

Every file in this rule's `paths:` list comes from the copier template
`todofixthis/cookiecutter-py`, which `.copier-answers.yml` records. Each
template release reaches this project as a Renovate PR running
`copier update`, which merges the release into those files.

The template also writes seed files for this project to replace:

- `README.rst`
- `docs/adr/INDEX.md`
- `docs/api.rst`
- `docs/index.rst`
- `src/class_registry/__init__.py`
- `test/__init__.py`
- `test/test_placeholder.py`

Change those freely. copier still merges template changes into them, so a
release that edits a seed can conflict.

A value derived from a copier answer, such as the supported Python range,
changes by re-answering with `copier update --data`, as the
`rotate-python-versions` skill does: never by hand, and never upstream.

Before changing any other listed file, ask whether the reason for the change
depends on something specific to this project: its code, the dependencies it
added itself (not the template's tooling, such as pytest, ruff or mypy), or
its users. Answer from this project alone; don't go looking for
cookiecutter-py.

If it does, make the change here. A rule for this project goes in
`.agents/rules/project.md`, never in a templated rules file; an extra CI job
goes in `.github/workflows/project.yml`, which build.yml calls and `gate`
requires, so the job blocks merges. `project.md` and `project.yml` are this
project's own, written once by the template.

If it doesn't, the change is a template candidate, however local the symptom
that brought it up: a fix for a problem any generated project could hit is a
candidate even when only this one has hit it. Don't make it here: stop and
tell the person you're working with, giving the change as a proposal for the
same file under cookiecutter-py's `template/` directory (where it may carry a
`.jinja` suffix). Open the PR there yourself only if this session already has
it checked out.

Make a candidate here only when the rest of the task can't proceed without it
(the candidate is a step towards the task, not the task itself), or when the
person you're working with asks for it here knowing it's a candidate. Keep it
to what the task needs, and list each such file under a "Template candidates"
heading, with the reason: in the PR description, or in the commit message when
there's no PR. If you leave the change uncommitted, put the list in your
report and ask the person you're working with to carry it into the commit
message. The template's maintainer is then asked to port the committed
change upstream verbatim, placement included, so the release makes the same
change and the next update PR merges cleanly.

To resolve a conflict in a template-update PR, keep this project's
project-only changes and take the template's side for everything else,
including any hand copy of a change the template has now released. Where
both sides changed the same line for reasons of their own, ask the
maintainer. Never resolve a conflict by moving a project rule back into a
templated file.
