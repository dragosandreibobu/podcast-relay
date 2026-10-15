from xml.etree import ElementTree as ET

from fastapi.testclient import TestClient
from websub.publisher.app import EPISODES, app


def test_rss_publisher():
    EPISODES.clear()
    client = TestClient(app)
    created = client.post(
        "/episodes",
        params={
            "title": "Episode One",
            "description": "First sample",
            "audio_url": "https://example.org/episode-one.mp3",
        },
    )
    assert created.status_code == 201
    feed = client.get("/feed.xml")
    assert feed.status_code == 200
    root = ET.fromstring(feed.content)
    assert root.tag == "rss"
    item = root.find("./channel/item")
    assert item is not None
    assert item.findtext("title") == "Episode One"
    assert item.find("enclosure").attrib["url"] == "https://example.org/episode-one.mp3"
