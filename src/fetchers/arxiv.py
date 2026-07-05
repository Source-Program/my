import urllib.parse
import xml.etree.ElementTree as ET
from typing import Dict, List

from src.http import fetch_text
from src.models import Item
from src.textutil import clean_html, truncate
from src.timeutil import parse_date, within_days


ATOM = "{http://www.w3.org/2005/Atom}"


def fetch_arxiv(config: Dict[str, object]) -> List[Item]:
    arxiv_cfg = config["sources"].get("arxiv", {})
    max_results = int(arxiv_cfg.get("max_results", 20))
    fresh_days = int(config["profile"].get("fresh_days", 7))
    items: List[Item] = []
    for query in arxiv_cfg.get("queries", []):
        params = urllib.parse.urlencode(
            {
                "search_query": query,
                "start": "0",
                "max_results": str(max_results),
                "sortBy": "submittedDate",
                "sortOrder": "descending",
            }
        )
        url = f"https://export.arxiv.org/api/query?{params}"
        try:
            root = ET.fromstring(fetch_text(url))
        except Exception as exc:
            items.append(
                Item(
                    title=f"arXiv query failed: {query}",
                    url="https://arxiv.org",
                    source="system",
                    kind="error",
                    summary=str(exc),
                    score=-100,
                )
            )
            continue
        for entry in root.findall(f"{ATOM}entry"):
            title = clean_html((entry.findtext(f"{ATOM}title") or "").replace("\n", " "))
            summary = clean_html(entry.findtext(f"{ATOM}summary") or "")
            published_at = parse_date(entry.findtext(f"{ATOM}published") or "")
            if not title or not within_days(published_at, fresh_days):
                continue
            link = ""
            for node in entry.findall(f"{ATOM}link"):
                if node.attrib.get("type") == "text/html":
                    link = node.attrib.get("href", "")
                    break
                if not link:
                    link = node.attrib.get("href", "")
            items.append(
                Item(
                    title=title,
                    url=link,
                    source="arXiv",
                    kind="paper",
                    summary=truncate(summary, 650),
                    published_at=published_at,
                    meta={"query": query},
                )
            )
    return items

