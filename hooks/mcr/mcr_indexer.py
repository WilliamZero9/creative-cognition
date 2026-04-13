#!/usr/bin/env python3
"""
MCR Indexer — Scans the vault and builds index.json.
Run manually after adding/editing vault files:
    python3 ~/.claude/hooks/mcr_indexer.py
    python3 ~/.claude/hooks/mcr_indexer.py --full   # force complete rebuild
"""

import glob as globmod
import json
import os
import re
import sys
from datetime import datetime, timezone
from math import log2

# Add hooks dir to path for mcr_lib import
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mcr_lib import (
    VAULT_PATH,
    INDEX_PATH,
    MEMORY_PATHS,
    STOPWORDS,
    parse_frontmatter,
    normalize_path,
    PRIORITY_MULTIPLIER,
)

_TOKEN_RE = re.compile(r"[a-zA-Z][a-zA-Z0-9_-]{2,}")
_HEADING_RE = re.compile(r"^#{2,3}\s+(.+)", re.MULTILINE)
_MD_STRIP_RE = re.compile(r"[*_`#\[\]()>]")
_TYPE_RE = re.compile(r"^type:\s*(\w+)", re.MULTILINE)
_FM_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)

SKIP_DIRS = {".mcr", ".obsidian", ".git", ".trash", "templates"}
MAX_FILE_SIZE = 50 * 1024  # 50KB

# Term weights by source
W_KEYWORD = 5.0
W_ALIAS = 4.0
W_TAG = 3.0
W_TITLE = 2.0
W_HEADING = 1.5
W_BODY = 1.0

# Short document threshold (words) — single mention is enough below this
SHORT_DOC_WORDS = 500


def extract_body_terms(body):
    """Extract meaningful terms from body text. Returns {term: weight}."""
    terms = {}

    # Extract heading terms (higher weight)
    for m in _HEADING_RE.finditer(body):
        heading_text = _MD_STRIP_RE.sub("", m.group(1)).lower()
        for token in _TOKEN_RE.findall(heading_text):
            if token not in STOPWORDS:
                terms[token] = max(terms.get(token, 0), W_HEADING)

    # Extract body terms
    clean = _MD_STRIP_RE.sub(" ", body).lower()
    tokens = [t for t in _TOKEN_RE.findall(clean) if t not in STOPWORDS]
    freq = {}
    for t in tokens:
        freq[t] = freq.get(t, 0) + 1

    # Short docs: single mention is enough; longer docs: need 2+ occurrences
    word_count = len(clean.split())
    min_occurrences = 1 if word_count < SHORT_DOC_WORDS else 2

    for t, count in freq.items():
        if count >= min_occurrences and t not in terms:
            terms[t] = W_BODY

    return terms


def _parse_type_from_content(content):
    """Extract frontmatter type field from raw content."""
    fm_match = _FM_RE.match(content)
    if fm_match:
        m = _TYPE_RE.search(fm_match.group(1))
        if m:
            return m.group(1).lower()
    return None


def index_file(rel_path, full_path, source="vault"):
    """Index a single file. Returns (file_meta, term_entries) or None."""
    try:
        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read()
    except (OSError, UnicodeDecodeError):
        return None

    meta, body = parse_frontmatter(content)
    priority_mult = PRIORITY_MULTIPLIER.get(meta["priority"], 1.0)

    # Feedback memory files get a priority boost
    if source == "memory":
        fm_type = _parse_type_from_content(content)
        if fm_type == "feedback":
            priority_mult *= 1.5

    # Collect all terms with weights
    all_terms = {}

    # Keywords (highest weight)
    for kw in meta["keywords"]:
        kw_lower = kw.lower().strip()
        if kw_lower:
            all_terms[kw_lower] = W_KEYWORD * priority_mult
            # Also index individual words from multi-word keywords
            for word in _TOKEN_RE.findall(kw_lower):
                if word not in STOPWORDS and word != kw_lower:
                    all_terms[word] = max(all_terms.get(word, 0), W_KEYWORD * 0.6 * priority_mult)

    # Aliases
    for alias in meta["aliases"]:
        alias_lower = alias.lower().strip()
        if alias_lower:
            all_terms[alias_lower] = max(all_terms.get(alias_lower, 0), W_ALIAS * priority_mult)
            for word in _TOKEN_RE.findall(alias_lower):
                if word not in STOPWORDS and word != alias_lower:
                    all_terms[word] = max(all_terms.get(word, 0), W_ALIAS * 0.6 * priority_mult)

    # Tags
    for tag in meta["tags"]:
        tag_lower = tag.lower().strip()
        if tag_lower:
            all_terms[tag_lower] = max(all_terms.get(tag_lower, 0), W_TAG * priority_mult)

    # Title
    if meta["title"]:
        title_lower = meta["title"].lower()
        for word in _TOKEN_RE.findall(title_lower):
            if word not in STOPWORDS:
                all_terms[word] = max(all_terms.get(word, 0), W_TITLE * priority_mult)

    # Body terms
    body_terms = extract_body_terms(body)
    for term, weight in body_terms.items():
        all_terms[term] = max(all_terms.get(term, 0), weight * priority_mult)

    file_meta = {
        "title": meta["title"] or os.path.splitext(os.path.basename(rel_path))[0],
        "tags": meta["tags"],
        "priority": meta["priority"],
        "char_count": len(body.strip()),
        "mtime": os.path.getmtime(full_path),
        "source": source,
    }

    return file_meta, all_terms


def _collect_vault_files():
    """Walk the vault and yield (rel_path, full_path, source) tuples."""
    for root, dirs, files in os.walk(VAULT_PATH):
        # Skip hidden/special dirs
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".")]

        for fname in files:
            if not fname.endswith(".md"):
                continue

            full_path = os.path.join(root, fname)

            # Skip large files
            try:
                if os.path.getsize(full_path) > MAX_FILE_SIZE:
                    continue
            except OSError:
                continue

            rel_path = os.path.relpath(full_path, VAULT_PATH).replace("\\", "/")
            yield rel_path, full_path, "vault"


def _collect_memory_files():
    """Scan Claude Code memory directories and yield (rel_path, full_path, source) tuples."""
    for projects_dir in MEMORY_PATHS:
        if not os.path.isdir(projects_dir):
            continue
        # Scan ~/.claude/projects/*/memory/*.md
        pattern = os.path.join(projects_dir, "*", "memory", "*.md")
        for full_path in globmod.glob(pattern):
            try:
                if os.path.getsize(full_path) > MAX_FILE_SIZE:
                    continue
            except OSError:
                continue

            # Use memory: prefix to distinguish from vault files
            basename = os.path.basename(full_path)
            # Include parent project dir for uniqueness
            project_dir = os.path.basename(os.path.dirname(os.path.dirname(full_path)))
            rel_path = f"memory:{project_dir}/{basename}"
            yield rel_path, full_path, "memory"


def _apply_tfidf(terms_index, files_meta):
    """Apply TF-IDF weighting to body-weight terms in the inverted index (in-place)."""
    total_docs = len(files_meta)
    if total_docs <= 1:
        return

    # Compute document frequency for each term
    doc_freq = {}
    for term, entries in terms_index.items():
        doc_freq[term] = len(entries)

    # Apply IDF boost to body-weight terms only
    for term, entries in terms_index.items():
        df = doc_freq[term]
        idf_boost = 1.0 + log2(total_docs / df) * 0.3
        for entry in entries:
            if entry["weight"] <= W_BODY:
                entry["weight"] = round(entry["weight"] * idf_boost, 2)


def _load_existing_index():
    """Load the existing index for incremental reuse. Returns (files_meta, terms_index) or (None, None)."""
    try:
        with open(INDEX_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("files", {}), data.get("terms", {})
    except (OSError, json.JSONDecodeError):
        return None, None


def build_index(full_rebuild=False):
    """Scan vault and memory files, build the index. Incremental by default."""
    # Load existing index for incremental mode
    old_files = None
    if not full_rebuild:
        old_files, _ = _load_existing_index()

    # Collect all current files
    current_files = {}  # rel_path -> (full_path, source)
    for rel_path, full_path, source in _collect_vault_files():
        current_files[rel_path] = (full_path, source)
    for rel_path, full_path, source in _collect_memory_files():
        current_files[rel_path] = (full_path, source)

    # Determine which files need (re)processing
    stats = {"new": 0, "updated": 0, "removed": 0, "unchanged": 0}
    files_to_process = {}  # rel_path -> (full_path, source)
    files_meta = {}        # rel_path -> meta (reused from old index when unchanged)

    for rel_path, (full_path, source) in current_files.items():
        if old_files and rel_path in old_files:
            old_mtime = old_files[rel_path].get("mtime", 0)
            try:
                cur_mtime = os.path.getmtime(full_path)
            except OSError:
                cur_mtime = 0
            if cur_mtime <= old_mtime:
                # Unchanged — reuse old metadata
                files_meta[rel_path] = old_files[rel_path]
                stats["unchanged"] += 1
                continue
            else:
                files_to_process[rel_path] = (full_path, source)
                stats["updated"] += 1
        else:
            files_to_process[rel_path] = (full_path, source)
            stats["new"] += 1

    # Count removed files
    if old_files:
        for old_path in old_files:
            if old_path not in current_files:
                stats["removed"] += 1

    # Process new/updated files
    file_terms = {}  # rel_path -> {term: weight}
    for rel_path, (full_path, source) in files_to_process.items():
        result = index_file(rel_path, full_path, source)
        if result is None:
            continue
        file_meta, all_terms = result
        files_meta[rel_path] = file_meta
        file_terms[rel_path] = all_terms

    # For unchanged files, we need to re-extract their terms for the inverted index
    # (we don't store per-file terms in the old index, only the inverted index)
    for rel_path in list(files_meta.keys()):
        if rel_path not in file_terms:
            full_path, source = current_files.get(rel_path, (None, "vault"))
            if full_path is None:
                continue
            result = index_file(rel_path, full_path, source)
            if result is None:
                # File became unreadable — drop it
                del files_meta[rel_path]
                continue
            _, all_terms = result
            file_terms[rel_path] = all_terms

    # Build inverted index
    terms_index = {}
    for rel_path, all_terms in file_terms.items():
        for term, weight in all_terms.items():
            if term not in terms_index:
                terms_index[term] = []
            terms_index[term].append({"file": rel_path, "weight": round(weight, 2)})

    # Apply TF-IDF to body terms
    _apply_tfidf(terms_index, files_meta)

    # Sort each term's entries by weight descending
    for term in terms_index:
        terms_index[term].sort(key=lambda e: -e["weight"])

    index = {
        "version": 2,
        "built_at": datetime.now(timezone.utc).isoformat(),
        "vault_path": VAULT_PATH,
        "file_count": len(files_meta),
        "terms": terms_index,
        "files": files_meta,
    }

    return index, stats


def main():
    full_rebuild = "--full" in sys.argv

    # Ensure .mcr directory exists
    mcr_dir = os.path.join(VAULT_PATH, ".mcr")
    os.makedirs(mcr_dir, exist_ok=True)

    mode = "full rebuild" if full_rebuild else "incremental"
    print(f"MCR Indexer ({mode}): scanning {VAULT_PATH}...")
    index, stats = build_index(full_rebuild=full_rebuild)

    # Atomic write
    tmp_path = INDEX_PATH + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2, ensure_ascii=False)
    os.replace(tmp_path, INDEX_PATH)

    print(f"Reindexed: {stats['new']} new, {stats['updated']} updated, "
          f"{stats['removed']} removed, {stats['unchanged']} unchanged")
    print(f"Index built: {index['file_count']} files, {len(index['terms'])} unique terms")
    print(f"Written to: {INDEX_PATH}")

    # Print top terms for verification
    top_terms = sorted(index["terms"].items(), key=lambda x: -max(e["weight"] for e in x[1]))[:15]
    print("\nTop terms by weight:")
    for term, entries in top_terms:
        files = ", ".join(e["file"].split("/")[-1] for e in entries[:3])
        max_w = max(e["weight"] for e in entries)
        print(f"  {term} (w={max_w:.1f}) -> {files}")


if __name__ == "__main__":
    main()
