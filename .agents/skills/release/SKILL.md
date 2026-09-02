---
name: release
description: Use when preparing or publishing a new release of class-registry — covers release notes, version bump, build, PyPI upload, and GitHub release creation
---
# Release

## Phase 1 — Research & draft (before touching any files)

### 1. Gather changes since last release
```bash
gh release list --limit 1 --json tagName --jq '.[0].tagName'   # find last release tag
git log <last-tag>..HEAD --oneline                              # all commits since
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
Using the commit list, PR descriptions, and issue context, draft the release notes following the _Writing Release Notes_ guide below. When a bullet relates to a GitHub issue, prefix it with `[#number]`. Run the `nz-english` skill on the draft, then present it to the developer for review and incorporate feedback before proceeding.

### 4. Recommend version number
Based on the changes, recommend a semver bump:
- **major** — breaking changes
- **minor** — new features or behaviour changes, fully backwards-compatible
- **patch** — bug fixes only

### 5. Gate: breaking changes require a migration guide
A **breaking change** is anything that makes previously-working code fail — at runtime, or under a type checker. Undocumented behaviour someone relied on still counts; "only a couple of users" measures blast radius, not compatibility. If this release has none, skip to the stop below.

**First, settle the version.** Step 4 defines minor and patch as *fully backwards-compatible*, so a breaking change in anything but a major contradicts it. When that happens, stop and put it to the developer: bump to major, or keep the smaller bump and record why in an ADR. Neither pick it for them nor draft around it — the answer decides which guide the rest of this step is about, and a release drafted for one version and linked to another ships broken.

**Then the guide.** One guide per major line, `docs/upgrading_to_v<major>.rst` — never a per-minor page. `<major>` is the major being released, or, for a break shipped in a minor or patch, the major line it lands on.

It must:
- **cover *this* release's breaking change.** A guide left over from an earlier release satisfies nothing — its existence is what makes this the easy check to fake. A break shipped in 6.3.0 gets its own section in `upgrading_to_v6.rst`, headed by the version that introduced it.
- exist, be listed in the `docs/index.rst` toctree, and be linked from the upgrade-alert listing in **both** `docs/index.rst` and `README.rst` — the two carry the same listing and drift apart easily. The link syntax differs by file: `docs/index.rst` uses a Sphinx `:doc:` role targeting `upgrading_to_v<major>`; `README.rst` uses a relative link to the source, `` `Upgrading to ClassRegistry v<major> <docs/upgrading_to_v<major>.rst>`_ `` — the `:doc:` role renders as raw text on GitHub, where the README is read.
- follow _Writing a Migration Guide_ below.

**If any of that is missing, the release stops here** — write it first.

Release notes do not satisfy this gate. They are read once, by people who already know a release happened; the guide is what someone finds months later when their code breaks and they don't yet know why.

```bash
ls docs/upgrading_to_v<major>.rst                        # exists
rg 'upgrading_to_v<major>' docs/index.rst README.rst     # index: toctree + alert; README: alert
uv run make -C docs clean && uv run make -C docs html    # builds, and it isn't orphaned
```
Then read the guide and confirm it covers this release's break. No command checks that for you.

**Stop here. Get explicit confirmation of the release notes and version number before continuing.**

---

## Phase 2 — Publish (after confirmation)

### 6. Bump version on `develop`
```bash
uv version <version>
```
This updates `pyproject.toml` and re-locks `uv.lock` in one step. Commit both files and push to `develop`.

### 7. Open release PR
```bash
gh pr create --base main --title "Release v<version>" --body-file release-<version>.md
```
**Stop here. Wait for the user to confirm the PR is merged before continuing.**

### 8. Switch to `main`
```bash
git checkout main && git pull
```

### 9. Build
```bash
uv sync --group=dev
rm -rf dist
uv build
```
Sync first — pulling `main` may have brought in dependency changes. Artefacts
land in `dist/`. Nothing under `dist/` is tracked, so removing the whole
directory is safe — and necessary: under zsh `rm -f dist/*` aborts with `no
matches found` when `dist/` is empty or absent, and otherwise skips uv's
`.gitignore`. `uv build` recreates both.

### 10. Tag and push
```bash
git tag -a <version> -m "Release <version>"
git push origin <version>
```
`<version>` must match `pyproject.toml`.

### 11. Create GitHub release

**a. Append checksums to the release notes file:**
```bash
shasum -a 256 dist/phx_class_registry-* >> release-<version>.md
```

**b. GPG-sign the document and each build artefact:**
```bash
GPG_KEY=$(git config user.email)
gpg --local-user "$GPG_KEY" --clearsign release-<version>.md   # → release-<version>.md.asc
for f in dist/phx_class_registry-*; do gpg --local-user "$GPG_KEY" --detach-sign "$f"; done
# Creates dist/phx_class_registry-*.sig alongside each artefact
```

**c. Build the release body** — concatenate the notes and the signed copy:
```
<contents of release-<version>.md>

---

````
<contents of release-<version>.md.asc>
````
```
Write this to `release-<version>-body.md`.

**d. Create the release and upload all artefacts:**
```bash
gh release create <version> dist/* \
  --title "ClassRegistry v<version>" \
  --notes-file release-<version>-body.md
```
`dist/*` picks up the `.whl`, `.tar.gz`, and `.sig` files.

### 12. Upload to PyPI
```bash
# Publishes only if the keyring can supply the token
keyring get https://upload.pypi.org/legacy/ __token__ >/dev/null 2>&1 && \
  uv publish --username __token__
```
The token comes from the developer's keyring: `[tool.uv]` in `pyproject.toml`
sets `keyring-provider = "subprocess"`, so uv shells out to a `keyring`
executable on `PATH`. Run the check first — it exits non-zero when the keyring
cannot supply the token, and prints nothing either way. Never echo the token to
confirm it; that puts a live credential in the transcript.

**If the check fails, stop here** and ask the developer to set
`UV_PUBLISH_TOKEN` (which takes precedence over the keyring) and run the publish
themselves. You cannot export it into their shell, and discovering this by
running the upload means failing the release's one irreversible step.

### 13. Clean up
```bash
rm -f release-<version>.md release-<version>.md.asc release-<version>-body.md
rm -rf dist
git checkout develop && git pull
```
`-f` so a re-run does not fail on a file already removed. `dist` goes too — its
artefacts and `.sig` files are on the GitHub release and PyPI by now. To correct
a release afterwards, fetch those assets back with `gh release download
<version>`: a rebuilt wheel may not be byte-identical, so its checksums would
disagree with the published notes.

### 14. Close related GitHub issues
For every issue referenced in the release notes, close it with a comment:
```bash
gh issue close <number> --comment "Implemented in [v<version>](https://github.com/todofixthis/class-registry/releases/tag/<version>)."
```

### 15. Rebase `develop` onto `main`
```bash
git rebase origin/main
git push
```
Because `develop` now contains all of `main`'s commits, the histories no longer diverge and a regular (non-force) push succeeds.

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
>
> Full migration guide: [Upgrading to ClassRegistry v{major}](https://class-registry.readthedocs.io/en/latest/upgrading_to_v{major}.html)

## New features
## Enhancements
## Bug fixes

> [!NOTE]
> **Verifying release artefacts**
> 1. Import the signing key: `curl https://github.com/todofixthis.gpg | gpg --import`
> 2. Download the `.whl` or `.tar.gz` and its matching `.sig` file from the release assets
> 3. Verify: `gpg --verify phx_class_registry-<version>-py3-none-any.whl.sig phx_class_registry-<version>-py3-none-any.whl`
>
> Key fingerprint: `457997A2A506270F918D7BD1925CC6E316680401`

# SHA256 Checksums
```

Only include the `[!WARNING]` block if there are breaking changes — but when it is present, the migration guide link is **required**, not optional. Omit any section that has no entries.

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
>
> Full migration guide: [Upgrading to ClassRegistry v6](https://class-registry.readthedocs.io/en/latest/upgrading_to_v6.html)
```

---

## Writing a Migration Guide

`docs/upgrading_to_v<major>.rst`, modelled on the existing `upgrading_to_v6.rst`. It stays unreachable until wired into three slots: the `docs/index.rst` toctree, and the upgrade-alert listing in **both** `docs/index.rst` and `README.rst`. The two listings (one bullet per major upgrade) drift apart easily — add the bullet to each, or the README goes stale. Their link syntax differs: `docs/index.rst` uses a Sphinx `:doc:` role targeting `upgrading_to_v<major>`; `README.rst` uses a relative link to the source, `` `Upgrading to ClassRegistry v<major> <docs/upgrading_to_v<major>.rst>`_ `` — `:doc:` renders as raw text on GitHub, where the README is read.

One page covers a whole major line: the move onto it, and any break shipped later within it. Say so in the opening paragraph — someone already on v6 has no reason to guess that "Upgrading to ClassRegistry v6" is where a 6.3.0 break is written down. Breaks after the major boundary get their own `Changes in v<version>` section; the major boundary itself is the page's main content.

Write for someone who upgraded, hit an error, and does not yet know a release caused it. They arrive by searching the error text — not by reading release notes.

Each breaking change needs four things:

1. **What changed**, in terms of what the developer wrote, not what the internals do.
2. **The error they'll actually see** — copy it verbatim from the tool. Never paraphrase a compiler; they match on this text.
3. **The fix**, as code.
4. **Whether runtime behaviour changed.** If it didn't, say so plainly and early — it converts a panic into a chore.

Then add what the fix leads them into next:

- **Second-order traps.** A fix that lands people in a subtler failure needs that failure documented beside it, with its error text.
- **Facts stranded in ADRs.** ADRs are not in the toctree and readers never see them. If an ADR holds the only explanation of something a migrating developer needs, the guide is where it goes.

Verify every code sample and every error message by running it. Prose that merely sounds right is the recurring failure in this repo's documentation, and a migration guide is the worst place for it — its readers are already stuck.

Before wiring the guide in, run two passes over the draft:

### Audience-surrogate review

Dispatch one subagent on the main model (a reasoning task, not a cheap one), given only the draft and cast as the reader above. It must resolve its problem from the guide alone and flag every place it stays stuck: an error string it can't match verbatim against what a tool emits, a fix it can't apply without knowledge the guide assumes, unexplained jargon, a missing second-order trap or stranded-ADR fact. Address the feedback before continuing.

### Conciseness pass

Tighten the reviewed draft: cut repetition, merge overlapping fixes, drop hedging and prose that restates a code sample. The surrogate review optimises for completeness and leaves the draft longer than it needs to be, so weigh each addition and keep only what earns its place. Never trim two things for length: **verbatim error text and code fixes** — readers match on them — and any **migration step**. Then, since this repo uses NZ English, run `phx:nz-english` over the result.
