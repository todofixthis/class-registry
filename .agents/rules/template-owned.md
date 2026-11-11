---
paths:
  - ".agents/rules/template-owned.md"
  - ".agents/rules/testing.md"
  - ".agents/skills/release/SKILL.md"
  - ".agents/skills/rotate-python-versions/SKILL.md"
  - ".autohooks/docs_build.py"
  - ".claude/rules/template-owned.md"
  - ".claude/rules/testing.md"
  - ".claude/settings.json"
  - ".claude/skills/release/SKILL.md"
  - ".claude/skills/rotate-python-versions/SKILL.md"
  - ".copier-answers.yml"
  - ".github/workflows/build.yml"
  - ".gitignore"
  - ".readthedocs.yaml"
  - "AGENTS.md"
  - "CLAUDE.md"
  - "LICENCE.txt"
  - "docs/Makefile"
  - "docs/conf.py"
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

Before changing any other listed file, ask whether the change would be right
for every project generated from the template. If it would, don't make it
here: stop and tell the maintainer, giving the change as a proposal for the
same file under cookiecutter-py's `template/` directory (where it may carry a
`.jinja` suffix). This list already answers whether the file is template-owned,
so don't go looking for cookiecutter-py to check; open the PR there yourself
only if this session already has it checked out. If this project can't wait
for the release,
stop and ask the maintainer rather than editing here: a hand copy that
differs from the released change turns the next update PR into a merge
conflict.

If the change is right for this project only, make it here. A rule for this
project goes in `.agents/rules/project.md`, never in a templated rules file;
an extra CI job goes in its own workflow file.

To resolve a conflict in a template-update PR, keep this project's
project-only changes and take the template's side for everything else,
including any hand copy of a change the template has now released. Where
both sides changed the same line for reasons of their own, ask the
maintainer. Never resolve a conflict by moving a project rule back into a
templated file.
