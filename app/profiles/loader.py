"""User profile loading utilities."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

DEFAULT_PROFILE_PATH = Path(__file__).resolve().parent / "default_user_profile.json"


def load_profile(path: Path = DEFAULT_PROFILE_PATH) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"User profile not found at {path}")
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)
