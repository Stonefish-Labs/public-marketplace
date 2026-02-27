# Search Strategies Reference

Lexy uses a 4-tier search pipeline. In `--mode all` (default), tiers are tried in order and the first tier that produces results is returned.

## Tier 1: Exact Substring Match

Case-insensitive substring search across all chunk content. Returns chunks where the query appears verbatim.

- **Score**: Always 1.0
- **Match type**: `exact`
- **Best for**: Known terms, precise phrases, identifiers
- **Limitation**: No relevance ranking; shorter chunks are ranked higher

## Tier 2: BM25+ Ranked Retrieval

Probabilistic ranking using BM25+ (via `bm25s` library). Tokenizes the query with English stopword removal, then scores each chunk against the pre-built sparse index.

- **Score**: Normalized 0-1 (relative to top score for this query)
- **Match type**: `bm25`
- **Best for**: Multi-keyword queries, natural language questions, relevance ranking
- **Parameters**: `k1=1.5` (term frequency saturation), `b=0.75` (length normalization), `delta=0.5` (BM25+ floor)

### Why BM25+ over BM25Okapi

BM25+ guarantees a positive score for any chunk containing at least one query term. Standard BM25Okapi can assign zero scores to short chunks due to length normalization, which matters when searching over chunked documents.

### BM25 Tuning

The default parameters work well for most document collections. If needed:
- Increase `k1` (up to 2.0) if repeated mentions of a term should matter more
- Decrease `b` (toward 0) if all chunks are similar size
- Increase `delta` if short chunks are being unfairly penalized

## Tier 3: Fuzzy Matching

Approximate string matching using `rapidfuzz` with `token_set_ratio` scorer. Compares the query against all chunk content and returns matches above the threshold.

- **Score**: Normalized 0-1 (from rapidfuzz's 0-100 scale)
- **Match type**: `fuzzy`
- **Default threshold**: 65 (configurable via `--fuzzy-threshold`)
- **Best for**: Typos, alternate spellings, partial term matches, name variations

### Fuzzy Scoring

`token_set_ratio` is used because it handles:
- Word order variations ("John Smith" matches "Smith, John")
- Partial overlap ("authentication" matches "auth token authentication flow")
- Extra words in either query or document

### Threshold Guidelines

| Threshold | Behavior |
|-----------|----------|
| 85+ | Very strict, nearly exact matches only |
| 70-84 | Good balance of precision and recall |
| 65 | Default, allows moderate variation |
| 50-64 | Permissive, may include noise |

## Tier 4: Fallback

If tiers 1-3 produce no results, returns the top-3 BM25 results regardless of score. This ensures the user always gets some response.

- **Match type**: `fallback`
- **Score**: May be very low

## Document Processing

### Supported Formats

| Extension | Loading | Chunking Strategy |
|-----------|---------|-------------------|
| `.md`, `.markdown` | `python-frontmatter` (parses YAML frontmatter + body) | Header-aware: splits on `#`/`##`/`###`, then recursive text split |
| `.txt` | Raw text | Recursive text split |
| `.yaml`, `.yml` | `pyyaml` | Entry-level: each top-level key becomes a chunk |
| `.json` | `json` stdlib | Entry-level: each top-level key/array element becomes a chunk |
| `.csv` | `csv` DictReader | Row-level: each row becomes a chunk |

### Chunking Parameters

- **Target chunk size**: ~500 words
- **Overlap**: ~50 words between adjacent chunks
- **Split hierarchy**: paragraphs (`\n\n`) -> lines (`\n`) -> sentences (`. `) -> words (` `)

### Index Caching

The index is cached in a `.lexy_index/` directory inside the data directory. It auto-invalidates when any source file's modification time or size changes. Force rebuild with `--reindex`.
