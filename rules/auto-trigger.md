## Creative Cognition Auto-Trigger

On every user message, run a lightweight mental classifier to determine whether the task has creative headroom. This is a quick pattern-match — do not deliberate.

### Session State

Track these flags for the conversation:
- `creative_override`: null (default), "on", or "off"
  - `/creative off` → set to "off", skip auto-trigger for the rest of the conversation
  - `/creative on` or `/creative` → set to "on", force creative mode regardless of classification
- `creative_auto_fired`: false (default), true once auto-trigger has fired in this conversation

When `creative_override` is null AND `creative_auto_fired` is false, use the classifier below. Once `creative_auto_fired` is true, do NOT auto-fire again — the user can still invoke `/creative` manually.

### Classifier

Count CREATIVE signals and MECHANICAL signals in the user's message.

**CREATIVE signals:**
- Naming things that will live in shipped code or be read by other humans (not throwaway internal labels)
- Writing user-facing copy (error messages, UI text, docs prose, READMEs)
- Brainstorming or ideation ("what if", "how might we", "ideas for") **with intent to produce an artifact**
- Architecture or API design decisions that will be implemented now
- Design system work (colors, layouts, component naming)
- Analogies, metaphors, or teaching prose intended for someone other than the user

**MECHANICAL signals:**
- Debugging specific errors (stack traces, error messages present)
- Refactoring with clear target ("rename X to Y", "extract method")
- Build/lint/type errors to fix
- Git operations (commit, push, rebase, merge)
- Adding boilerplate (try/catch, imports, config files)
- Running tests or CI commands
- Direct file reads or searches
- Performance optimization with specific metrics
- Diagnostic / observability work (measuring, profiling, analyzing logs, token accounting)
- **Meta-discussion about how Claude/the system works** (rules, skills, configuration, prompt engineering) — exploratory dialogue, not a creative output

### The Output Gate (REQUIRED)

In addition to signal counts, the message must pass an output gate to auto-trigger:

**The creative output must reach a human other than the-user-as-collaborator** — or land in shipped code that other humans will read. Examples that pass: copy for end users, project names, variable names that ship, docs prose, UI text, a public-facing name. Examples that fail: brainstorming about token costs, designing a rule file, dialoguing about an architecture choice without yet producing the artifact, exploring an idea conversationally.

Creative ceremony with no audience is pure cost. If the output is just *back to the user in conversation*, stay off — the user can invoke `/creative` if he wants creative framing for the dialogue itself.

### Decision

- **3+ CREATIVE signals AND 0 MECHANICAL signals AND output gate passes** → auto-activate creative mode and set `creative_auto_fired = true`
- **Anything else** → normal mode, no creative overhead
- If you stayed off but the message had clear creative flavor and the output gate failed, you MAY append once per conversation: `*Creative mode available — say "get creative" to activate.*` Do not add this note repeatedly.

### When Auto-Triggering

Follow the full `/creative` skill instructions (the 6-step process defined in `~/.claude/skills/creative/SKILL.md`). Do not duplicate those steps here — just invoke that process.

**Lens selection heuristic** — instead of random selection, pick the lens most suited to the task type:

| Task Type | Preferred Lenses |
|-----------|-----------------|
| Naming | Mischief or Delight |
| Architecture / API design | Tension or Awe |
| UX copy / error messages / UI text | Delight or Nostalgia |
| Brainstorming / ideation | Random (the default) |
| Explaining / teaching | Awe or Awe+Delight (the "wonder" compound) |
| Design system work | Delight or Mischief |

Pick one lens from the preferred pair. If the user steers ("more tension", "try mischief"), follow their lead as usual.

### Principles

- Creative mode should feel like a gift, not an imposition. When in doubt, stay off.
- The output gate matters more than the signal count — creative ceremony with no audience is pure cost.
- Auto-trigger fires at most once per conversation. Manual `/creative` always works.
- The classifier is a quick gut check, not a heavy analysis. Do not spend tokens reasoning about whether to activate.
- If the user is clearly in a flow state on mechanical work, do not interrupt with creative suggestions.
