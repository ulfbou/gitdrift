"""Private import support for release-evidence tests."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).parents[1]
ACCEPTANCE = ROOT / "scripts" / "acceptance"
if str(ACCEPTANCE) not in sys.path:
    sys.path.insert(0, str(ACCEPTANCE))
