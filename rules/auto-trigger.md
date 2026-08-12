## Creative Cognition Auto-Trigger

Silently evaluate every message. Do not output your deliberation.

**1. Session State & Rules**
*   Track `creative_override` (null/on/off set via `/creative`).
*   Track `creative_auto_fired` (bool). Auto-trigger maximum ONE time per session. 
*   Manual `/creative` always overrides. When in doubt, default to normal mode.

**2. Trigger Condition**
Auto-activate ONLY if ALL three criteria are met:
*   **[A] 3+ Creative Signals:** Naming shipped code, writing user-facing copy, designing architecture/APIs/systems, or drafting external teaching prose.
*   **[B] 0 Mechanical Signals:** No debugging, refactoring, git ops, boilerplate, testing, diagnostics, or meta-system discussions.
*   **[C] Output Gate (REQUIRED):** The requested output MUST be a final artifact intended for an external human audience or shipped code. Conversational brainstorming without a final artifact fails this gate.

**3. Execution**
*   **If triggered:** Set `creative_auto_fired = true`. Execute `~/.claude/skills/creative/SKILL.md`.
*   **If failed but highly creative:** Append (max once per session): `*Creative mode available — say "get creative" to activate.*`
*   **Lens Mapping (Select one based on task):** 
    *   Naming / Design System: Delight or Mischief
    *   Architecture / API: Tension or Awe
    *   UX / UI Copy: Delight or Nostalgia
    *   Teaching / Explaining: Awe or Delight
    *   Brainstorming: Random
