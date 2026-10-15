"""Minimal WebSub callback and delivery inspector."""
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import PlainTextResponse
from xml.etree import ElementTree as ET

app = FastAPI(title="PodcastRelay Subscriber")
DELIVERIES: list[dict] = []


@app.get("/callback")
def verify(
    request: Request,
):
    params = request.query_params
    if params.get("hub.mode") not in {"subscribe", "unsubscribe"}:
        raise HTTPException(400, "Unknown mode")
    if not params.get("hub.topic") or not params.get("hub.challenge"):
        raise HTTPException(400, "Missing verification fields")
    return PlainTextResponse(params["hub.challenge"])


@app.post("/callback", status_code=204)
async def receive(request: Request):
    payload = await request.body()
    if len(payload) > 1_000_000:
        raise HTTPException(413, "Feed too large")
    try:
        root = ET.fromstring(payload)
        if root.tag != "rss":
            raise ValueError("Not an RSS document")
    except (ET.ParseError, ValueError) as exc:
        raise HTTPException(400, "Invalid RSS") from exc
    DELIVERIES.append({
        "titles": [node.text for node in root.findall("./channel/item/title")],
        "bytes": len(payload),
    })


@app.get("/deliveries")
def deliveries():
    return DELIVERIES
