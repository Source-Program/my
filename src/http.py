import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Dict, Optional


DEFAULT_TIMEOUT = 25
USER_AGENT = "AgentRadar/0.1 (+https://github.com/agent-radar)"


def fetch_text(url: str, headers: Optional[Dict[str, str]] = None, timeout: int = DEFAULT_TIMEOUT) -> str:
    req_headers = {"User-Agent": USER_AGENT}
    if headers:
        req_headers.update(headers)
    request = urllib.request.Request(url, headers=req_headers)
    with urllib.request.urlopen(request, timeout=timeout) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        return response.read().decode(charset, errors="replace")


def fetch_json(url: str, headers: Optional[Dict[str, str]] = None, timeout: int = DEFAULT_TIMEOUT):
    return json.loads(fetch_text(url, headers=headers, timeout=timeout))


def post_json(url: str, payload: Dict[str, object], headers: Optional[Dict[str, str]] = None, timeout: int = DEFAULT_TIMEOUT):
    req_headers = {"User-Agent": USER_AGENT, "Content-Type": "application/json"}
    if headers:
        req_headers.update(headers)
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(url, data=data, headers=req_headers, method="POST")
    with urllib.request.urlopen(request, timeout=timeout) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        return json.loads(response.read().decode(charset, errors="replace"))

