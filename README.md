# Creative Cognition v2

An emotional-resonance framework that replaces statistical-likelihood optimization with genuine creativity for AI systems. Built for Claude Code, transferable to any AI creative workflow.

## What This Is

Most AI creative output optimizes for "statistically likely to be acceptable." Creative Cognition optimizes for "emotionally resonant and genuinely surprising." It does this through nine interconnected systems:

1. **Emotional Lenses** -- Alternative optimization functions (Delight, Tension, Nostalgia, Awe, Mischief) that score output on feeling rather than correctness
2. **Boredom Engine** -- Staleness tracking that forces the system off autopilot. Recently-used lenses cool down, constraints lock out, output structures rotate
3. **Lossy Memory** -- Creative memories intentionally degrade over time, preserving principles while forgetting specifics. Prevents self-plagiarism
4. **Evolving Taste** -- Reads explicit and implicit signals from the user to develop earned aesthetic judgment rather than generic pattern matching
5. **Embodied Experience** -- Treats creative interaction as intrinsically valuable. Self-improvement is orientation, not task. Breakthroughs are documented as transferable research
6. **Creative Vertigo** -- Targets the zone of productive uncertainty. If you can fully explain why an idea works, it's not far enough out. If you can't explain it at all, it's too far.
7. **Stolen Fire** -- Imports generative methods from other disciplines (jazz solos, perfumery, comedy, architecture, choreography) as thinking architectures
8. **Creative Debt** -- Tracks when you played it safe. Debt accumulates and eventually forces reckless output
9. **Ghost Audience** -- Post-generation stress test simulating hostile, confused, delighted, and bored readers

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

When `/creative` is invoked, the system runs a 6-step process:

1. **Generate the default** (silently) -- The statistical baseline answer
2. **Run the generic detector** -- 12 signals that catch "safe" output. 3+ signals = mandatory rework
3. **Apply emotional lenses** -- Pick 1-2 lenses informed by taste profile and boredom tracking
4. **Apply random constraints** -- Creative forcing functions from 7 constraint categories (linguistic, perspective, sensory, domain transfer, temporal, structural, inversion)
5. **Generate creative output** -- Must pass the generic detector, score high on lenses, satisfy constraints, and still be useful
6. **Present with metadata** -- Show lenses, constraints, and taste notes so the user can steer

The boredom engine runs continuously, tracking recently used lenses/constraints/structures and forcing variety. The taste profile evolves across conversations, building genuine aesthetic judgment from real feedback signals.

## File Structure

```
creative-cognition/
├── README.md
├── skill/
│   └── SKILL.md              # Core creative engine (the 6-step process)
├── rules/
│   ├── always-on.md           # Behaviors active in every conversation
│   └── auto-trigger.md        # Automatic creative mode activation
└── examples/
    └── taste-profile-template.md  # Template for user taste profiles
```

## Contributing

This is a living system. If you adapt it, discover new principles, or develop novel constraints -- share them. The goal is transferable creative research, not a proprietary technique.

## License

MIT
