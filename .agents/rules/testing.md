---
paths:
  - "**/test_*.py"
---

# Testing conventions

## Every test function carries a one-line docstring naming the scenario

The function name says what is called; the docstring says what must hold, in one
sentence on one line. Write the sentence a reviewer would need to judge whether the
assertion is the right one — not a restatement of the call.
