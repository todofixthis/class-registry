"""Autohooks plugin: regenerate ADR index when ADR files are staged."""

import re
import sys
from pathlib import Path
from typing import Optional

from autohooks.api import ok
from autohooks.api.git import get_staged_status, stage_files
from autohooks.config import Config
from autohooks.precommit.run import ReportProgress

# Add project root to sys.path so scripts.adr.generate_index is importable
_PROJECT_ROOT = Path(__file__).parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from scripts.adr.generate_index import INDEX_FILE, generate  # noqa: E402

RE_STAGED_ADR = re.compile(r"docs/adr/[0-9]+-.*\.md$")


def precommit(
    config: Optional[Config] = None,
    report_progress: Optional[ReportProgress] = None,
    **kwargs: object,
) -> int:
    """Regenerate ADR index when ADR files are staged."""
    staged = [f for f in get_staged_status() if RE_STAGED_ADR.search(str(f.path))]

    if not staged:
        ok("No staged ADR files.")
        return 0

    result = generate()
    if result == 0:
        stage_files([INDEX_FILE])
        ok("Generated ADR index.")
    return result
