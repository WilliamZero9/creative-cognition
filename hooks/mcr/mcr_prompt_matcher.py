#!/usr/bin/env python3
"""
MCR Prompt Matcher — Layer 1: UserPromptSubmit hook.
Receives user prompt, matches against vault index, injects relevant context.
"""

import json
import os
import subprocess
import sys

# Graceful import — if mcr_lib is broken, output valid empty JSON and exit
try:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from mcr_lib import (
        read_hook_input,
        write_hook_output,
        safe_exit_empty,
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

CONTENT_BUDGET = 8000


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


def main():
    hook_input = read_hook_input()
    if hook_input is None:
        debug_log("prompt_matcher: no hook input")
        safe_exit_empty()

    prompt = hook_input.get("prompt") or hook_input.get("user_prompt") or hook_input.get("userPrompt", "")
    if len(prompt) < 5:
        debug_log(f"prompt_matcher: prompt too short ({len(prompt)} chars)")
        safe_exit_empty()

    maybe_reindex()

    index = load_index()
    if index is None:
        debug_log("prompt_matcher: index load failed")
        safe_exit_empty()

    tokens = tokenize_query(prompt)
    if not tokens:
        debug_log("prompt_matcher: no tokens extracted")
        safe_exit_empty()

    debug_log(f"prompt_matcher: extracted {len(tokens)} tokens from prompt")

    matches = match_terms(tokens, index)
    if not matches:
        debug_log("prompt_matcher: no matches found")
        safe_exit_empty()

    debug_log(f"prompt_matcher: {len(matches)} raw matches (top: {matches[0][0]}={matches[0][1]:.1f})")

    session_id = hook_input.get("session_id", "")
    pre_dedup = len(matches)
    matches = filter_matches(matches, session_id=session_id)
    if not matches:
        deduped = pre_dedup - len(matches) if pre_dedup else 0
        debug_log(f"prompt_matcher: all matches filtered (session dedup removed {deduped})")
        safe_exit_empty()

    if pre_dedup != len(matches):
        debug_log(f"prompt_matcher: session dedup filtered {pre_dedup - len(matches)} files")

    context, injected = build_context_string(matches, CONTENT_BUDGET)
    if not context:
        debug_log("prompt_matcher: context build returned empty")
        safe_exit_empty()

    record_injected(injected, session_id)
    debug_log(f"prompt_matcher: injected {len(injected)} files ({len(context)} chars): {injected}")

    output = {
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": context,
        }
    }
    write_hook_output(output)


if __name__ == "__main__":
    try:
        if not _LIB_OK:
            # mcr_lib import failed — output nothing, don't crash Claude Code
            sys.exit(0)
        main()
    except Exception:
        # Never crash Claude Code — silently exit
        try:
            safe_exit_empty()
        except Exception:
            sys.exit(0)
