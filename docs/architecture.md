# PodcastRelay architecture

## Boundaries

Keep the first implementation small and independently testable:

```text
                   WebSub
Podcast publisher ---> Hub ---> Subscriber callback
     |                 ^                |
     +---- RSS feed ---+--- fetch ------+

                  ActivityPub
Podcast actor A (outbox) ---> Actor B (inbox)
           |                       |
           +--- actor discovery ---+
```

## WebSub lifecycle

1. Publisher serves an RSS feed containing `rel=hub` and `rel=self` discovery links.
2. Subscriber sends `hub.mode=subscribe`, `hub.topic`, and `hub.callback` to the hub.
3. Hub performs the required GET challenge verification against the callback before accepting the subscription.
4. Publisher signals `hub.mode=publish` with its topic URL.
5. Hub fetches the topic and POSTs the content to verified callbacks.
6. Subscriber records and displays the delivery.

Include unsubscribe, lease handling, request validation, safe outbound HTTP behavior, and idempotent processing in the implementation. Localhost-only demonstration endpoints must not be exposed as a public SSRF-capable hub.

## ActivityPub lifecycle

1. Serve actors with stable IDs, inbox and outbox URLs.
2. Represent episode announcements as ActivityStreams objects, e.g. `Create` containing a `Note` with a podcast episode URL.
3. Deliver activities between two distinct actor inboxes.
4. Record request and response bodies for inspection.

A local two-server demo is **not** proof of federation interoperability. Before claiming interoperability, implement and test HTTP signatures/authentication as appropriate, addressing, delivery retries, content negotiation, and relevant security constraints.

## Suggested layout

```text
podcast-relay/
  websub/
    publisher/
    hub/
    subscriber/
  activitypub/
    server/
  tests/
  docs/
```

Prefer FastAPI, Python standard-library XML facilities, and pytest. SQLite is optional until persistence is needed.

## Demo acceptance criteria

- A newly published podcast episode appears in the RSS feed.
- A verified WebSub subscription receives a real HTTP callback after publication.
- An unverified callback is never treated as subscribed.
- Two distinct ActivityPub actors exchange a valid ActivityStreams activity over HTTP.
- The presenter can explain and show each request, response, and payload.
