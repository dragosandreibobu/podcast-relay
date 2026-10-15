# PodcastRelay

A small podcast publishing and distribution lab comparing **WebSub** and **ActivityPub**, built for a WADe presentation on 22 October 2026.

## Objective

Publish a sample podcast episode and inspect how independent applications receive it through two different web protocols:

- **WebSub:** RSS publisher → hub → verified subscriber callbacks.
- **ActivityPub:** federated podcast actors exchanging ActivityStreams activities through inboxes and outboxes.

WebSub is a content-update delivery mechanism; ActivityPub is a federation and social interaction protocol. They are not interchangeable.

## Planned demonstrations

1. Publish a podcast RSS 2.0 feed with episode metadata and an audio enclosure.
2. Subscribe a listener service to the feed through a WebSub hub, complete callback challenge verification, then deliver a new episode notification.
3. Exchange a podcast episode announcement between two independent ActivityPub actors.
4. Inspect the actual HTTP requests, responses and payloads side by side.

## Implementation plan

- Python / FastAPI for small HTTP services
- RSS 2.0 XML and ActivityStreams JSON-LD
- pytest for protocol tests
- Minimal HTML interface for the live demo
- No database until persistence becomes necessary

See [architecture and acceptance criteria](docs/architecture.md).

## References

- [W3C WebSub](https://www.w3.org/TR/websub/)
- [W3C ActivityPub](https://www.w3.org/TR/activitypub/)
- [RSS 2.0 specification](https://www.rssboard.org/rss-specification)

## Status

Architecture initialized; executable services are not yet implemented.
