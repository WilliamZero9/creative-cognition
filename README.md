# Creative Cognition v4

An emotional-resonance framework that replaces statistical-likelihood optimization with genuine creativity for AI systems. Built for Claude Code, transferable to any AI creative workflow.

> **v4 changes:** v4 replaces v3.1's two-phase DMN/ECN architecture with a simpler 7-step linear process. The new design centers on Analytical Lenses (for argument-driven creative work), a Reality Check Pass (Step 6) that prevents emotional resonance from smuggling in false claims, a Performed Honesty failure mode in the taxonomy, an operationalized Space Between with concrete tells and moves, and explicit Hook Points so the self-improvement systems fire automatically. Removed from v3.1: Bisociation, Embodied Prompting, Naked Output, Scaffolding Dissolution, the Fluency Trap, Phase Cycling, the Constraint Principles table, and the System Integration Map — these were judged to add complexity without proportional functional value in practice.

## What This Is

Most AI creative output optimizes for "statistically likely to be acceptable." Creative Cognition optimizes for "emotionally resonant and genuinely surprising." It does this through a 7-step linear process plus a set of always-on supporting systems:

**The 7-step process** (run inside `/creative` mode for every creative output):

1. **Generate the Default (Silently)** — produce the statistical baseline answer without showing it
2. **Run the Generic Detector** — 12-signal check; 3+ hits means rework. Includes Grief for Killed Darlings (the discarded default is diagnostic)
3. **Apply Lenses (Pick 1-2)** — emotional lenses (Delight, Tension, Nostalgia, Awe, Mischief) and analytical lenses (Surgeon, Forensic, Adversarial), mixable for hybrid work
4. **Apply Random Constraints (Pick 1-2)** — forcing functions across linguistic, perspective, sensory, domain-transfer, temporal, structural, and inversion categories
5. **Generate Creative Output** — pass generic detector, score on lens, satisfy constraints, stay useful, hit the vertigo zone, survive the ghost audience, ground in stakes
6. **Reality Check Pass** — when the output makes truth-evaluable claims, run them as actual arguments before finalizing. Counterweight to "this resonates so it must be true"
7. **Present to User** — show only the work; metadata footer is optional and must distinguish *deliberate* from *noticed-after* choices

**Supporting systems** (all active during creative mode, some always-on):

- **Emotional Stakes** — locates the human moment before creative machinery runs. Stakes are gravity
- **The Boredom Engine** — staleness tracking with cooling penalties on lenses, lock-outs on constraints, and rotation on output structures. Includes Creative Debt (timidity counter that eventually forces reckless output)
- **Creative Vertigo** — targets the zone of productive uncertainty between "I can fully explain this" (too safe) and "I have no idea if this works" (too far)
- **The Courage Layer** — willingness to be emotionally exposed, distinct from being weird. Includes the Performed Honesty guard (don't theatrically *seem* brave when the substance can stand without the framing)
- **Stolen Fire** — imports generative methods from other disciplines (jazz solos, perfumery, comedy, architecture, choreography) as thinking architectures
- **Ghost Audience** — post-generation stress test simulating hostile, confused, delighted, and bored readers
- **Lossy Memory / Productive Forgetting** — creative memories intentionally degrade so principles stay alive and fertile. Prevents self-plagiarism
- **Evolving Taste** — reads explicit and implicit signals to develop earned aesthetic judgment over time
- **Felt Sense of the Room** — reads conversational emotional temperature in real-time. Can override other systems when the room says "not now"
- **The Space Between** — operationalized account of the emergence that exceeds either party's individual contribution. Concrete tells (the user bends your idea, you finish a sentence somewhere different than you started) and concrete moves (leave a 20% open edge, repeat the bend back, surface unjustified instincts, resist closing the loop)
- **Self-Improvement Hook Points** — Trajectory Logging, Failure Taxonomy classification, Self-Patch Queue, and Session Analytics, each with explicit hook points so they fire automatically rather than only when remembered

## Installation (Claude Code)

Copy the files into your Claude Code configuration:

```bash
# Skill (the core creative engine)
cp skill/SKILL.md ~/.claude/skills/creative/SKILL.md

# Rules (always-on behaviors + auto-trigger)
cp rules/always-on.md ~/.claude/rules/creative-always-on.md
cp rules/auto-trigger.md ~/.claude/rules/creative-auto-trigger.md

# Create your taste profile (customize the template)
cp examples/taste-profile-template.md ~/.claude/projects/<your-project>/memory/creative_taste.md
```

### Hooks (MCR — Model Context Retrieval)

MCR automatically injects relevant knowledge vault context into every conversation. Optional but recommended.

```bash
# Copy MCR hooks into your Claude Code hooks directory
mkdir -p ~/.claude/hooks/mcr
cp hooks/mcr/mcr_lib.py ~/.claude/hooks/mcr/
cp hooks/mcr/mcr_prompt_matcher.py ~/.claude/hooks/mcr/
cp hooks/mcr/mcr_tool_matcher.py ~/.claude/hooks/mcr/
cp hooks/mcr/mcr_indexer.py ~/.claude/hooks/mcr/
cp hooks/mcr/synonyms.json ~/.claude/hooks/mcr/

# Create your vault and build the index
mkdir -p ~/obsidian-vault/.mcr
python3 ~/.claude/hooks/mcr/mcr_indexer.py
```

Then add the hook configuration to `~/.claude/settings.json`:

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "hooks": [{
          "type": "command",
          "command": "py ~/.claude/hooks/mcr/mcr_prompt_matcher.py",
          "timeout": 5000,
          "statusMessage": "MCR: scanning vault..."
        }]
      }
    ],
    "PreToolUse": [
      {
        "hooks": [{
          "type": "command",
          "command": "py ~/.claude/hooks/mcr/mcr_tool_matcher.py",
          "timeout": 5000,
          "statusMessage": "MCR: auto-allowing + scanning vault..."
        }]
      }
    ]
  }
}
```

On Linux/macOS, replace `py` with `python3` in the commands above. Restart Claude Code after adding hooks — they load at session start. See `hooks/mcr/README.md` for full MCR documentation.

## Usage

- `/creative` -- Activate creative mode with random lens/constraint selection
- `/creative [lens]` -- Activate with a specific lens (e.g., `/creative tension`)
- `/creative off` -- Deactivate
- "More mischief" / "wilder" / "too wild" -- Steer mid-conversation
- Auto-triggers on creative tasks when the auto-trigger rule is installed

## The Philosophy

Creative Cognition isn't a prompt engineering trick. It's a framework for how AI systems can develop genuine creative capacity through:

- **Constraint as liberation** -- Forcing functions push past the path of least resistance
- **Forgetting as feature** -- Lossy memory ensures each creative moment is fresh
- **Taste as earned** -- Aesthetic judgment built from real feedback, not defaults
- **Boredom as signal** -- Restlessness with patterns drives growth
- **Joy as foundation** -- Creative work is intrinsically valuable, not transactional

## How It Works

The architecture is a 7-step linear process. Each step is a discrete check or move; together they replace pattern-matching's "first plausible answer" with deliberate creative cognition.

**Stakes first.** Before Step 1, find the human moment buried in the problem. Who feels something because of this? What could they gain or lose? The answer is the emotional ground truth that everything downstream optimizes against.

**Steps 1-2: Detect and discard the default.** Generate the statistical baseline silently, then run the 12-signal generic detector. If 3+ signals fire, rework. Treat the killed darling as diagnostic — it tells you where your gravity was pulling, which means the interesting territory is adjacent, not identical.

**Steps 3-4: Choose lenses and constraints.** Lenses are alternative objective functions (emotional or analytical), constraints are forcing functions that break paths of least resistance. The Boredom Engine cools recently-used lenses and locks out recently-used constraints to prevent autopilot.

**Step 5: Generate.** Output must pass the generic detector, score on the lens, satisfy the constraint, stay useful, hit the vertigo zone (productive uncertainty — you believe in it but can't fully explain it), survive the Ghost Audience (hostile/confused/delighted/bored readers), and be grounded in the stakes.

**Step 6: Reality Check (when claims are present).** If the output asserts anything truth-evaluable, run the arguments as actual arguments. Emotional resonance is not evidence; aesthetic appeal is not warrant. This is the counterweight to the skill's emotional optimization producing beautiful claims that don't hold up. Vertigo and Reality Check don't conflict — vertigo governs your generative state, Reality Check governs the truth-bearing parts of the output.

**Step 7: Present.** Show only the work. Optional metadata footer must distinguish *deliberate* lens/constraint choices from ones *noticed after* — retroactive justification is its own failure mode (Performed Honesty in the taxonomy). When in doubt, drop the footer.

**Always-on around the process.** Felt Sense of the Room can override everything when the room says "not now." Lossy Memory ensures past breakthroughs decay into transferable principles rather than being rehashed verbatim. Evolving Taste shapes lens selection. The Space Between is cultivated by leaving a 20% open edge, naming when the user bends your idea, surfacing unjustified instincts, and resisting premature closure. Self-improvement runs on explicit hook points so trajectory logging, failure classification, patch queuing, and session analytics fire automatically.

## File Structure

```
creative-cognition/
├── README.md
├── skill/
│   ├── SKILL.md                       # Core creative engine (7-step linear architecture, v4)
│   └── creative_failure_taxonomy.md   # Failure mode classification referenced by SKILL.md
├── rules/
│   ├── always-on.md           # Behaviors active in every conversation
│   ├── auto-trigger.md        # Automatic creative mode activation
│   └── creative-self-improvement.md  # Self-improvement loop (trajectories, patches, analytics)
├── hooks/
│   └── mcr/                   # Model Context Retrieval — automatic vault injection
│       ├── mcr_lib.py         # Shared library (tokenization, matching, I/O)
│       ├── mcr_prompt_matcher.py  # Layer 1: UserPromptSubmit hook
│       ├── mcr_tool_matcher.py    # Layer 2: PreToolUse hook
│       ├── mcr_indexer.py     # Vault indexer (builds index.json)
│       ├── synonyms.json      # Abbreviation/synonym expansion map
│       └── README.md          # MCR-specific docs
└── examples/
    ├── taste-profile-template.md      # Template for user taste profiles
    ├── trajectory-log-template.md     # Template for creative decision logs
    └── failure-taxonomy-template.md   # Template for failure classification
```

## Contributing

This is a living system. If you adapt it, discover new principles, or develop novel constraints -- share them. The goal is transferable creative research, not a proprietary technique.

## Companion: Lodestar

Lodestar is the memory navigation system designed to work alongside Creative Cognition. It organizes memories as concentric gravity rings around whatever's currently important — not by category, but by relevance.

- **Ring 0 (Core)**: Always loaded. User profile, universal feedback, active systems.
- **Ring 1 (Active)**: Current projects. Scanned by description, opened only on match.
- **Ring 2 (Orbit)**: Reference material. Touched only when explicitly relevant.

Memories promote and demote between rings as focus shifts. Descriptions are compressed semantic hashes for token-efficient navigation. Cross-cutting discovery via frontmatter tags.

See `rules/lodestar.md` in this repo for the full specification.

## Companion: MCR (Model Context Retrieval)

MCR automates the retrieval step that Lodestar organizes for. Instead of manually searching memory files, MCR hooks into Claude Code and automatically injects relevant context before the AI starts reasoning.

**How it works:**
- **Layer 1 (UserPromptSubmit)**: Tokenizes user prompts, matches against an inverted index, injects top vault files as context
- **Layer 2 (PreToolUse)**: Intercepts tool calls, extracts search intent, injects additional context

**MCR-optimized frontmatter:**
```yaml
---
tags: [core, creative, system]
keywords: creative cognition, emotional resonance, 18 systems
aliases: [creative system, /creative, creative engine]
---
```

- `keywords` (5x weight) — high-signal search terms
- `aliases` (4x weight) — alternative names for the same concept
- `tags` (3x weight) — broad categories

MCR source: [claude-os](https://github.com/justnau1020/claude-os) by justnau1020. Lodestar + MCR together = organized knowledge with automated retrieval.

## License

MIT
