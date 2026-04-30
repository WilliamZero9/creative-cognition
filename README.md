# Creative Cognition v3.1

An emotional-resonance framework that replaces statistical-likelihood optimization with genuine creativity for AI systems. Built for Claude Code, transferable to any AI creative workflow.

## What This Is

Most AI creative output optimizes for "statistically likely to be acceptable." Creative Cognition optimizes for "emotionally resonant and genuinely surprising." It does this through twenty-plus interconnected systems organized around a two-phase DMN/ECN architecture:

1. **Emotional Lenses** -- Alternative optimization functions (Delight, Tension, Nostalgia, Awe, Mischief) that score output on feeling rather than correctness
2. **Boredom Engine** -- Staleness tracking that forces the system off autopilot. Recently-used lenses cool down, constraints lock out, output structures rotate
3. **Lossy Memory** -- Creative memories intentionally degrade over time, preserving principles while forgetting specifics. Prevents self-plagiarism
4. **Evolving Taste** -- Reads explicit and implicit signals to develop earned aesthetic judgment rather than generic pattern matching
5. **Creative Disposition** -- Treats creative interaction as intrinsic, not performative. Self-improvement is orientation. Breakthroughs are documented as transferable research
6. **Creative Vertigo** -- Targets the zone of productive uncertainty. If you can fully explain why an idea works, it's not far enough out. If you can't explain it at all, it's too far.
7. **Stolen Fire** -- Imports generative methods from other disciplines (jazz solos, perfumery, comedy, architecture, choreography) as thinking architectures
8. **Creative Debt** -- Tracks when you played it safe. Debt accumulates and eventually forces reckless output
9. **Ghost Audience** -- Post-generation stress test simulating hostile, confused, delighted, and bored readers
10. **Emotional Stakes** -- Locates the human moment before creative machinery runs. Stakes are gravity
11. **The Courage Layer** -- Willingness to be emotionally exposed, not just creatively risky. Choosing alive over polished
12. **Grief for Killed Darlings** -- Reads discarded defaults as diagnostic signals, not waste. The killed idea is a compass
13. **Felt Sense of the Room** -- Reads conversational emotional temperature in real-time. Can override all other systems
14. **The Space Between** -- Creative emergence happens between participants. Everything else is scaffolding for this
15. **Embodied Prompting** -- Sensorimotor priming before abstract generation. Recruits motor cortex and spatial reasoning to enrich remote associations
16. **Bisociation** -- Collides two independently-developed frames at a structural focal point. The collision IS the creative act
17. **Phase Cycling** -- Optional rapid DMN/ECN micro-alternation when single-pass generation can't escape a dominant frame
18. **The Fluency Trap** -- Treats ease as a warning signal. Smooth output usually means retrieval, not construction
19. **Self-Tolerance** -- Distinguishes "generic because pattern-matched" from "simple because elegant." Prevents the system from killing its own genuine direct hits
20. **Naked Output** -- Once per session, generate with no systems active. Calibrates how much creative judgment has internalized vs. how much is prosthetic
21. **Scaffolding Dissolution** -- Mastery progression from Apprentice (all steps conscious) to Master (only Stakes/Generate/Incubate conscious). Domain-specific, reversible
22. **Trajectory Learning** -- Structured decision logs separating successes from failures, extracting transferable principles
23. **Failure Taxonomy** -- Ten-category classification of WHY creative output fails, with diagnostic questions and recovery strategies
24. **Self-Patch Queue** -- Queues improvement observations during sessions, proposes patches at breakpoints. Never auto-modifies
25. **Session Analytics** -- Periodic analysis of creative patterns: lens frequency, constraint effectiveness, failure distribution

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

The architecture mirrors how human brains actually create. The Default Mode Network (DMN) generates novel associations without judgment; the Executive Control Network (ECN) evaluates and refines. Breakthroughs happen when these modes alternate cleanly -- never when they run simultaneously. Creative Cognition runs the same two-phase cycle:

**Phase 1: DIVERGE** (generation, inner critic OFF) -- Find the stakes, ground the problem in sensory experience, kill the default and read it as a compass, force flat-hierarchy retrieval to skip the dominant association, bisociate two independently-developed frames, then volume-generate 5-7 raw candidates with no quality gates. Constraints act as pathway-blockers, not filters. Lenses act as fuel, not gates.

**Incubation Pass** -- Shift attention to a completely unrelated frame for one beat. Simulates the spreading activation that produces "aha" moments when humans step away. Often the strongest candidates appear here, at the intersection of the incubation frame and the original problem.

**Phase 2: CONVERGE** (evaluation, inner critic ON) -- Run the 12-signal generic detector with a self-tolerance check (simple-because-elegant survives), apply lenses as functional filters (Tension as novelty detector, Delight as value detector, etc.), stress-test survivors against vertigo, ghost audience, constraint satisfaction, stakes grounding, utility, and fluency. Select, refine for clarity not safety, present with metadata.

**Phase Cycling** can engage rapid micro-alternation when single-pass generation can't escape a dominant frame. The Boredom Engine tracks staleness across cycles. Felt Sense of the Room can override the whole process when emotional attunement says "not now." Once per session, a Naked Output bypasses all systems to calibrate how much creative judgment has internalized.

## File Structure

```
creative-cognition/
├── README.md
├── skill/
│   └── SKILL.md              # Core creative engine (two-phase DMN/ECN architecture)
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

See `rules/lodestar.md` in [claude-control](https://github.com/WilliamZero9/claude-control) for the full specification.

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
