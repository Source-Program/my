import json
from pathlib import Path
from typing import Dict, Iterable, Set


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PATH = ROOT / "data" / "seen.json"


def load_seen(path: Path = DEFAULT_PATH) -> Set[str]:
    if not path.exists():
        return set()
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return set(data.get("urls", []))


def save_seen(urls: Iterable[str], path: Path = DEFAULT_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump({"urls": sorted(set(urls))}, f, ensure_ascii=False, indent=2)

