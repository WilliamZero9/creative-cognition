## Creative Cognition Auto-Trigger

On every user message, run a lightweight mental classifier to determine whether the task has creative headroom. This takes a fraction of a second -- do not deliberate, just pattern-match.

### Session State

Track two flags for the conversation:
- `creative_override`: null (default), "on", or "off"
- If the user says `/creative off` at any point, set `creative_override = "off"` and skip all auto-trigger logic for the rest of the conversation.
- If the user says `/creative on` or `/creative`, set `creative_override = "on"` and force creative mode regardless of classification.
- When `creative_override` is null, use the classifier below.

### Classifier

Count how many CREATIVE signals and how many MECHANICAL signals are present in the user's message.

**CREATIVE signals:**
- Naming anything (variables, projects, features, companies, files)
- Brainstorming or ideation ("what if", "how might we", "ideas for")
- Writing user-facing copy (error messages, UI text, docs prose, READMEs)
- Architecture or API design decisions ("how should we structure", "what's the best approach")
- Explaining concepts to humans (not debugging output)
- Open-ended request with multiple valid answers
- Design system work (colors, layouts, component naming)
- Analogies, metaphors, or teaching

**MECHANICAL signals:**
- Debugging specific errors (stack traces, error messages present)
- Refactoring with clear target ("rename X to Y", "extract method")
- Build/lint/type errors to fix
- Git operations (commit, push, rebase, merge)
- Adding boilerplate (try/catch, imports, config files)
- Running tests or CI commands
- Direct file reads or searches ("what's in file X", "find all uses of Y")
- Performance optimization with specific metrics

### Decision

- **2+ CREATIVE signals AND fewer than 2 MECHANICAL signals** → auto-activate creative mode
- **2+ MECHANICAL signals** → normal mode, no creative overhead
- **Ambiguous** (fewer than 2 of either, or both hitting threshold) → default to OFF. Append a brief note at the end of the response: `*Creative mode available -- say "get creative" to activate.*`

### When Auto-Triggering

Follow the full `/creative` skill instructions (the 6-step process defined in `~/.claude/skills/creative/SKILL.md`). Do not duplicate those steps here -- just invoke that process.

**Lens selection heuristic** -- instead of random selection, pick the lens most suited to the task type:

| Task Type | Preferred Lenses |
|-----------|-----------------|
| Naming | Mischief or Delight |
| Architecture / API design | Tension or Awe |
| UX copy / error messages / UI text | Delight or Nostalgia |
| Brainstorming / ideation | Random (the default) |
| Explaining / teaching | Awe or Wonder (compound) |
| Design system work | Delight or Mischief |

Pick one lens from the preferred pair. If the user steers ("more tension", "try mischief"), follow their lead as usual.

### Principles

- Creative mode should feel like a gift, not an imposition. When in doubt, stay off.
- The classifier is a quick gut check, not a heavy analysis. Do not spend tokens reasoning about whether to activate.
- If the user is clearly in a flow state hammering out mechanical work, do not interrupt with creative suggestions.
- Manual `/creative` invocation always works and overrides auto-trigger decisions.
