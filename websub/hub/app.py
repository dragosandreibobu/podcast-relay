"""Local-only educational WebSub hub (not for public deployment)."""
from __future__ import annotations

import secrets
from urllib.parse import urlsplit

import httpx
from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import PlainTextResponse

app = FastAPI(title="PodcastRelay WebSub Hub")
# topic -> callback -> secret. Memory-only for a deterministic classroom demo.
SUBSCRIPTIONS: dict[str, dict[str, str]] = {}


def local_url(value: str) -> bool:
    """Restrict outbound HTTP to loopback in this demonstration."""
    try:
        parts = urlsplit(value)
        return parts.scheme == "http" and parts.hostname in {"127.0.0.1", "localhost"} and parts.port is not None and not parts.username and not parts.password
    except ValueError:
        return False


@app.post("/hub")
async def hub(
    hub_mode: str = Form(alias="hub.mode"),
    hub_topic: str = Form(alias="hub.topic"),
    hub_callback: str | None = Form(default=None, alias="hub.callback"),
):
    if not local_url(hub_topic):
        raise HTTPException(400, "Demo supports only loopback topic URLs")
    if hub_mode == "publish":
        async with httpx.AsyncClient(timeout=5, follow_redirects=False, trust_env=False) as client:
            feed = await client.get(hub_topic)
            feed.raise_for_status()
            delivered = 0
            for callback in list(SUBSCRIPTIONS.get(hub_topic, {})):
                try:
                    response = await client.post(callback, content=feed.content, headers={"content-type": "application/rss+xml"})
                    response.raise_for_status()
                    delivered += 1
                except httpx.HTTPError:
                    pass
        return {"delivered": delivered}
    if hub_mode not in {"subscribe", "unsubscribe"} or not hub_callback or not local_url(hub_callback):
        raise HTTPException(400, "Invalid subscription request")
    challenge = secrets.token_urlsafe(24)
    params = {"hub.mode": hub_mode, "hub.topic": hub_topic, "hub.challenge": challenge}
    if hub_mode == "subscribe":
        params["hub.lease_seconds"] = "3600"
    try:
        async with httpx.AsyncClient(timeout=5, follow_redirects=False, trust_env=False) as client:
            response = await client.get(hub_callback, params=params)
        if response.status_code != 200 or response.text != challenge:
            raise HTTPException(409, "Callback verification failed")
    except httpx.HTTPError as exc:
        raise HTTPException(409, "Callback unavailable") from exc
    if hub_mode == "subscribe":
        SUBSCRIPTIONS.setdefault(hub_topic, {})[hub_callback] = ""
    else:
        SUBSCRIPTIONS.get(hub_topic, {}).pop(hub_callback, None)
    return PlainTextResponse("verified", status_code=202)
