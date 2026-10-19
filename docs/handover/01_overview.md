# 01 — Overview

## The goal

Build a **knowledge management system that runs entirely on Claude** (no external apps, no database, no embeddings), where plain markdown files are the source of truth and Claude acts as both the **curator** (authors and maintains the knowledge) and the **query engine** (answers questions by reading and traversing the files). The end product is a **reusable template**: drop the folder anywhere, point Cowork (or Claude Code) at it, and it configures itself to whatever the KB is about.

## How we got here (research foundation)

The project started as research into **LLM-powered personal knowledge management (PKM)**. The relevant conclusions that shaped the design:

- **~16 approaches were surveyed**, spanning off-the-shelf apps (Notion AI, Mem, Reflect, NotebookLM), local plugin stacks (Obsidian + Smart Connections / Copilot, Khoj, AnythingLLM + Ollama), custom RAG builds, GraphRAG pipelines (LightRAG, Microsoft GraphRAG, Cognee, Graphiti), and interface-layer approaches (CLI+agent, MCP servers). The recurring lesson: **the bottleneck in PKM is maintenance overhead, not storage** — the approaches that win remove upkeep rather than adding clever retrieval.

- **Vector vs. graph retrieval.** Vector retrieval finds what is *similar* (points in embedding space, nearest neighbours); graph retrieval finds what is *connected* (typed, labelled edges you can traverse). Vector wins single-hop/detail lookups; graph wins multi-hop "how does all this connect" questions. The user chose **graph**.

- **Graph tool landscape.** The strongest md-first, local options were **LightRAG** (lightweight typed graph + vectors, files stay canonical, graph is a rebuildable index) and **Cognee** (local-first typed-graph memory engine). **Karpathy's "LLM Wiki" pattern** was the strongest *curator* model but its "graph" is untyped `[[wikilinks]]` — not a real typed graph.

- **The pivotal turn:** the user wanted *both* a powerful curator *and* a real typed graph, entirely on Claude. No single external tool does both. The resolution was to stop treating them as competitors and realise that **when Claude is both curator and query engine, the graph can simply *be* the markdown**: store typed edges as frontmatter fields, and Claude traverses them by reading. This removes the external graph store, the drift between "prose says X / graph says Y", and the second pipeline — the curator's output *is* the graph.

## What it became

A self-contained folder with:

- **`sources/`** — an inbox of immutable source material (drop things here).
- **`content/`** — flat folder of Claude-authored **node pages**; each is simultaneously a *catalog* entry (typed frontmatter fields + edges) and a *wiki* page (synthesised prose).
- **`meta/`** — the machinery: the navigation `index.md`, the operation `skills/` (setup, ingest, query, lint), and optional node `templates/`.
- **`CLAUDE.md`** — a **static rulebook**, identical across every KB.
- **`SETTINGS.md`** — the **only per-KB mutable rules file**: this KB's purpose, node types, edge predicates, and setup state.
- **`README.md`** — human onboarding (Cowork + Claude Code).

Retrieval is **navigation, not vector search**: Claude reads the index and traverses typed frontmatter edges. Because edges are plain frontmatter, the same files are readable by Obsidian's graph, Dataview, Breadcrumbs, Juggl, and Graph Link Types — with no plugin required by the template itself.

## Two tools, one folder

The system is designed to be operated primarily through **Claude Cowork** (chat-first, no terminal, scheduled tasks for upkeep) and, on the same folder, **Claude Code** (for Git and heavy batch jobs). Both read the same `CLAUDE.md`; each keeps its session state separately; the files are the shared canonical layer. The one rule: don't run both on the folder simultaneously.

## Important non-goals / caveats

- **Not local / not private-by-default.** Running on Claude sends note *contents* to Anthropic; the *files* stay on the user's disk. For a true air-gap, a local-model GraphRAG tool (e.g. LightRAG on Ollama) is the alternative.
- **It has a ceiling.** The navigation-based design is comfortable to ~150–200 pages / ~50–100k tokens of content; past that, an external indexed store becomes worth adding.
