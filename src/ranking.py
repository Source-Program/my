from typing import Dict, Iterable, List

from src.models import Item
from src.textutil import truncate
from src.timeutil import now_utc


def dedupe(items: Iterable[Item]) -> List[Item]:
    seen = set()
    out: List[Item] = []
    for item in items:
        key = item.url.strip().lower() or item.title.strip().lower()
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(item)
    return out


def score_items(items: List[Item], config: Dict[str, object]) -> List[Item]:
    keywords = config.get("keywords", {})
    groups = [
        ("high", 9),
        ("medium", 5),
        ("low", 2),
    ]
    negative = [k.lower() for k in keywords.get("negative", [])]
    for item in items:
        if item.kind == "error":
            continue
        text = f"{item.title} {item.summary}".lower()
        score = float(item.meta.get("source_weight", 1))
        tags = []
        for group, weight in groups:
            for kw in keywords.get(group, []):
                needle = kw.lower()
                if needle in text:
                    score += weight
                    if len(tags) < 5:
                        tags.append(kw)
        for kw in negative:
            if kw in text:
                score -= 10
        if item.kind == "paper":
            score += 1
        if item.published_at:
            age_hours = max(1, (now_utc() - item.published_at).total_seconds() / 3600)
            score += max(0, 5 - age_hours / 24)
        item.score = round(score, 2)
        item.tags = list(dict.fromkeys(tags))[:6]
        item.reason = reason_for(item)
    return sorted(items, key=lambda x: x.score, reverse=True)


def reason_for(item: Item) -> str:
    if item.kind == "paper":
        return "研究快讯，适合快速判断是否代表 AI 技术或应用的新方向。"
    if "agent" in (item.title + item.summary).lower():
        return "和 Agent 应用开发相关，适合快速了解生态变化。"
    if item.tags:
        return f"命中了你的关注主题：{', '.join(item.tags[:4])}。"
    return "来源质量较高，适合快速了解 AI 或科技生态变化。"


def select_items(items: List[Item], config: Dict[str, object]) -> List[Item]:
    max_items = int(config["profile"].get("max_items", 10))
    max_per_source = int(config["profile"].get("max_per_source", 3))
    non_errors = [item for item in items if item.kind != "error" and item.score > 0]
    selected: List[Item] = []
    papers = [i for i in non_errors if i.kind == "paper"][:2]
    news = [i for i in non_errors if i.kind != "paper"]
    source_counts = {}
    for bucket in (news, papers):
        for item in bucket:
            if source_counts.get(item.source, 0) >= max_per_source:
                continue
            if item not in selected and len(selected) < max_items:
                selected.append(item)
                source_counts[item.source] = source_counts.get(item.source, 0) + 1
    for item in non_errors:
        if len(selected) >= max_items:
            break
        if item not in selected:
            selected.append(item)
    return selected


def fallback_summary(item: Item) -> str:
    tags = "、".join(item.tags[:3])
    if item.kind == "paper":
        if tags:
            return f"一篇关于 {tags} 的研究更新，适合快速判断是否值得继续阅读论文摘要。"
        return "一篇 AI 研究更新，适合快速判断是否代表新的技术方向。"
    if tags:
        return f"来自 {item.source} 的快讯，主题涉及 {tags}，值得关注它对 AI 与科技生态的影响。"
    return f"来自 {item.source} 的科技快讯，适合快速了解 AI 与技术生态的新变化。"
