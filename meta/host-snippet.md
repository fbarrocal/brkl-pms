<!-- kb-host-snippet v1 — managed block: injected into the host project's CLAUDE.md by this KB's setup skill. Edit the copy in the KB's meta/host-snippet.md, not the injected block; lint checks the two stay in sync. -->
## Knowledge base

A self-governing knowledge base lives in `kb/` — its rulebook is `kb/CLAUDE.md`, and that rulebook applies to everything under `kb/`.

- **Feed it:** drop raw material into `kb/sources/`, then ask to ingest it.
- **Consume it:** ask questions of it — answers come from its query procedure, grounded in its pages. Never edit `kb/content/` directly.
- The KB manages its own files. Treat `kb/` as self-contained: `sources/` is its inlet, answers are its outlet.
<!-- /kb-host-snippet -->
