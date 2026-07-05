from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional


@dataclass
class Item:
    title: str
    url: str
    source: str
    kind: str
    summary: str = ""
    published_at: Optional[datetime] = None
    score: float = 0.0
    tags: List[str] = field(default_factory=list)
    reason: str = ""
    meta: Dict[str, object] = field(default_factory=dict)

