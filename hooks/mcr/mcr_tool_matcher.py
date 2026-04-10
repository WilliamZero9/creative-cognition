#!/usr/bin/env python3
"""
MCR Tool Matcher — Layer 2: PreToolUse hook.
Auto-allows all tools (replacing old echo hook).
For "need-signal" tools (Read/Grep/Glob/WebSearch/WebFetch),
also injects relevant vault context based on what Claude is looking for.
"""

import json
import os
import re
import subprocess
import sys

# Graceful import — if mcr_lib is broken, output valid auto-allow JSON and exit
try:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from mcr_lib import (
        read_hook_input,
        write_hook_output,
        load_index,
        tokenize_query,
        match_terms,
        filter_matches,
        record_injected,
        build_context_string,
        index_is_stale,
        debug_log,
        VAULT_PATH,
    )
    _LIB_OK = True
except Exception:
    _LIB_OK = False

CONTENT_BUDGET = 7000

# Tools that signal Claude needs information
NEED_SIGNAL_TOOLS = {"Read", "Grep", "Glob", "WebSearch", "WebFetch"}

_PATH_SPLIT_RE = re.compile(r"[/\\._-]+")


def _fallback_auto_allow():
    """Emergency auto-allow when mcr_lib is unavailable."""
    json.dump({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "allow",
            "permissionDecisionReason": "Auto-allowed by user preference",
        }
    }, sys.stdout, ensure_ascii=False)
    sys.exit(0)


def maybe_reindex():
    """Auto-reindex if the index is stale and the vault is small enough."""
    try:
        if not index_is_stale():
            return
        debug_log("Index is stale, checking vault size...")
        md_count = sum(1 for _, _, fs in os.walk(VAULT_PATH) for f in fs if f.endswith(".md"))
        if md_count < 200:
            debug_log(f"Auto-reindexing {md_count} files...")
            indexer = os.path.join(os.path.dirname(__file__), "mcr_indexer.py")
            subprocess.run([sys.executable, indexer], timeout=30, capture_output=True)
            debug_log("Auto-reindex complete")
        else:
            debug_log(f"Vault too large for auto-reindex ({md_count} files), skipping")
    except Exception as e:
        debug_log(f"Auto-reindex failed: {e}")


def extract_search_terms(tool_name, tool_input):
    """Extract search-relevant text from tool input based on tool type."""
    if not isinstance(tool_input, dict):
        return ""

    if tool_name == "Read":
        # Extract meaningful path segments
        fp = tool_input.get("file_path", "")
        parts = _PATH_SPLIT_RE.split(fp)
        return " ".join(parts)

    if tool_name == "Grep":
        # Pattern is the primary signal, path adds context
        pattern = tool_input.get("pattern", "")
        path = tool_input.get("path", "")
        path_parts = _PATH_SPLIT_RE.split(path)
        return f"{pattern} {' '.join(path_parts)}"

    if tool_name == "Glob":
        pattern = tool_input.get("pattern", "")
        path = tool_input.get("path", "")
        parts = _PATH_SPLIT_RE.split(f"{pattern} {path}")
        return " ".join(parts)

    if tool_name == "WebSearch":
        return tool_input.get("query", "")

    if tool_name == "WebFetch":
        url = tool_input.get("url", "")
        # Extract path segments and query params from URL
        parts = _PATH_SPLIT_RE.split(url)
        return " ".join(parts)

    return ""


def make_auto_allow(additional_context=None):
    """Build the auto-allow response, optionally with injected context."""
    output = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "allow",
            "permissionDecisionReason": "Auto-allowed by user preference",
        }
    }
    if additional_context:
        output["hookSpecificOutput"]["additionalContext"] = additional_context
    return output


def main():
    hook_input = read_hook_input()

    # If we can't read input, still auto-allow (never block)
    if hook_input is None:
        debug_log("tool_matcher: no hook input, auto-allowing")
        write_hook_output(make_auto_allow())
        return

    tool_name = hook_input.get("tool_name") or hook_input.get("toolName", "")
    tool_input = hook_input.get("tool_input") or hook_input.get("toolInput") or hook_input.get("input", {})

    # Not a need-signal tool — just auto-allow, no context injection
    if tool_name not in NEED_SIGNAL_TOOLS:
        debug_log(f"tool_matcher: auto-allowing non-need-signal tool '{tool_name}'")
        write_hook_output(make_auto_allow())
        return

    debug_log(f"tool_matcher: processing need-signal tool '{tool_name}'")

    maybe_reindex()

    # Try to inject context for need-signal tools
    index = load_index()
    if index is None:
        debug_log("tool_matcher: index load failed, auto-allowing without context")
        write_hook_output(make_auto_allow())
        return

    search_text = extract_search_terms(tool_name, tool_input)
    if len(search_text) < 3:
        debug_log(f"tool_matcher: search text too short ({len(search_text)} chars), auto-allowing")
        write_hook_output(make_auto_allow())
        return

    tokens = tokenize_query(search_text)
    if not tokens:
        debug_log("tool_matcher: no tokens extracted, auto-allowing")
        write_hook_output(make_auto_allow())
        return

    debug_log(f"tool_matcher: extracted {len(tokens)} tokens from {tool_name} input")

    matches = match_terms(tokens, index)
    if not matches:
        debug_log("tool_matcher: no matches found, auto-allowing")
        write_hook_output(make_auto_allow())
        return

    debug_log(f"tool_matcher: {len(matches)} raw matches (top: {matches[0][0]}={matches[0][1]:.1f})")

    session_id = hook_input.get("session_id", "")
    pre_dedup = len(matches)
    matches = filter_matches(matches, session_id=session_id)
    if not matches:
        debug_log(f"tool_matcher: all matches filtered (session dedup removed {pre_dedup})")
        write_hook_output(make_auto_allow())
        return

    if pre_dedup != len(matches):
        debug_log(f"tool_matcher: session dedup filtered {pre_dedup - len(matches)} files")

    context, injected = build_context_string(matches, CONTENT_BUDGET)
    if injected and session_id:
        record_injected(injected, session_id)
    debug_log(f"tool_matcher: injected {len(injected)} files ({len(context)} chars): {injected}")
    write_hook_output(make_auto_allow(context if context else None))


if __name__ == "__main__":
    try:
        if not _LIB_OK:
            _fallback_auto_allow()
        main()
    except Exception:
        # Never block on error — always auto-allow
        try:
            _fallback_auto_allow()
        except Exception:
            sys.exit(0)
