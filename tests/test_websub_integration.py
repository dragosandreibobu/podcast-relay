"""End-to-end WebSub tests using three real local HTTP servers."""
import contextlib
import socket
import subprocess
import sys
import time

import httpx
import pytest

TOPIC = "http://127.0.0.1:8000/feed.xml"
CALLBACK = "http://127.0.0.1:8002/callback"
HUB = "http://127.0.0.1:8001/hub"


@pytest.fixture
def services():
    ports = (8000, 8001, 8002)
    for port in ports:
        with socket.socket() as sock:
            try:
                sock.bind(("127.0.0.1", port))
            except OSError:
                pytest.skip(f"Demo port {port} occupied")
    processes = []
    try:
        for name, port in zip(("publisher", "hub", "subscriber"), ports):
            processes.append(subprocess.Popen(
                [sys.executable, "-m", "uvicorn", f"websub.{name}.app:app",
                 "--host", "127.0.0.1", "--port", str(port), "--log-level", "error"],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            ))
        with httpx.Client(trust_env=False) as client:
            for _ in range(80):
                if any(p.poll() is not None for p in processes):
                    pytest.fail("Service exited during startup")
                try:
                    if all(client.get(f"http://127.0.0.1:{port}/openapi.json", timeout=.3).status_code == 200 for port in ports):
                        break
                except httpx.HTTPError:
                    pass
                time.sleep(.1)
            else:
                pytest.fail("Services did not start")
        yield
    finally:
        for p in processes:
            p.terminate()
        for p in processes:
            with contextlib.suppress(subprocess.TimeoutExpired):
                p.wait(timeout=5)
            if p.poll() is None:
                p.kill()
                p.wait()


def test_subscribe_publish_unsubscribe(services):
    with httpx.Client(timeout=6, trust_env=False) as client:
        subscription = {"hub.mode": "subscribe", "hub.topic": TOPIC, "hub.callback": CALLBACK}
        assert client.post(HUB, data=subscription).status_code == 202
        assert client.post("http://127.0.0.1:8000/episodes", params={
            "title": "First Episode", "description": "A test",
            "audio_url": "https://example.org/first.mp3",
        }).status_code == 201
        result = client.post(HUB, data={"hub.mode": "publish", "hub.url": TOPIC})
        assert result.status_code == 200, result.text
        assert result.json()["delivered"] == 1
        deliveries = client.get("http://127.0.0.1:8002/deliveries").json()
        assert len(deliveries) == 1
        assert "First Episode" in deliveries[0]["titles"]
        assert client.post(HUB, data={**subscription, "hub.mode": "unsubscribe"}).status_code == 202
        assert client.post(HUB, data={"hub.mode": "publish", "hub.url": TOPIC}).json()["delivered"] == 0
        assert len(client.get("http://127.0.0.1:8002/deliveries").json()) == 1


def test_invalid_subscription_rejected(services):
    with httpx.Client(timeout=6, trust_env=False) as client:
        response = client.post(HUB, data={
            "hub.mode": "subscribe", "hub.topic": TOPIC,
            "hub.callback": "https://example.com/callback",
        })
        assert response.status_code == 400
