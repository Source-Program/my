from datetime import datetime
from typing import Dict, Iterable, List
from zoneinfo import ZoneInfo

from src.models import Item


def section_for(item: Item) -> str:
    if item.kind == "paper":
        return "研究快讯"
    return "今日快讯"


def render_digest(items: Iterable[Item], config: Dict[str, object]) -> str:
    items = list(items)
    tz_name = config["profile"].get("timezone", "Asia/Shanghai")
    today = datetime.now(ZoneInfo(tz_name)).strftime("%Y-%m-%d")
    title = config.get("render", {}).get("title", "Agent Radar")
    sections = config.get("render", {}).get("sections", [])
    grouped = {name: [] for name in sections}
    for item in items:
        grouped.setdefault(section_for(item), []).append(item)

    lines: List[str] = [f"{title} · {today}", ""]
    lead = "今天为你筛了 10 条 AI、科技生态和 Agent 开发相关的新闻/快讯。"
    lines.extend([lead, ""])
    if not items:
        lines.append("今天没有筛出新的高相关快讯。可以检查网络、放宽关键词，或使用 --include-seen 查看已推送内容。")
        return "\n".join(lines).strip()
    icons = {
        "今日快讯": "📰",
        "研究快讯": "📄",
    }
    for section in sections:
        bucket = grouped.get(section) or []
        if not bucket:
            continue
        lines.append(f"{icons.get(section, '•')} {section}")
        lines.append("")
        for idx, item in enumerate(bucket, 1):
            tags = f"#{' #'.join(t.replace(' ', '_') for t in item.tags[:4])}" if item.tags else ""
            lines.append(f"{idx}. {item.title}")
            if item.summary:
                lines.append(f"一句话：{item.summary}")
            if item.reason and item.reason != item.summary:
                lines.append(f"为什么值得读：{item.reason}")
            if tags:
                lines.append(f"标签：{tags}")
            lines.append(f"来源：{item.source}")
            lines.append(f"链接：{item.url}")
            lines.append("")
    return "\n".join(lines).strip()
