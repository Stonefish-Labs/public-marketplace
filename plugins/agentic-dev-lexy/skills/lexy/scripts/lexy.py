#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "bm25s>=0.2",
#     "rapidfuzz>=3.0",
#     "pyyaml>=6.0",
#     "python-frontmatter>=1.0",
# ]
# ///
"""
Lexy - Multi-tier local document search.

Indexes documents from a data directory and provides exact, BM25, and fuzzy
search without any external API or LLM inference calls.

Usage:
    uv run scripts/lexy.py search "query" --data ./data
    uv run scripts/lexy.py index --data ./data
    uv run scripts/lexy.py info --data ./data
"""

import argparse
import csv
import hashlib
import io
import json
import os
import pickle
import re
import sys
from pathlib import Path

import bm25s
import frontmatter
import yaml
from rapidfuzz import fuzz, process

# ---------------------------------------------------------------------------
# Document loading
# ---------------------------------------------------------------------------

SUPPORTED_EXTENSIONS = {".md", ".markdown", ".txt", ".yaml", ".yml", ".json", ".csv"}


def _load_markdown(path: Path) -> dict:
    post = frontmatter.load(str(path))
    return {"content": post.content, "metadata": dict(post.metadata)}


def _load_text(path: Path) -> dict:
    return {"content": path.read_text(encoding="utf-8", errors="replace"), "metadata": {}}


def _load_yaml(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if data is None:
        return {"content": "", "metadata": {}}
    return {"content": data, "metadata": {"format": "yaml"}}


def _load_json(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return {"content": data, "metadata": {"format": "json"}}


def _load_csv(path: Path) -> dict:
    with open(path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    return {"content": rows, "metadata": {"format": "csv", "row_count": len(rows)}}


LOADERS = {
    ".md": _load_markdown,
    ".markdown": _load_markdown,
    ".txt": _load_text,
    ".yaml": _load_yaml,
    ".yml": _load_yaml,
    ".json": _load_json,
    ".csv": _load_csv,
}


def load_document(path: Path) -> dict | None:
    ext = path.suffix.lower()
    loader = LOADERS.get(ext)
    if loader is None:
        return None
    try:
        return loader(path)
    except Exception as e:
        print(f"Warning: failed to load {path}: {e}", file=sys.stderr)
        return None


def scan_data_directory(data_dir: Path) -> list[Path]:
    files = []
    for p in sorted(data_dir.rglob("*")):
        if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS:
            # skip hidden files and index artifacts
            if any(part.startswith(".") for part in p.relative_to(data_dir).parts):
                continue
            files.append(p)
    return files


# ---------------------------------------------------------------------------
# Chunking
# ---------------------------------------------------------------------------


def _chunk_text_recursive(
    text: str,
    max_words: int = 500,
    overlap_words: int = 50,
    separators: tuple[str, ...] = ("\n\n", "\n", ". ", " "),
) -> list[str]:
    """Split text into chunks of roughly max_words, trying higher-level separators first."""
    words = text.split()
    if len(words) <= max_words:
        return [text.strip()] if text.strip() else []

    # Try each separator level
    for sep in separators:
        parts = text.split(sep)
        if len(parts) <= 1:
            continue

        chunks = []
        current = []
        current_word_count = 0

        for part in parts:
            part_words = len(part.split())
            if current_word_count + part_words > max_words and current:
                chunk_text = sep.join(current).strip()
                if chunk_text:
                    chunks.append(chunk_text)
                # overlap: keep last portion
                overlap_parts = []
                overlap_count = 0
                for p in reversed(current):
                    pw = len(p.split())
                    if overlap_count + pw > overlap_words:
                        break
                    overlap_parts.insert(0, p)
                    overlap_count += pw
                current = overlap_parts + [part]
                current_word_count = overlap_count + part_words
            else:
                current.append(part)
                current_word_count += part_words

        if current:
            chunk_text = sep.join(current).strip()
            if chunk_text:
                chunks.append(chunk_text)

        if len(chunks) > 1:
            return chunks

    # Hard split by word count as last resort
    chunks = []
    for i in range(0, len(words), max_words - overlap_words):
        chunk = " ".join(words[i : i + max_words])
        if chunk.strip():
            chunks.append(chunk.strip())
    return chunks


def _chunk_markdown(text: str, max_words: int = 500, overlap_words: int = 50) -> list[dict]:
    """Split markdown by headers, then chunk large sections."""
    # Split on headers (# through ###)
    header_pattern = re.compile(r"^(#{1,3} .+)$", re.MULTILINE)
    parts = header_pattern.split(text)

    sections = []
    current_section = ""
    current_header = ""

    for part in parts:
        if header_pattern.match(part):
            if current_section.strip():
                sections.append({"section": current_header, "text": current_section.strip()})
            current_header = part.strip()
            current_section = ""
        else:
            current_section += part

    if current_section.strip():
        sections.append({"section": current_header, "text": current_section.strip()})

    # Now chunk each section if too large
    chunks = []
    for sec in sections:
        sub_chunks = _chunk_text_recursive(sec["text"], max_words, overlap_words)
        for i, chunk_text in enumerate(sub_chunks):
            chunks.append({"section": sec["section"], "text": chunk_text, "sub_index": i})

    return chunks


def _flatten_structured(data, prefix: str = "") -> list[dict]:
    """Flatten structured data (dict/list) into searchable text chunks."""
    chunks = []

    if isinstance(data, dict):
        for key, value in data.items():
            entry_key = f"{prefix}{key}" if not prefix else f"{prefix} > {key}"
            if isinstance(value, dict):
                # Check if it looks like a glossary entry (has 'definitions' key)
                if "definitions" in value:
                    defs = value["definitions"]
                    texts = []
                    see_also = []
                    for d in defs:
                        if isinstance(d, dict):
                            texts.append(d.get("text", str(d)))
                            see_also.extend(d.get("see_also", []))
                        else:
                            texts.append(str(d))
                    content = f"{key}: {'; '.join(texts)}"
                    if see_also:
                        content += f" (See also: {', '.join(set(see_also))})"
                    chunks.append({"section": key, "text": content})
                else:
                    # Recurse for nested dicts
                    sub = _flatten_structured(value, entry_key)
                    if sub:
                        chunks.extend(sub)
                    else:
                        chunks.append({"section": entry_key, "text": json.dumps(value, indent=2)})
            elif isinstance(value, list):
                # Each list item as a chunk under this key
                for i, item in enumerate(value):
                    if isinstance(item, dict):
                        item_text = json.dumps(item, ensure_ascii=False)
                    else:
                        item_text = str(item)
                    chunks.append({"section": f"{entry_key}[{i}]", "text": f"{key}: {item_text}"})
            else:
                chunks.append({"section": entry_key, "text": f"{key}: {value}"})
    elif isinstance(data, list):
        for i, item in enumerate(data):
            if isinstance(item, dict):
                # CSV row or JSON array element
                item_text = " | ".join(f"{k}: {v}" for k, v in item.items())
                chunks.append({"section": f"{prefix}[{i}]", "text": item_text})
            else:
                chunks.append({"section": f"{prefix}[{i}]", "text": str(item)})

    return chunks


def build_chunks(data_dir: Path, files: list[Path]) -> list[dict]:
    """Load and chunk all documents, returning a list of chunk dicts."""
    all_chunks = []

    for filepath in files:
        doc = load_document(filepath)
        if doc is None:
            continue

        rel_path = str(filepath.relative_to(data_dir))
        content = doc["content"]
        metadata = doc.get("metadata", {})
        ext = filepath.suffix.lower()

        if ext in (".yaml", ".yml", ".json", ".csv") and not isinstance(content, str):
            # Structured data: flatten into chunks
            structured_chunks = _flatten_structured(content)
            for i, sc in enumerate(structured_chunks):
                all_chunks.append(
                    {
                        "content": sc["text"],
                        "source": rel_path,
                        "section": sc.get("section", ""),
                        "chunk_index": i,
                        "metadata": metadata,
                    }
                )
        elif ext in (".md", ".markdown"):
            # Markdown: header-aware chunking
            md_chunks = _chunk_markdown(content)
            for i, mc in enumerate(md_chunks):
                all_chunks.append(
                    {
                        "content": mc["text"],
                        "source": rel_path,
                        "section": mc.get("section", ""),
                        "chunk_index": i,
                        "metadata": metadata,
                    }
                )
        else:
            # Plain text: recursive chunking
            text_chunks = _chunk_text_recursive(content)
            for i, tc in enumerate(text_chunks):
                all_chunks.append(
                    {
                        "content": tc,
                        "source": rel_path,
                        "section": "",
                        "chunk_index": i,
                        "metadata": metadata,
                    }
                )

    return all_chunks


# ---------------------------------------------------------------------------
# Index management
# ---------------------------------------------------------------------------

INDEX_DIR_NAME = ".lexy_index"


def _compute_data_hash(files: list[Path]) -> str:
    """Hash based on file paths and modification times for cache invalidation."""
    h = hashlib.sha256()
    for f in sorted(files):
        h.update(str(f).encode())
        h.update(str(f.stat().st_mtime_ns).encode())
        h.update(str(f.stat().st_size).encode())
    return h.hexdigest()


def _index_dir(data_dir: Path) -> Path:
    return data_dir / INDEX_DIR_NAME


def build_index(data_dir: Path, force: bool = False) -> dict:
    """Build or load cached index for the data directory."""
    files = scan_data_directory(data_dir)
    if not files:
        return {"chunks": [], "bm25": None, "corpus_tokens": None, "data_hash": "", "stats": {"documents": 0, "chunks": 0}}

    data_hash = _compute_data_hash(files)
    idx_dir = _index_dir(data_dir)

    # Check cache
    if not force and idx_dir.exists():
        cache_meta_path = idx_dir / "meta.pkl"
        if cache_meta_path.exists():
            try:
                with open(cache_meta_path, "rb") as f:
                    cached = pickle.load(f)
                if cached.get("data_hash") == data_hash:
                    # Load bm25s index
                    retriever = bm25s.BM25.load(str(idx_dir / "bm25"), load_corpus=False)
                    cached["bm25"] = retriever
                    print(f"Loaded cached index ({cached['stats']['chunks']} chunks)", file=sys.stderr)
                    return cached
            except Exception as e:
                print(f"Cache invalid, rebuilding: {e}", file=sys.stderr)

    # Build fresh
    print(f"Indexing {len(files)} files from {data_dir}...", file=sys.stderr)
    chunks = build_chunks(data_dir, files)

    if not chunks:
        return {"chunks": [], "bm25": None, "corpus_tokens": None, "data_hash": data_hash, "stats": {"documents": len(files), "chunks": 0}}

    # Build BM25 index
    corpus_texts = [c["content"] for c in chunks]
    corpus_tokens = bm25s.tokenize(corpus_texts, stopwords="en")

    retriever = bm25s.BM25(method="bm25+")
    retriever.index(corpus_tokens)

    # Build fuzzy corpus (unique content strings for rapidfuzz)
    fuzzy_corpus = list(set(corpus_texts))

    # Persist
    idx_dir.mkdir(parents=True, exist_ok=True)

    retriever.save(str(idx_dir / "bm25"), corpus=corpus_texts)

    meta = {
        "chunks": chunks,
        "fuzzy_corpus": fuzzy_corpus,
        "data_hash": data_hash,
        "stats": {
            "documents": len(files),
            "chunks": len(chunks),
            "sources": sorted(set(c["source"] for c in chunks)),
        },
    }
    with open(idx_dir / "meta.pkl", "wb") as f:
        pickle.dump(meta, f)

    print(f"Indexed {len(chunks)} chunks from {len(files)} files", file=sys.stderr)

    meta["bm25"] = retriever
    return meta


# ---------------------------------------------------------------------------
# Search tiers
# ---------------------------------------------------------------------------


def _search_exact(query: str, chunks: list[dict], top_k: int = 10) -> list[dict]:
    """Tier 1: Exact substring match (case-insensitive)."""
    q_lower = query.lower()
    results = []
    for chunk in chunks:
        content_lower = chunk["content"].lower()
        if q_lower in content_lower:
            results.append(
                {
                    "content": chunk["content"],
                    "source": chunk["source"],
                    "section": chunk["section"],
                    "chunk_index": chunk["chunk_index"],
                    "score": 1.0,
                    "match_type": "exact",
                }
            )
    # Sort by content length (shorter = more focused match) then truncate
    results.sort(key=lambda r: len(r["content"]))
    return results[:top_k]


def _search_bm25(query: str, retriever, chunks: list[dict], top_k: int = 10) -> list[dict]:
    """Tier 2: BM25+ ranked retrieval."""
    if retriever is None:
        return []

    query_tokens = bm25s.tokenize([query], stopwords="en")
    doc_ids, scores = retriever.retrieve(query_tokens, k=min(top_k, len(chunks)))

    results = []
    # doc_ids and scores are 2D arrays (n_queries x k)
    ids = doc_ids[0]
    scr = scores[0]

    # Normalize scores to 0-1
    max_score = float(scr[0]) if len(scr) > 0 and float(scr[0]) > 0 else 1.0

    for doc_id, score in zip(ids, scr):
        score_f = float(score)
        if score_f <= 0:
            continue
        idx = int(doc_id)
        if idx < 0 or idx >= len(chunks):
            continue
        chunk = chunks[idx]
        results.append(
            {
                "content": chunk["content"],
                "source": chunk["source"],
                "section": chunk["section"],
                "chunk_index": chunk["chunk_index"],
                "score": round(score_f / max_score, 4),
                "match_type": "bm25",
            }
        )

    return results


def _search_fuzzy(
    query: str, chunks: list[dict], top_k: int = 10, threshold: int = 65
) -> list[dict]:
    """Tier 3: Fuzzy string matching via rapidfuzz.

    Matches against both section names (term titles) and full content.
    Section matches are boosted because short queries match term names better
    than full paragraphs.
    """
    if not chunks:
        return []

    results = []
    seen = set()

    # First pass: match against section/title names (better for short queries)
    sections = [c["section"] for c in chunks]
    non_empty_sections = [(i, s) for i, s in enumerate(sections) if s]
    if non_empty_sections:
        section_indices, section_texts = zip(*non_empty_sections)
        section_matches = process.extract(
            query,
            list(section_texts),
            scorer=fuzz.WRatio,
            limit=top_k,
            score_cutoff=threshold,
        )
        for _, score, match_pos in section_matches:
            chunk_idx = section_indices[match_pos]
            if chunk_idx in seen:
                continue
            seen.add(chunk_idx)
            chunk = chunks[chunk_idx]
            results.append(
                {
                    "content": chunk["content"],
                    "source": chunk["source"],
                    "section": chunk["section"],
                    "chunk_index": chunk["chunk_index"],
                    "score": round(score / 100.0, 4),
                    "match_type": "fuzzy",
                }
            )

    # Second pass: match against full content (better for longer queries)
    corpus = [c["content"] for c in chunks]
    content_matches = process.extract(
        query,
        corpus,
        scorer=fuzz.token_set_ratio,
        limit=top_k,
        score_cutoff=threshold,
    )
    for _, score, match_idx in content_matches:
        if match_idx in seen:
            continue
        seen.add(match_idx)
        chunk = chunks[match_idx]
        results.append(
            {
                "content": chunk["content"],
                "source": chunk["source"],
                "section": chunk["section"],
                "chunk_index": chunk["chunk_index"],
                "score": round(score / 100.0, 4),
                "match_type": "fuzzy",
            }
        )

    # Sort by score descending
    results.sort(key=lambda r: r["score"], reverse=True)
    return results[:top_k]


def search(
    query: str,
    index: dict,
    mode: str = "all",
    top_k: int = 5,
    fuzzy_threshold: int = 65,
) -> list[dict]:
    """Run the multi-tier search pipeline."""
    chunks = index.get("chunks", [])
    retriever = index.get("bm25")

    if not chunks:
        return []

    if mode == "exact":
        return _search_exact(query, chunks, top_k)
    elif mode == "bm25":
        return _search_bm25(query, retriever, chunks, top_k)
    elif mode == "fuzzy":
        return _search_fuzzy(query, chunks, top_k, fuzzy_threshold)

    # mode == "all": multi-tier pipeline
    # Tier 1: exact
    exact = _search_exact(query, chunks, top_k)
    if exact:
        return exact[:top_k]

    # Tier 2: BM25
    bm25_results = _search_bm25(query, retriever, chunks, top_k)
    if bm25_results:
        return bm25_results[:top_k]

    # Tier 3: fuzzy
    fuzzy = _search_fuzzy(query, chunks, top_k, fuzzy_threshold)
    if fuzzy:
        return fuzzy[:top_k]

    # Tier 4: fallback - return top BM25 regardless of score
    if retriever is not None:
        query_tokens = bm25s.tokenize([query], stopwords="en")
        doc_ids, scores = retriever.retrieve(query_tokens, k=min(3, len(chunks)))
        results = []
        ids = doc_ids[0]
        scr = scores[0]
        max_score = float(scr[0]) if len(scr) > 0 and float(scr[0]) > 0 else 1.0
        for doc_id, score in zip(ids, scr):
            idx = int(doc_id)
            if idx < 0 or idx >= len(chunks):
                continue
            chunk = chunks[idx]
            results.append(
                {
                    "content": chunk["content"],
                    "source": chunk["source"],
                    "section": chunk["section"],
                    "chunk_index": chunk["chunk_index"],
                    "score": round(float(score) / max_score, 4) if max_score > 0 else 0.0,
                    "match_type": "fallback",
                }
            )
        return results

    return []


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def cmd_search(args):
    data_dir = Path(args.data).resolve()
    if not data_dir.is_dir():
        print(json.dumps({"error": f"Data directory not found: {data_dir}"}))
        sys.exit(1)

    index = build_index(data_dir)
    results = search(
        query=args.query,
        index=index,
        mode=args.mode,
        top_k=args.top,
        fuzzy_threshold=args.fuzzy_threshold,
    )

    output = {
        "query": args.query,
        "mode": args.mode,
        "results": results,
        "total_results": len(results),
        "index_stats": index.get("stats", {}),
    }
    print(json.dumps(output, indent=2, ensure_ascii=False))


def cmd_index(args):
    data_dir = Path(args.data).resolve()
    if not data_dir.is_dir():
        print(json.dumps({"error": f"Data directory not found: {data_dir}"}))
        sys.exit(1)

    index = build_index(data_dir, force=args.reindex)
    output = {
        "action": "index",
        "stats": index.get("stats", {}),
        "cached": not args.reindex,
    }
    print(json.dumps(output, indent=2, ensure_ascii=False))


def cmd_info(args):
    data_dir = Path(args.data).resolve()
    if not data_dir.is_dir():
        print(json.dumps({"error": f"Data directory not found: {data_dir}"}))
        sys.exit(1)

    files = scan_data_directory(data_dir)
    idx_dir = _index_dir(data_dir)
    has_cache = idx_dir.exists() and (idx_dir / "meta.pkl").exists()

    # File type breakdown
    ext_counts: dict[str, int] = {}
    for f in files:
        ext = f.suffix.lower()
        ext_counts[ext] = ext_counts.get(ext, 0) + 1

    output = {
        "data_dir": str(data_dir),
        "total_files": len(files),
        "file_types": ext_counts,
        "has_cached_index": has_cache,
        "supported_extensions": sorted(SUPPORTED_EXTENSIONS),
    }

    if has_cache:
        try:
            with open(idx_dir / "meta.pkl", "rb") as f:
                cached = pickle.load(f)
            output["index_stats"] = cached.get("stats", {})
        except Exception:
            pass

    print(json.dumps(output, indent=2, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(
        description="Lexy - Multi-tier local document search",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # search
    p_search = subparsers.add_parser("search", help="Search the knowledge base")
    p_search.add_argument("query", help="Search query text")
    p_search.add_argument("--data", default="./data", help="Path to data directory")
    p_search.add_argument("--top", type=int, default=5, help="Number of results to return")
    p_search.add_argument(
        "--mode",
        choices=["all", "exact", "bm25", "fuzzy"],
        default="all",
        help="Search mode (default: all tiers)",
    )
    p_search.add_argument(
        "--fuzzy-threshold", type=int, default=65, help="Fuzzy match score threshold (0-100)"
    )
    p_search.set_defaults(func=cmd_search)

    # index
    p_index = subparsers.add_parser("index", help="Build/rebuild the search index")
    p_index.add_argument("--data", default="./data", help="Path to data directory")
    p_index.add_argument("--reindex", action="store_true", help="Force rebuild the index")
    p_index.set_defaults(func=cmd_index)

    # info
    p_info = subparsers.add_parser("info", help="Show info about the data and index")
    p_info.add_argument("--data", default="./data", help="Path to data directory")
    p_info.set_defaults(func=cmd_info)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
