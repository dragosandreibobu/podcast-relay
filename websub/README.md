# Local WebSub demonstration

Start three terminals from the repository root after installing the project dependencies:

```bash
uvicorn websub.publisher.app:app --port 8000
uvicorn websub.hub.app:app --port 8001
uvicorn websub.subscriber.app:app --port 8002
```

Subscribe (hub verifies the callback with a challenge):

```bash
curl -X POST http://127.0.0.1:8001/hub \
  --data-urlencode 'hub.mode=subscribe' \
  --data-urlencode 'hub.topic=http://127.0.0.1:8000/feed.xml' \
  --data-urlencode 'hub.callback=http://127.0.0.1:8002/callback'
```

Publish an episode:

```bash
curl -X POST 'http://127.0.0.1:8000/episodes?title=Episode%20One&description=First%20episode&audio_url=https%3A%2F%2Fexample.org%2Fepisode.mp3'
```

Tell the hub that the feed changed:

```bash
curl -X POST http://127.0.0.1:8001/hub \
  --data-urlencode 'hub.mode=publish' \
  --data-urlencode 'hub.topic=http://127.0.0.1:8000/feed.xml'
curl http://127.0.0.1:8002/deliveries
```

This is a teaching prototype, **not a complete WebSub implementation**: publisher notifications are manual, the hub lacks lease expiration and authenticated delivery, and subscribers do not validate an HMAC signature. Do not deploy publicly.
