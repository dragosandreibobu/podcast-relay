"""Minimal RSS 2.0 publisher. WebSub hub integration comes next."""
from datetime import datetime, timezone
from email.utils import format_datetime
from xml.etree import ElementTree as ET

from fastapi import FastAPI, Request
from fastapi.responses import Response

app = FastAPI(title="PodcastRelay Publisher")
EPISODES: list[dict[str, str]] = []


@app.get("/")
def index():
    return {"service": "PodcastRelay publisher", "feed": "/feed.xml", "episodes": len(EPISODES)}


@app.post("/episodes", status_code=201)
def publish_episode(title: str, description: str, audio_url: str):
    """Educational endpoint; do not expose publicly without authentication."""
    episode = {
        "id": str(len(EPISODES) + 1),
        "title": title,
        "description": description,
        "audio_url": audio_url,
        "published": format_datetime(datetime.now(timezone.utc)),
    }
    EPISODES.append(episode)
    return episode


@app.get("/feed.xml")
def feed(request: Request):
    root = ET.Element("rss", version="2.0")
    channel = ET.SubElement(root, "channel")
    for tag, value in (
        ("title", "PodcastRelay Demo"),
        ("link", str(request.base_url)),
        ("description", "A sample podcast feed for WebSub experiments"),
    ):
        ET.SubElement(channel, tag).text = value
    for episode in reversed(EPISODES):
        item = ET.SubElement(channel, "item")
        for tag, value in (
            ("title", episode["title"]),
            ("description", episode["description"]),
            ("guid", f"podcast-relay:episode:{episode['id']}"),
            ("pubDate", episode["published"]),
        ):
            ET.SubElement(item, tag).text = value
        ET.SubElement(item, "enclosure", url=episode["audio_url"], type="audio/mpeg", length="0")
    return Response(ET.tostring(root, encoding="utf-8", xml_declaration=True), media_type="application/rss+xml")
