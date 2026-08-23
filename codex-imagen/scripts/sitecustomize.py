"""Add relay-compatible headers to the bundled imagegen child process."""

from __future__ import annotations

import base64
import os
from urllib.parse import urlsplit


DEFAULT_PROXY_URL = "socks5h://127.0.0.1:7897"


def _proxy_url() -> str:
    return (
        os.environ.get("CODEX_IMAGEN_PROXY_URL")
        or os.environ.get("CLASH_PROXY_URL")
        or DEFAULT_PROXY_URL
    )


def _download_image_urls(result):
    """Convert relay-hosted image URLs to b64_json for the bundled CLI."""
    try:
        import httpx2
    except ImportError:
        return result

    proxy = _proxy_url()
    with httpx2.Client(proxy=proxy, trust_env=False, follow_redirects=True, timeout=180) as client:
        for item in getattr(result, "data", []) or []:
            if getattr(item, "b64_json", None) or not getattr(item, "url", None):
                continue
            response = client.get(item.url)
            response.raise_for_status()
            item.b64_json = base64.b64encode(response.content).decode("ascii")
    return result


def _patch_image_resource(client):
    images = getattr(client, "images", None)
    if images is None or getattr(images, "_codex_imagen_patched", False):
        return
    for method_name in ("generate", "edit"):
        original = getattr(images, method_name, None)
        if original is None:
            continue

        def wrapped(*args, _original=original, **kwargs):
            return _download_image_urls(_original(*args, **kwargs))

        setattr(images, method_name, wrapped)
    images._codex_imagen_patched = True


def _patch_openai_client(name: str, user_agent: str) -> None:
    try:
        import openai
    except ImportError:
        return

    original = getattr(openai, name, None)
    if original is None or getattr(original, "_codex_imagen_patched", False):
        return

    def factory(*args, **kwargs):
        kwargs.setdefault("max_retries", 0)
        headers = dict(kwargs.get("default_headers") or {})
        headers["User-Agent"] = user_agent
        kwargs["default_headers"] = headers
        client = original(*args, **kwargs)
        _patch_image_resource(client)
        return client

    factory._codex_imagen_patched = True
    setattr(openai, name, factory)


user_agent = os.environ.get("CODEX_IMAGEN_USER_AGENT")
if user_agent:
    _patch_openai_client("OpenAI", user_agent)
    _patch_openai_client("AsyncOpenAI", user_agent)
