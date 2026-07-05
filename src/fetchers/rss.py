import xml.etree.ElementTree as ET
from typing import Dict, List

from src.http import fetch_text
from src.models import Item
from src.textutil import clean_html, truncate
from src.timeutil import parse_date, within_days


ATOM_NS = "{http://www.w3.org/2005/Atom}"


def _text(node, names):
    for name in names:
        found = node.find(name)
        if found is not None and found.text:
            return found.text.strip()
    return ""


def _link(node) -> str:
    link = _text(node, ["link"])
    if link:
        return link
    for found in node.findall(f"{ATOM_NS}link"):
        href = found.attrib.get("href")
        if href:
            return href
    return ""


def fetch_rss(config: Dict[str, object]) -> List[Item]:
    fresh_days = int(config["profile"].get("fresh_days", 7))
    items: List[Item] = []
    for source in config["sources"].get("rss", []):
        try:
            raw = fetch_text(source["url"])
            root = ET.fromstring(raw)
        except Exception as exc:
            items.append(
                Item(
                    title=f"RSS source failed: {source['name']}",
                    url=source["url"],
                    source="system",
                    kind="error",
                    summary=str(exc),
                    score=-100,
                )
            )
            continue

        nodes = root.findall(".//item") or root.findall(f".//{ATOM_NS}entry")
        for node in nodes:
            title = _text(node, ["title", f"{ATOM_NS}title"])
            url = _link(node)
            summary = _text(node, ["description", "summary", f"{ATOM_NS}summary", f"{ATOM_NS}content"])
            summary = clean_html(summary)
            if source["name"].startswith("Hacker News") and "Article URL:" in summary:
                summary = ""
            published = _text(node, ["pubDate", "published", "updated", f"{ATOM_NS}published", f"{ATOM_NS}updated"])
            published_at = parse_date(published)
            if not title or not url or not within_days(published_at, fresh_days):
                continue
            item = Item(
                title=clean_html(title),
                url=url,
                source=source["name"],
                kind="rss",
                summary=truncate(summary, 500),
                published_at=published_at,
                meta={"source_weight": source.get("source_weight", 1)},
            )
            items.append(item)
    return items
