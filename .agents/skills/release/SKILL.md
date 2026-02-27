---
name: release
description: Use when preparing or publishing a new release of class-registry — covers release notes, version bump, build, PyPI upload, and GitHub release creation
---
# Release

## Phase 1 — Research & draft (before touching any files)

### 1. Gather changes since last release
```bash
git describe --tags --abbrev=0          # find last release tag
git log <last-tag>..HEAD --oneline      # all commits since
```

### 2. Look up PR and issue context
For every merge commit, extract the PR number and fetch its description:
```bash
git log <last-tag>..HEAD --oneline --merges
gh pr view <number> --json title,body,labels
```

For every `#<number>` reference in commit messages, fetch the issue:
```bash
gh issue view <number> --json title,body,labels
```

### 3. Draft release notes
Using the commit list, PR descriptions, and issue context, draft the release notes following the _Writing Release Notes_ guide below. Present the draft to the developer for review and incorporate feedback before proceeding.

### 4. Recommend version number
Based on the changes, recommend a semver bump:
- **major** — breaking changes
- **minor** — new features or behaviour changes, fully backwards-compatible
- **patch** — bug fixes only

**Stop here. Get explicit confirmation of the release notes and version number before continuing.**

---

## Phase 2 — Publish (after confirmation)

### 5. Bump version on `develop`
```bash
uv version <version>
```
This updates `pyproject.toml` and re-locks `uv.lock` in one step. Commit both files and push to `develop`.

### 6. Open release PR
```bash
gh pr create --base main --title "Release v<version>" --body-file release-<version>.md
```
**Stop here. Wait for the user to confirm the PR is merged before continuing.**

### 7. Switch to `main`
```bash
git checkout main && git pull
```

### 8. Build
```bash
rm -f dist/*
uv build
```
Artefacts land in `dist/`.

### 9. Tag and push
```bash
git tag -a <version> -m "Release <version>"
git push origin <version>
```
`<version>` must match `pyproject.toml`.

### 10. Create GitHub release

**a. Append checksums to the release notes file:**
```bash
sha256sum dist/phx_class_registry-* >> release-<version>.md
```

**b. GPG-sign the document:**
```bash
gpg --clearsign release-<version>.md   # → release-<version>.md.asc
```

**c. Sign each build artefact:**
```bash
for f in dist/phx_class_registry-*; do gpg --detach-sign "$f"; done
# Creates dist/phx_class_registry-*.sig alongside each artefact
```

**d. Build the release body** — concatenate the notes and the signed copy:
```
<contents of release-<version>.md>

---

````
<contents of release-<version>.md.asc>
````
```
Write this to `release-<version>-body.md`.

**e. Create the release and upload all artefacts:**
```bash
gh release create <version> dist/* \
  --title "ClassRegistry v<version>" \
  --notes-file release-<version>-body.md
```
`dist/*` picks up the `.whl`, `.tar.gz`, and `.sig` files.

### 11. Upload to PyPI
```bash
uv publish --username __token__
```

### 12. Clean up
```bash
rm release-<version>.md release-<version>.md.asc release-<version>-body.md
```

---

## Writing Release Notes

### Structure
```markdown
# ClassRegistry v<version>
<one-sentence summary of the release character>

> [!WARNING]
> **Breaking changes**
> - {what changed}
>   - {migration instructions}
>   - {error you'll see if you don't migrate}

## New features
## Enhancements
## Bug fixes

# SHA256 Checksums
```

Only include the `[!WARNING]` block if there are breaking changes. Omit any section that has no entries.

### Grouping related items
- **2–4 related bullets:** nest as a hierarchical sublist under the parent bullet
- **5+ related bullets:** promote to a `###` subheading within the section

### Content filter

**Always include**
- New capabilities developers can use
- Architectural decisions
- Behaviour changes
- Breaking changes

**Usually omit**
- Technical details of how something works internally
- Configuration consolidation (unless it changes developer-facing behaviour)
- Code organisation changes
- Dependency updates (include only if resolving a critical or high-severity vulnerability)
- Improvements to coding agent instructions

**Always omit**
- Formatting, linting, minor refactoring
- Test coverage updates

### Breaking changes alert
```markdown
> [!WARNING]
> **Breaking changes**
> - `SomeClass.old_method()` removed
>   - Replace with `SomeClass.new_method()`
>   - You'll know you need to migrate if you see: `AttributeError: 'SomeClass' object has no attribute 'old_method'`
```
