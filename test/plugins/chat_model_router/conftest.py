from __future__ import annotations

import sys
from pathlib import Path


def _project_root() -> Path:
    """向上查找包含 pyproject.toml 的项目根目录。"""
    current = Path(__file__).resolve().parent
    for parent in current.parents:
        if (parent / "pyproject.toml").is_file():
            return parent
    return current.parents[0]


PROJECT_ROOT = _project_root()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
