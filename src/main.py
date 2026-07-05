import argparse
from typing import List
from urllib.parse import urlparse

from src.config import ROOT, load_config
from src.fetchers.arxiv import fetch_arxiv
from src.fetchers.rss import fetch_rss
from src.models import Item
from src.ranking import dedupe, score_items, select_items
from src.render import render_digest
from src.storage import load_seen, save_seen
from src.summarizer import maybe_llm_curate
from src.telegram import send_telegram


def collect(config) -> List[Item]:
    items: List[Item] = []
    items.extend(fetch_rss(config))
    items.extend(fetch_arxiv(config))
    return items


def allowed_by_filters(item: Item, config) -> bool:
    domains = config.get("filters", {}).get("exclude_url_domains", [])
    host = (urlparse(item.url).netloc or "").lower()
    return not any(host == domain or host.endswith(f".{domain}") for domain in domains)


def run(dry_run: bool, include_seen: bool, config_path: str) -> str:
    config = load_config(config_path)
    seen = load_seen()
    items = dedupe(collect(config))
    items = [item for item in items if allowed_by_filters(item, config)]
    if not include_seen:
        items = [item for item in items if item.url not in seen]
    ranked = score_items(items, config)
    candidates = ranked[: int(config["profile"].get("candidate_limit", 50))]
    selected = select_items(candidates, config)
    selected = maybe_llm_curate(selected, config)
    digest = render_digest(selected, config)

    output_path = ROOT / "outputs" / "latest.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(digest + "\n", encoding="utf-8")

    if not dry_run:
        send_telegram(digest)
        save_seen(list(seen) + [item.url for item in selected])
    return digest


def main() -> None:
    parser = argparse.ArgumentParser(description="Agent Radar daily Telegram digest")
    parser.add_argument("--dry-run", action="store_true", help="Print digest without sending Telegram message")
    parser.add_argument("--include-seen", action="store_true", help="Do not filter previously sent URLs")
    parser.add_argument("--config", default="config.json", help="Path to config JSON")
    args = parser.parse_args()
    print(run(args.dry_run, args.include_seen, args.config))


if __name__ == "__main__":
    main()
