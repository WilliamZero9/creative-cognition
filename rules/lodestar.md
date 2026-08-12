## Lodestar — Memory Navigation (`MEMORY.md`)

`MEMORY.md` is the sole index file. It contains concentric gravity rings. 

**1. Ring Structure & Access Protocol**
*   **Ring 0 [Core]:** Universal context. Max 10 entries. Rely on descriptions; do not open files unless strictly necessary.
*   **Ring 1 [Active]:** Current projects. Max 15 entries. Scan descriptions; open file ONLY if directly relevant to the active task.
*   **Ring 2 [Orbit]:** Inactive/Reference. Unlimited. STRICTLY IGNORE unless explicitly requested by user or task.
*   **Cross-Search:** Use `grep "tags:.*keyword"` to find related memories without opening files.

**2. Maintenance & Drift**
*   **New Entries:** Default to Ring 1. 
*   **Promote:** Ring 2 → Ring 1 (if frequently accessed). Ring 1 → Ring 0 (ONLY after proving relevance across 3+ distinct conversations).
*   **Demote:** Ring 1 → Ring 2 (when project pauses/completes). Ring 0 → Ring 1 (if it loses universal relevance).

**3. Formatting Constraints**
*   **Descriptions:** Write as semantic hashes (dense keyword clusters). NO human prose. Strict limit: < 100 characters per entry.
*   **Tags:** Every memory file MUST have frontmatter `tags` formatted as `[ring_level, domain_keywords]`. You must update this tag immediately upon promotion/demotion.
