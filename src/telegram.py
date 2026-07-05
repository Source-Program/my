from typing import List

from src.config import env
from src.http import post_json


TELEGRAM_LIMIT = 3900


def split_message(text: str, limit: int = TELEGRAM_LIMIT) -> List[str]:
    if len(text) <= limit:
        return [text]
    chunks: List[str] = []
    current: List[str] = []
    size = 0
    for block in text.split("\n\n"):
        add = len(block) + 2
        if current and size + add > limit:
            chunks.append("\n\n".join(current))
            current = [block]
            size = add
        else:
            current.append(block)
            size += add
    if current:
        chunks.append("\n\n".join(current))
    return chunks


def send_telegram(text: str) -> None:
    token = env("TELEGRAM_BOT_TOKEN")
    chat_id = env("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        raise RuntimeError("Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID")
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    chunks = split_message(text)
    for idx, chunk in enumerate(chunks, 1):
        suffix = f"\n\n({idx}/{len(chunks)})" if len(chunks) > 1 else ""
        post_json(
            url,
            {
                "chat_id": chat_id,
                "text": chunk + suffix,
                "disable_web_page_preview": True,
            },
        )

