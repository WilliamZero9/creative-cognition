"""
MCR (Model Context Retrieval) — Shared Library
Automatic context injection for Claude Code via hooks.
Pure stdlib Python, no dependencies.
"""

import json
import logging
import os
import re
import sys
import tempfile
from math import log2

# --- Configuration ---

VAULT_PATH = os.environ.get("MCR_VAULT_PATH", os.path.expanduser("~/obsidian-vault"))
INDEX_PATH = os.environ.get(
    "MCR_INDEX_PATH",
    os.path.join(VAULT_PATH, ".mcr", "index.json"),
)

MEMORY_PATHS = [
    os.path.expanduser("~/.claude/projects"),
]

# --- Debug Logging ---

MCR_DEBUG = os.environ.get("MCR_DEBUG", "0") == "1"
_logger = None


def debug_log(msg):
    """Write a debug message to mcr_debug.log when MCR_DEBUG=1."""
    global _logger
    if not MCR_DEBUG:
        return
    if _logger is None:
        _logger = logging.getLogger("mcr")
        _logger.setLevel(logging.DEBUG)
        handler = logging.FileHandler(
            os.path.join(os.path.dirname(__file__), "mcr_debug.log")
        )
        handler.setFormatter(logging.Formatter("%(asctime)s %(message)s"))
        _logger.addHandler(handler)
    _logger.debug(msg)


# --- Path Normalization ---


def normalize_path(p):
    """Normalize a path to forward slashes for consistent cross-platform comparison."""
    return p.replace("\\", "/")


# --- File Locking (cross-platform) ---

if sys.platform == "win32":
    import msvcrt

    def lock_file(f):
        msvcrt.locking(f.fileno(), msvcrt.LK_LOCK, 1)

    def unlock_file(f):
        msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
else:
    import fcntl

    def lock_file(f):
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)

    def unlock_file(f):
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)


# --- Stopwords ---

STOPWORDS = frozenset({
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "as", "is", "was", "are", "were", "be",
    "been", "being", "have", "has", "had", "do", "does", "did", "will",
    "would", "could", "should", "may", "might", "can", "shall", "must",
    "not", "no", "nor", "if", "then", "else", "when", "while", "where",
    "how", "what", "which", "who", "whom", "whose", "why", "that", "this",
    "these", "those", "it", "its", "he", "she", "they", "them", "their",
    "we", "our", "you", "your", "me", "my", "him", "her", "his", "us",
    "all", "each", "every", "both", "few", "more", "most", "other", "some",
    "such", "than", "too", "very", "just", "about", "above", "after",
    "again", "also", "any", "because", "before", "between", "down", "during",
    "even", "first", "get", "into", "like", "make", "made", "many", "much",
    "new", "now", "only", "out", "over", "own", "same", "set", "so",
    "still", "take", "through", "under", "up", "use", "used", "using",
    "want", "well", "here", "there", "need", "know", "way", "look",
})


# --- Frontmatter Parsing ---

_FM_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
_PRIORITY_RE = re.compile(r"^priority:\s*(\w+)", re.MULTILINE)
_TITLE_RE = re.compile(r"^#\s+(.+)", re.MULTILINE)

PRIORITY_MULTIPLIER = {"high": 1.5, "normal": 1.0, "low": 0.5}


def _parse_yaml_list(fm_text, key):
    """Parse a YAML key that may be inline [a, b] or multi-line '- item' format.

    Returns a list of stripped, unquoted strings.
    """
    # Try inline format first:  key: [a, b, c]
    inline_re = re.compile(rf"^{re.escape(key)}:\s*\[(.*?)\]", re.MULTILINE)
    m = inline_re.search(fm_text)
    if m:
        return [t.strip().strip("'\"") for t in m.group(1).split(",") if t.strip()]

    # Try multi-line format:
    #   key:
    #     - item1
    #     - item2
    lines = fm_text.splitlines()
    result = []
    collecting = False
    for line in lines:
        if collecting:
            stripped = line.strip()
            if stripped.startswith("- "):
                value = stripped[2:].strip().strip("'\"")
                if value:
                    result.append(value)
            else:
                # End of multi-line list (next key or blank unindented line)
                break
        else:
            # Check if this line starts our key
            key_match = re.match(rf"^{re.escape(key)}:\s*(.*)", line)
            if key_match:
                rest = key_match.group(1).strip()
                if rest:
                    # Single-line value (not a list), treat as comma-separated
                    return [k.strip().strip("'\"") for k in rest.split(",") if k.strip()]
                else:
                    # Value is on subsequent lines
                    collecting = True

    return result


def parse_frontmatter(content):
    """Parse YAML-like frontmatter. Returns (metadata_dict, body_text)."""
    meta = {"tags": [], "keywords": [], "aliases": [], "priority": "normal", "title": ""}
    body = content

    fm_match = _FM_RE.match(content)
    if fm_match:
        fm = fm_match.group(1)
        body = content[fm_match.end():]

        meta["tags"] = _parse_yaml_list(fm, "tags")
        meta["keywords"] = _parse_yaml_list(fm, "keywords")
        meta["aliases"] = _parse_yaml_list(fm, "aliases")

        m = _PRIORITY_RE.search(fm)
        if m:
            meta["priority"] = m.group(1).lower()

    title_match = _TITLE_RE.search(body)
    if title_match:
        meta["title"] = title_match.group(1).strip()

    return meta, body


# --- Synonym Expansion ---

_synonyms = None
_reverse_synonyms = None


def load_synonyms():
    """Load synonyms.json and build bidirectional lookup. Returns (forward, reverse) dicts."""
    global _synonyms, _reverse_synonyms
    if _synonyms is not None:
        return _synonyms, _reverse_synonyms

    syn_path = os.path.join(os.path.dirname(__file__), "synonyms.json")
    try:
        with open(syn_path, "r", encoding="utf-8") as f:
            _synonyms = json.load(f)
    except (OSError, json.JSONDecodeError):
        _synonyms = {}

    # Build reverse map: expansion -> [keys]
    _reverse_synonyms = {}
    for key, expansions in _synonyms.items():
        for exp in expansions:
            _reverse_synonyms.setdefault(exp.lower(), set()).add(key.lower())

    debug_log(f"Loaded {len(_synonyms)} synonym groups")
    return _synonyms, _reverse_synonyms


def expand_synonyms(tokens):
    """Expand a set of tokens with synonyms. Returns dict {term: weight_multiplier}.

    Original tokens get weight 1.0, synonym-expanded tokens get 0.7.
    """
    forward, reverse = load_synonyms()
    result = {t: 1.0 for t in tokens}

    for token in tokens:
        # Forward: token is a short form -> expand to long forms
        if token in forward:
            for exp in forward[token]:
                exp_lower = exp.lower()
                if exp_lower not in result:
                    result[exp_lower] = 0.7

        # Reverse: token is a long form -> also search the short form
        if token in reverse:
            for short in reverse[token]:
                if short not in result:
                    result[short] = 0.7

    expanded_count = sum(1 for w in result.values() if w < 1.0)
    if expanded_count:
        debug_log(f"Synonym expansion: {len(tokens)} tokens -> {len(result)} ({expanded_count} expanded)")

    return result


# --- Tokenization ---

_TOKEN_RE = re.compile(r"[a-zA-Z][a-zA-Z0-9_-]{2,}")


def tokenize_query(text, max_chars=2000):
    """Extract search tokens from text. Returns dict {term: weight} including synonyms + bigrams."""
    text = text[:max_chars].lower()
    tokens = [t for t in _TOKEN_RE.findall(text) if t not in STOPWORDS]

    base_tokens = set(tokens)
    # Generate bigrams for compound matching
    for i in range(len(tokens) - 1):
        base_tokens.add(f"{tokens[i]} {tokens[i+1]}")

    # Expand with synonyms
    weighted = expand_synonyms(base_tokens)

    debug_log(f"Tokenized: {len(base_tokens)} base tokens -> {len(weighted)} with synonyms")
    return weighted


# --- Index Loading ---

def load_index():
    """Load index.json. Returns dict or None on failure."""
    try:
        with open(INDEX_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError):
        debug_log(f"Failed to load index from {INDEX_PATH}")
        return None

    # Normalize all paths in the index to forward slashes
    if "files" in data:
        data["files"] = {normalize_path(k): v for k, v in data["files"].items()}
    if "terms" in data:
        for term, entries in data["terms"].items():
            for entry in entries:
                entry["file"] = normalize_path(entry["file"])

    debug_log(f"Loaded index: {len(data.get('files', {}))} files, {len(data.get('terms', {}))} terms")
    return data


# --- Levenshtein / Fuzzy Matching ---

def _levenshtein(s1, s2):
    """Compute Levenshtein edit distance between two strings."""
    if len(s1) < len(s2):
        return _levenshtein(s2, s1)
    if len(s2) == 0:
        return len(s1)

    prev_row = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        curr_row = [i + 1]
        for j, c2 in enumerate(s2):
            cost = 0 if c1 == c2 else 1
            curr_row.append(min(
                curr_row[j] + 1,        # insert
                prev_row[j + 1] + 1,    # delete
                prev_row[j] + cost,      # substitute
            ))
        prev_row = curr_row

    return prev_row[-1]


def fuzzy_match_terms(weighted_tokens, index):
    """Try fuzzy matching for tokens 5+ chars against index terms. Returns {file: score} additions."""
    terms_index = index.get("terms", {})
    all_index_terms = list(terms_index.keys())
    fuzzy_scores = {}

    # Only attempt fuzzy matching for longer tokens to avoid false positives
    candidates = [t for t, w in weighted_tokens.items() if len(t) >= 5 and " " not in t]
    if not candidates:
        return fuzzy_scores

    for token in candidates:
        token_weight = weighted_tokens[token]
        for idx_term in all_index_terms:
            if idx_term == token or " " in idx_term:
                continue
            if abs(len(idx_term) - len(token)) > 2:
                continue  # Quick length pre-filter
            dist = _levenshtein(token, idx_term)
            if dist <= 2:
                for entry in terms_index[idx_term]:
                    fp = entry["file"]
                    w = entry["weight"] * 0.5 * token_weight  # Fuzzy discount
                    fuzzy_scores[fp] = fuzzy_scores.get(fp, 0.0) + w

    if fuzzy_scores:
        debug_log(f"Fuzzy matching found {len(fuzzy_scores)} additional file candidates")

    return fuzzy_scores


# --- Matching ---

def match_terms(weighted_tokens, index):
    """Match tokens against index. Returns [(relative_path, score)] sorted by score desc.

    weighted_tokens: dict {term: weight_multiplier} from tokenize_query.
    For backward compat, also accepts a plain set (all weights = 1.0).
    """
    # Support both dict (new) and set (old) inputs
    if isinstance(weighted_tokens, set):
        weighted_tokens = {t: 1.0 for t in weighted_tokens}

    terms_index = index.get("terms", {})
    files_meta = index.get("files", {})
    scores = {}
    match_counts = {}

    for token, token_weight in weighted_tokens.items():
        entries = terms_index.get(token, [])
        for entry in entries:
            fp = normalize_path(entry["file"])
            w = entry["weight"] * token_weight
            scores[fp] = scores.get(fp, 0.0) + w
            match_counts[fp] = match_counts.get(fp, 0) + 1

    # Apply breadth bonus: reward files matching multiple different tokens
    for fp in scores:
        n = match_counts[fp]
        if n > 1:
            scores[fp] *= (1.0 + 0.3 * log2(n))

    # If exact matching returned few results, try fuzzy matching
    exact_above_threshold = sum(1 for sc in scores.values() if sc >= 3.0)
    if exact_above_threshold < 2:
        fuzzy_scores = fuzzy_match_terms(weighted_tokens, index)
        for fp, fsc in fuzzy_scores.items():
            scores[fp] = scores.get(fp, 0.0) + fsc
            match_counts[fp] = match_counts.get(fp, 0) + 1

    # Filter below minimum threshold
    results = [(fp, sc) for fp, sc in scores.items() if sc >= 3.0]

    # Sort: score desc, then smaller files first (tie-break), then alphabetical
    def sort_key(item):
        fp, sc = item
        char_count = files_meta.get(fp, {}).get("char_count", 99999)
        return (-sc, char_count, fp)

    results.sort(key=sort_key)

    debug_log(f"Matching: {len(results)} files above threshold (top: {results[0] if results else 'none'})")
    return results


# --- Index Staleness Check ---

def index_is_stale():
    """Check if any .md file in the vault (or memory paths) is newer than index.json.

    Returns True if index is stale or missing, False if up-to-date.
    """
    try:
        index_mtime = os.path.getmtime(INDEX_PATH)
    except OSError:
        debug_log("Index file missing — stale")
        return True

    scan_dirs = [VAULT_PATH] + MEMORY_PATHS

    for scan_dir in scan_dirs:
        if not os.path.isdir(scan_dir):
            continue
        for root, _dirs, files in os.walk(scan_dir):
            for fname in files:
                if fname.endswith(".md"):
                    fpath = os.path.join(root, fname)
                    try:
                        if os.path.getmtime(fpath) > index_mtime:
                            debug_log(f"Stale: {fpath} is newer than index")
                            return True
                    except OSError:
                        continue

    debug_log("Index is up-to-date")
    return False


# --- Session Deduplication ---

SEEN_DIR = os.path.join(tempfile.gettempdir(), "mcr_sessions")


def _seen_path(session_id):
    return os.path.join(SEEN_DIR, f"seen_{session_id}.json")


def load_seen_files(session_id):
    """Load set of vault files already injected this session (with file locking)."""
    if not session_id:
        return set()
    path = _seen_path(session_id)
    try:
        with open(path, "r+") as f:
            try:
                lock_file(f)
                data = set(json.load(f))
            finally:
                try:
                    unlock_file(f)
                except OSError:
                    pass
            return data
    except (OSError, json.JSONDecodeError):
        return set()


def record_injected(files, session_id):
    """Record which files were injected so they aren't repeated (with file locking)."""
    if not session_id or not files:
        return
    os.makedirs(SEEN_DIR, exist_ok=True)
    path = _seen_path(session_id)

    try:
        # Open for read+write, create if not exists
        try:
            f = open(path, "r+")
        except FileNotFoundError:
            f = open(path, "w+")

        try:
            lock_file(f)
            f.seek(0)
            content = f.read()
            if content:
                try:
                    seen = set(json.loads(content))
                except json.JSONDecodeError:
                    seen = set()
            else:
                seen = set()

            seen.update(normalize_path(fp) for fp in files)
            f.seek(0)
            f.truncate()
            json.dump(sorted(seen), f)
        finally:
            try:
                unlock_file(f)
            except OSError:
                pass
            f.close()
    except OSError:
        pass

    debug_log(f"Recorded {len(files)} injected files for session {session_id}")


def filter_matches(matches, session_id=None):
    """Apply relative threshold and session deduplication."""
    if not matches:
        return []

    # Relative threshold: only keep files within 30% of top score
    top_score = matches[0][1]
    rel_floor = top_score * 0.3
    matches = [(fp, sc) for fp, sc in matches if sc >= rel_floor]

    # Dedup: skip files already injected this session
    if session_id:
        seen = load_seen_files(session_id)
        # Normalize for comparison
        seen_normalized = {normalize_path(s) for s in seen}
        matches = [(fp, sc) for fp, sc in matches if normalize_path(fp) not in seen_normalized]

    return matches


# --- File Reading with Budget ---

def read_vault_files(matches, char_budget, max_files=5):
    """Read matched vault files within character budget. Returns (formatted_string, list_of_injected_paths)."""
    if not matches:
        return "", []

    parts = []
    injected = []
    remaining = char_budget

    for fp, _score in matches[:max_files]:
        if remaining <= 100:
            break

        norm_fp = normalize_path(fp)

        # Resolve memory: prefixed paths to actual filesystem paths
        if fp.startswith("memory:"):
            mem_rel = fp[len("memory:"):]  # e.g. "C--Users-Liam/file.md"
            full_path = None
            for mem_dir in MEMORY_PATHS:
                candidate = os.path.join(mem_dir, mem_rel.replace("/", os.sep))
                # Also try with "memory" subdirectory
                candidate_mem = os.path.join(mem_dir, mem_rel.split("/")[0], "memory", *mem_rel.split("/")[1:])
                if os.path.isfile(candidate):
                    full_path = candidate
                    break
                if os.path.isfile(candidate_mem):
                    full_path = candidate_mem
                    break
            if not full_path:
                debug_log(f"Memory file not found: {fp}")
                continue
        else:
            # Try vault path first, then memory paths
            full_path = os.path.join(VAULT_PATH, fp)
            if not os.path.isfile(full_path):
                # Check memory paths
                found = False
                for mem_dir in MEMORY_PATHS:
                    candidate = os.path.join(mem_dir, fp)
                    if os.path.isfile(candidate):
                        full_path = candidate
                        found = True
                        break
                if not found:
                    # Try as absolute path
                    if os.path.isfile(fp):
                        full_path = fp
                    else:
                        debug_log(f"File not found: {fp}")
                        continue

        try:
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()
        except OSError:
            continue

        # Strip frontmatter for injection (Claude doesn't need the YAML)
        _, body = parse_frontmatter(content)
        body = body.strip()

        if not body:
            continue

        header = f"--- [vault: {norm_fp}] ---\n"
        footer = "\n--- [end] ---"
        overhead = len(header) + len(footer)

        if len(body) + overhead <= remaining:
            parts.append(f"{header}{body}{footer}")
            remaining -= len(body) + overhead
            injected.append(norm_fp)
        else:
            # Truncate to fit
            available = remaining - overhead - 50
            if available < 100:
                break
            truncated = body[:available] + "\n[...truncated, see full file in vault]"
            parts.append(f"{header}{truncated}{footer}")
            remaining = 0
            injected.append(norm_fp)

    debug_log(f"Injected {len(injected)} files, {char_budget - remaining} chars used of {char_budget} budget")
    return "\n\n".join(parts), injected


# --- Output Building ---

MCR_HEADER = "[MCR: Knowledge vault context injected automatically. These are reference documents relevant to the current task.]"
MCR_FOOTER = "[End MCR context]"


def build_context_string(matches, char_budget):
    """Build the full additionalContext string from matches. Returns (context_string, injected_files)."""
    content, injected = read_vault_files(matches, char_budget)
    if not content:
        return "", []
    return f"{MCR_HEADER}\n\n{content}\n\n{MCR_FOOTER}", injected


# --- Safe Hook I/O ---

def read_hook_input():
    """Read JSON from stdin. Returns dict or None."""
    try:
        return json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return None


def write_hook_output(obj):
    """Write JSON to stdout and exit 0."""
    json.dump(obj, sys.stdout, ensure_ascii=False)
    sys.exit(0)


def safe_exit_empty():
    """Exit with empty output (no context injection, no blocking)."""
    sys.exit(0)
