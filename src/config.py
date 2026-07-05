import json
import os
from pathlib import Path
from typing import Any, Dict


ROOT = Path(__file__).resolve().parents[1]


def load_config(path: str = "config.json") -> Dict[str, Any]:
    config_path = Path(path)
    if not config_path.is_absolute():
        config_path = ROOT / config_path
    with config_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def env(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()

