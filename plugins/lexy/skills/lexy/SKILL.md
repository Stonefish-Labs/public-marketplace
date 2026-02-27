---
name: lexy
description: >
  General-purpose knowledge base search skill. Point it at a data directory
  containing documents (markdown, text, YAML, JSON, CSV) and search using a
  multi-tier pipeline: exact match, BM25 ranked retrieval, and fuzzy matching.
  Use when you need to find information in a local document collection without
  external APIs or LLM inference. Trigger on requests like "search the knowledge
  base", "look up in the data", "find in documents", or "query the glossary".
metadata:
  author: Lexy Team
  version: 1.0.0
  category: search
  tags: ["search", "retrieval", "bm25", "fuzzy", "knowledge-base"]
---

# Lexy - Local Knowledge Base Search

Search a local document collection using a multi-tier pipeline (exact, BM25, fuzzy) with zero external API calls.

## Prerequisites

- [uv](https://docs.astral.sh/uv/) (handles Python dependencies automatically)

## Usage

All commands output JSON to stdout. Diagnostic messages go to stderr.

### Search

```bash
uv run ${SKILL_DIR}/scripts/lexy.py search "<query>" --data <data-dir> [--top N] [--mode all|exact|bm25|fuzzy]
```

### Build/Rebuild Index

```bash
uv run ${SKILL_DIR}/scripts/lexy.py index --data <data-dir> [--reindex]
```

### Info

```bash
uv run ${SKILL_DIR}/scripts/lexy.py info --data <data-dir>
```

## Instructions

### 1. Determine the Data Directory

The `--data` argument points to a directory of documents to search. Use `${SKILL_DIR}/data` for the bundled sample data, or any user-specified path. The directory is scanned recursively for supported files: `.md`, `.txt`, `.yaml`, `.yml`, `.json`, `.csv`.

### 2. Run a Search

Execute the search script with `uv run`. The first invocation indexes the data (cached for subsequent runs). Example:

```bash
uv run ${SKILL_DIR}/scripts/lexy.py search "authentication flow" --data /path/to/docs --top 5
```

### 3. Interpret Results

The output is a JSON object with a `results` array. Each result has:
- `content`: the matched chunk text
- `source`: the source file (relative to data dir)
- `section`: the section/header within the file
- `score`: relevance score normalized to 0-1
- `match_type`: one of `exact`, `bm25`, `fuzzy`, `fallback`

Present the most relevant results to the user, citing `source` and `section`.

### 4. Query Decomposition Strategy

For complex or multi-concept queries, decompose into sub-queries:

1. **Break apart compound questions** - "What is the relationship between X and Y?" becomes two searches: one for X, one for Y.
2. **Try specific terms first** - Search for precise keywords before broader phrases.
3. **Use fuzzy mode for uncertain spelling** - If a term might have typos or alternate forms, run with `--mode fuzzy`.
4. **Combine results** - Merge and deduplicate results from multiple searches.
5. **Follow cross-references** - If results mention related terms or "see also" references, search for those too.

### 5. Search Modes

| Mode | Flag | Best For |
|------|------|----------|
| All tiers | `--mode all` | General queries (default) |
| Exact only | `--mode exact` | When you know the exact term |
| BM25 only | `--mode bm25` | Ranked relevance for keyword queries |
| Fuzzy only | `--mode fuzzy` | Typo tolerance, partial matches |

### 6. Rebuilding the Index

If the data directory has been modified, the index auto-rebuilds on next search. To force a rebuild:

```bash
uv run ${SKILL_DIR}/scripts/lexy.py index --data <data-dir> --reindex
```

## Reference

For detailed documentation on the search pipeline tiers and tuning, read `${SKILL_DIR}/references/search-strategies.md`.
