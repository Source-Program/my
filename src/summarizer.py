import json
from typing import Dict, List

from src.config import env
from src.http import post_json
from src.models import Item
from src.ranking import fallback_summary


OPENAI_URL = "https://api.openai.com/v1/responses"


def maybe_llm_curate(items: List[Item], config: Dict[str, object]) -> List[Item]:
    api_key = env("OPENAI_API_KEY")
    if not api_key:
        for item in items:
            item.summary = fallback_summary(item)
        return items

    max_items = int(config["profile"].get("max_items", 12))
    payload_items = [
        {
            "title": item.title,
            "url": item.url,
            "source": item.source,
            "kind": item.kind,
            "summary": item.summary,
            "score": item.score,
            "tags": item.tags,
            "reason": item.reason,
            "meta": item.meta,
        }
        for item in items[: int(config["profile"].get("candidate_limit", 50))]
        if item.kind != "error"
    ]
    prompt = {
        "task": "为一个关注 AI、科技生态，并正在转向 Agent 开发的工程师筛选每日新闻/快讯列表。",
        "rules": [
            f"最多选择 {max_items} 条。",
            "覆盖 AI 模型、AI 产品、Agent、开发者工具、芯片/算力、机器人、AI 安全/监管、科技公司动态、AI 工程化。",
            "不要选择 GitHub 项目推荐，除非它来自新闻源且代表重要生态事件。",
            "降低纯融资、营销、泛泛新闻的优先级。",
            "输出 JSON，不要 markdown。",
            "每条保留原 url，summary 和 reason 必须全部使用简体中文，tags 3-5 个。",
            "summary 是一句话中文摘要，不要照搬英文原文。",
        ],
        "items": payload_items,
    }
    body = {
        "model": env("OPENAI_MODEL", "gpt-4.1-mini"),
        "input": [
            {
                "role": "system",
                "content": "你是一个严格的技术情报编辑，只输出可解析 JSON。",
            },
            {
                "role": "user",
                "content": json.dumps(prompt, ensure_ascii=False),
            },
        ],
        "text": {
            "format": {
                "type": "json_schema",
                "name": "agent_radar_digest",
                "schema": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "items": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "additionalProperties": False,
                                "properties": {
                                    "url": {"type": "string"},
                                    "summary": {"type": "string"},
                                    "reason": {"type": "string"},
                                    "tags": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                    },
                                },
                                "required": ["url", "summary", "reason", "tags"],
                            },
                        }
                    },
                    "required": ["items"],
                },
            }
        },
    }
    try:
        data = post_json(
            OPENAI_URL,
            body,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=60,
        )
        content = data["output"][0]["content"][0]["text"]
        result = json.loads(content)
    except Exception:
        for item in items[:max_items]:
            item.summary = fallback_summary(item)
        return items[:max_items]

    by_url = {item.url: item for item in items}
    curated: List[Item] = []
    for selected in result.get("items", []):
        item = by_url.get(selected.get("url"))
        if not item:
            continue
        item.summary = selected.get("summary") or fallback_summary(item)
        item.reason = selected.get("reason") or item.reason
        tags = selected.get("tags") or item.tags
        item.tags = list(dict.fromkeys([str(tag) for tag in tags]))[:6]
        curated.append(item)
        if len(curated) >= max_items:
            break
    if not curated:
        return items[:max_items]
    return curated
