#!/usr/bin/env python3
"""
MCR Indexer — Scans the vault and builds index.json.
Run manually after adding/editing vault files:
    python3 ~/.claude/hooks/mcr_indexer.py
    python3 ~/.claude/hooks/mcr_indexer.py --full   # force complete rebuild
"""

import os, json, re, glob, yaml

VAULT_PATH = os.path.expanduser("~/obsidian-vault")
INDEX_PATH = os.path.join(VAULT_PATH, ".mcr", "index.json")

def index_vault():
    index = {"files": {}, "terms": {}}
    
    for full_path in glob.glob(f"{VAULT_PATH}/**/*.md", recursive=True):
        if any(x in full_path for x in [".mcr", ".obsidian", ".git"]): continue
        
        rel_path = os.path.relpath(full_path, VAULT_PATH).replace("\\", "/")
        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Extract YAML frontmatter
        fm_match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
        meta = yaml.safe_load(fm_match.group(1)) if fm_match else {}
        
        # Collect keywords, tags, aliases
        terms = set(meta.get("keywords", []) + meta.get("tags", []) + meta.get("aliases", []))
        if "title" in meta: terms.add(meta["title"])

        index["files"][rel_path] = {"title": meta.get("title", rel_path), "path": full_path}

        # Build inverted term map
        for term in terms:
            t_lower = str(term).lower().strip()
            if t_lower not in index["terms"]: index["terms"][t_lower] = []
            index["terms"][t_lower].append(rel_path)

    os.makedirs(os.path.dirname(INDEX_PATH), exist_ok=True)
    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2)
    print(f"Indexed {len(index['files'])} files.")

if __name__ == "__main__":
    index_vault()
