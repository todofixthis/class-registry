"""Autohooks plugin: build the docs when a docs-affecting file is staged."""

import subprocess
import sys
from pathlib import Path
from typing import Optional

from autohooks.api import error, ok, out
from autohooks.api.git import get_staged_status
from autohooks.api.path import match
from autohooks.config import Config
from autohooks.precommit.run import ReportProgress

_PROJECT_ROOT = Path(__file__).parent.parent
_DOCS_DIR = _PROJECT_ROOT / "docs"
# A dedicated directory, not docs/_build/html, so this doesn't race a
# concurrent `make html` in another terminal.
_BUILD_DIR = _DOCS_DIR / "_build" / "precommit"
_BUILD_TIMEOUT_SECONDS = 120

# Docstrings under src/ are pulled into the built API page by autodoc (see
# docs/adr/006-check-the-docs-build-in-the-pre-commit-hook.md), so they can
# break the build the same way an .rst change can.
INCLUDE = ("docs/*.rst", "docs/conf.py", "src/*.py")


def precommit(
    config: Optional[Config] = None,
    report_progress: Optional[ReportProgress] = None,
    **kwargs: object,
) -> int:
    """Build the docs when a staged file could affect them."""
    staged = [f for f in get_staged_status() if match(f.path, INCLUDE)]

    if not staged:
        ok("No staged files affect the docs.")
        return 0

    cmd = [
        sys.executable,
        "-m",
        "sphinx",
        "-b",
        "html",
        "-W",
        "--keep-going",
        # Force a full re-read on every run: an unchanged file that a
        # previous build already read keeps whatever it registered then
        # (e.g. an autosectionlabel target), so a warning a *different*
        # file would now raise against it can go undetected without this
        # (see docs/adr/006-check-the-docs-build-in-the-pre-commit-hook.md).
        "-E",
        str(_DOCS_DIR),
        str(_BUILD_DIR),
    ]
    try:
        subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            cwd=_PROJECT_ROOT,
            timeout=_BUILD_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired:
        error(f"Docs build timed out after {_BUILD_TIMEOUT_SECONDS}s.")
        return 1
    except subprocess.CalledProcessError as e:
        error("Docs build failed:")
        output = e.stderr.decode(encoding=sys.getdefaultencoding(), errors="replace")
        for line in output.split("\n"):
            out(line)
        return e.returncode

    ok("Docs build succeeded.")
    return 0
