---
paths:
  - "docs/**/*.rst"
---

# Admonitions in docs

Use an admonition only for an aside readers must spot before they act: one whose miss
costs them a failure or misbehaviour they would struggle to trace back, a risk to their
data or security, or behaviour confined to one environment that would leave a reader
there hunting for the cause. A harmless quirk, an optional feature and a shortcut all
stay prose. Admonitions lose their pull when every section has one, so give a section
(the content under its nearest heading) at most one; where two qualify, keep the
higher-consequence one as the admonition and write the other as prose.

Pick the type by consequence, taking the first that fits:

- `caution`: a risk to the reader's data or security.
- `warning`: the obvious approach fails or behaves wrongly.
- `note`: the environment-specific case that doesn't fail: behaviour differs in one
  setup (a platform, a Python version, a dependency's), surprising a reader there and
  no one else. One that fails is a `warning`.

Don't use any other admonition type.

Start the admonition with a bold line naming the case, so readers can judge from it
alone whether the admonition applies to them:

```rst
.. warning::

   **A relative** ``path`` **resolves against the working directory**

   Not against the config file's own directory, so …
```

RST can't nest inline markup, so a code span in that line sits between bold runs, as
above, not inside one: nested, it renders its backticks with no warning. Where a bold run
follows the code with no space, as in ``` ``FOO``\ **'s value** ```, separate them
with an escaped space (`\ `), or the build fails. A title that is all code stays an
unbolded literal.
