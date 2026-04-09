## Lodestar — Memory Navigation System

The memory index (MEMORY.md) is organized as concentric gravity rings, not categories.

### Ring Structure
- **Ring 0 — Core**: Always relevant regardless of task. User profile, universal feedback, active systems. ~10 entries max.
- **Ring 1 — Active**: Current projects, project-specific feedback. Scanned by description, files opened only on relevance match. ~15 entries max.
- **Ring 2 — Orbit**: Reference material, inactive projects. Only accessed when explicitly relevant. No entry limit.

### Navigation Protocol (Token-Efficient)
1. MEMORY.md is always loaded (~50 lines). This is the ONLY index file.
2. Ring 0 descriptions are dense enough to inform most decisions without opening files.
3. Ring 1: scan descriptions, open only files matching current task.
4. Ring 2: ignore unless the user or task explicitly references something there.
5. Cross-cutting queries: `grep "tags:.*keyword"` on frontmatter finds all related memories in one call.

### Maintenance Rules
- **Promotion**: When a Ring 2 memory becomes frequently relevant, promote to Ring 1. When a Ring 1 memory is relevant in nearly every conversation, promote to Ring 0.
- **Demotion**: When a project completes or pauses, demote from Ring 1 to Ring 2. Ring 0 entries should only be demoted if they're genuinely no longer universal.
- **New memories**: Default to Ring 1. Only promote to Ring 0 after proving universal relevance across 3+ conversations.
- **Description compression**: Descriptions in MEMORY.md are semantic hashes — keyword clusters optimized for pattern-matching, not human prose. Under 100 chars each.
- **Tags**: Every memory file has a `tags` field in frontmatter. Tags use ring names (core/active/orbit) + domain keywords. Update tags when promoting/demoting.

### Why Lodestar
- Polar coordinate inspiration: memories addressed by distance-from-center (relevance) + angle (domain), not flat categories
- Single index file = one read per conversation (no MOC chain)
- Compressed descriptions = relevance decisions without opening files
- Tags = cross-cutting discovery via grep, no extra index files needed
- Dynamic drift = the map reorganizes around whatever's currently important
