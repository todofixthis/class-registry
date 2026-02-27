---
name: creative-commits
description: Use when creating Git commits — produces distinctive emoji-adorned commit messages with creative visual metaphors
---
# Creative Commits
Craft Git commits with distinctive, metaphorical emoji and concise messages.
## Rules
- Title <= 50 chars, emoji at **end** of title line
- **Title must be concrete** — plain-English description of the change; metaphor belongs only in the emoji, not the title (e.g. "Add shared path aliases" not "Lay the foundation stones")
- Commit via HEREDOC with three parts separated by blank lines: title, body, co-authored-by
- Use `uv run git commit` — autohooks requires the virtualenv to be active; run `git status` sequentially after
## Commit Body
Bullet the logical changes — what shifted and why. No file paths or function names; keep it conceptual.
- Group related changes into a single bullet
- Scale to the commit: 1 bullet for trivial, 3–5 for larger changes; omit body for self-evident changes
- Each bullet: change, then rationale (e.g. "Add X so Y" / "Remove X to Y")
### Example
```
Add path aliases and strict compiler options 🧱
- Add shared path aliases so imports stay clean across packages
- Set strict compiler options to catch errors at build time
Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
```
## Emoji Selection
Emphasise the **human story** behind each change — why someone made it, who it serves, what it enables — not just what changed mechanically.
### Process
1. Read full diff — grasp the high-level change
2. Ask: what **human intent or impact** does this change represent?
3. Translate that intent into a **concrete, everyday human scene** — a specific moment, action, or feeling a person might recognise (e.g. "someone quietly rearranging furniture before guests arrive", "a chef tasting and adjusting just before serving"). The more vivid and grounded the scene, the better.
4. Brainstorm 5–8 emoji that capture *that scene* rather than the commit directly — favour oblique, lateral choices; if candidates feel obvious, reframe the scene itself
5. Run each candidate through the three-stage filter:
| Stage | Verdict | Action |
|-------|---------|--------|
| **Too safe** — predictable, cliché, category-label (🐛 for bug, 📝 for docs, ✨ for feature), or literal echo of a word already in the message (🪧 for "signpost", 🗺️ for "roadmap") | Drop | Always discard |
| **Just right** — novel yet tells a clear story linking back to the commit's theme | Accept | Keep |
| **Too weird** — abstract, opaque, requires explanation to connect to the change | Drop | Always discard |
6. From accepted candidates, pick the one with the strongest narrative link to the commit
- **Never** reuse an emoji from the last 25 commits
- Avoid building a personal repertoire; each commit should feel like a fresh creative act
### Examples
| Message | Emoji | Why |
|---------|-------|-----|
| Add release changelog | 📣 | Someone announcing news to people, not just listing items |
| Hybrid background script | 🌉 | Bridge connects two worlds — emphasises unifying intent |
| NZ English convention | 🥝 | Cultural identity of the people behind the convention |
| Refine agent docs | 🪥 | Morning-routine care — someone tidying things for others |
| Rich-text clipboard plan | 🦎 | Adapting to surroundings like a person reading the room |
**Goal:** Git log reads like a human narrative — each emoji reflects intent, care, and craft rather than category.
