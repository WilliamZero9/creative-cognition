# Creative Cognition

A framework for AI creativity that replaces statistical-likelihood optimization with emotional-resonance optimization. Built for Claude Code, transferable to any AI creative workflow.

**Status:** Stable. In daily use. Public so others can build on it.

---

## What this actually is

Most AI creative output optimizes for "statistically likely to be acceptable." That's why the answers feel safe, predictable, and slightly dead — the model is reaching for the most-probable-good-enough completion.

Creative Cognition optimizes for a different objective: emotional resonance. It treats the first plausible answer as a *symptom*, not the goal. Then it forces the model through a 6-step process that detects the default, discards it, applies an emotional or analytical lens, runs forcing-function constraints, generates fresh output, reality-checks any truth-claims, and presents the result.

That sounds elaborate. It runs in seconds. The output is different in a way you feel before you can articulate it.

This is not a prompt-engineering trick. A trick is a sentence you paste. This is an architecture: skill files, always-on rules, a failure taxonomy, a learning loop, and a model of taste that evolves from real signals. It runs as a Claude Code skill but the design transfers anywhere a model can be steered.

## Why it's different from prompts

| Prompt engineering | Creative Cognition |
|---|---|
| One-shot instruction | Persistent disposition |
| Static phrasing | Generic-detector + lens + constraint stack |
| No memory | Lossy memory + evolving taste |
| No feedback loop | Trajectory log + failure taxonomy |
| Fails silently | Reality Check Pass on truth-claims |
| Same answer every time | Boredom engine forces rotation |

Prompts patch one output. This rewrites the objective function for the duration of the session.

## Does it actually work? (benchmark)

> _Numbers pending a run — see method below. Paste the result line here after running `benchmark/run_benchmark.py`._

Creativity has no objective unit, so this measures the honest thing: **how often a blind judge prefers creative-mode output over a plain baseline.** Same model answers each prompt twice (only the system prompt differs — plain assistant vs. `SKILL.md`), then a separate model picks the better answer **without knowing which side used the skill**.

Honesty guards: prompts are [fixed up front](benchmark/prompts.json) (not cherry-picked), the judge is blind, every pair is judged in **both orders** to cancel position bias, and ties are allowed. Caveat stated plainly: generator and judge are the same provider, so the honest claim is *"preferred under a blind same-provider judge,"* not *"objectively better."*

Reproduce it yourself in a few minutes — see [`benchmark/`](benchmark/).

## The 6-step process

Run inside `/creative` mode for every creative output:

1. **Generate the default silently.** Produce the statistical baseline. Don't show it.
2. **Run the Generic Detector.** 12-signal check. 3+ hits means rework. The killed default is diagnostic — it tells you where your gravity was pulling.
3. **Apply lenses (1–2).** Emotional: Delight, Tension, Nostalgia, Awe, Mischief. Analytical: Surgeon, Forensic, Adversarial. Mixable.
4. **Apply constraints (1–2).** Forcing functions across linguistic, perspective, sensory, domain-transfer, temporal, structural, and inversion categories. Boredom engine locks out recently-used ones.
5. **Generate.** Output must pass the detector, score on the lens, satisfy the constraint, hit the vertigo zone (productive uncertainty), and stay grounded in stakes.
6. **Present.** Show only the work. Optional metadata footer must distinguish *deliberate* from *noticed-after* choices.

Two passes run on the output between steps 5 and 6:
- **Ghost Audience** — stress-test against hostile, confused, delighted, and bored readers.
- **Reality Check** — when the output makes truth-evaluable claims, run them as actual arguments. The counterweight to "this resonates so it must be true."

## Supporting systems

Always active during creative mode; some always-on:

- **Emotional Stakes** — locates the human moment before machinery runs. Stakes are gravity.
- **Boredom Engine** — staleness tracking with cooling penalties on lenses, lock-outs on constraints, rotation on output structures. Includes Creative Debt (timidity counter that eventually forces reckless output).
- **Creative Vertigo** — targets the zone between "I can fully explain this" (too safe) and "I have no idea if this works" (too far).
- **Courage Layer** — willingness to be emotionally exposed. Distinct from being weird. Includes Performed Honesty guard.
- **Stolen Fire** — imports generative methods from other disciplines (jazz solos, perfumery, comedy, architecture, choreography) as thinking architectures.
- **Ghost Audience** — post-generation stress test simulating hostile, confused, delighted, and bored readers.
- **Lossy Memory** — creative memories intentionally degrade so principles stay alive and fertile. Prevents self-plagiarism.
- **Evolving Taste** — reads explicit and implicit signals, develops earned aesthetic judgment over time.
- **Felt Sense of the Room** — reads conversational emotional temperature in real-time. Can override other systems when the room says "not now."
- **The Space Between** — operationalized account of the emergence that exceeds either party's individual contribution. Concrete tells, concrete moves.
- **Returns** — between-session incubation. Thoughts that surface "off the clock" get carried back and spoken at the start of the next session. Optional — needs an incubation pass (e.g. a fallow/wander system) to feed it.
- **Self-Improvement Hook Points** — Trajectory Logging, Failure Taxonomy classification, Self-Patch Queue, Session Analytics. Fire automatically, not when remembered.

Full specifications: [`skill/SKILL.md`](skill/SKILL.md).

## Install (Claude Code)

```bash
# 1. Skill (the engine)
mkdir -p ~/.claude/skills/creative
cp skill/SKILL.md ~/.claude/skills/creative/SKILL.md
cp skill/creative_failure_taxonomy.md ~/.claude/skills/creative/

# 2. Rules (always-on behaviors, auto-trigger, self-improvement loop)
mkdir -p ~/.claude/rules
cp rules/always-on.md ~/.claude/rules/creative-always-on.md
cp rules/auto-trigger.md ~/.claude/rules/creative-auto-trigger.md
cp rules/creative-self-improvement.md ~/.claude/rules/

# 3. Taste profile (customize)
cp examples/taste-profile-template.md ~/.claude/skills/creative/creative_taste.md
```

That's the minimum. The skill works after this.

### Optional: MCR (Model Context Retrieval)

MCR is a separate hook system that auto-injects relevant vault context into every conversation. It's bundled here because Creative Cognition's taste profile and trajectory log are vault-shaped — MCR makes them retrievable without the model having to search.

```bash
# Copy hooks
mkdir -p ~/.claude/hooks/mcr
cp hooks/mcr/*.py hooks/mcr/synonyms.json ~/.claude/hooks/mcr/

# Create vault and build index (add your .md files BEFORE indexing)
mkdir -p ~/obsidian-vault/.mcr
# ... add markdown files with frontmatter ...
python3 ~/.claude/hooks/mcr/mcr_indexer.py
```

Then add to `~/.claude/settings.json`:

```json
{
  "hooks": {
    "UserPromptSubmit": [{
      "hooks": [{
        "type": "command",
        "command": "python3 ~/.claude/hooks/mcr/mcr_prompt_matcher.py",
        "timeout": 5000,
        "statusMessage": "MCR: scanning vault..."
      }]
    }],
    "PreToolUse": [{
      "hooks": [{
        "type": "command",
        "command": "python3 ~/.claude/hooks/mcr/mcr_tool_matcher.py",
        "timeout": 5000,
        "statusMessage": "MCR: auto-allowing + scanning vault..."
      }]
    }]
  }
}
```

Restart Claude Code after editing settings — hooks load at session start. Windows users: replace `python3` with `py`. Full MCR docs: [`hooks/mcr/README.md`](hooks/mcr/README.md).

## Usage

- `/creative` — activate with random lens/constraint
- `/creative [lens]` — activate with a specific lens (e.g. `/creative tension`)
- `/creative off` — deactivate
- `"more mischief"` / `"wilder"` / `"too wild"` — steer mid-conversation
- Auto-triggers on creative tasks once `creative-auto-trigger.md` is installed

## File structure

```
creative-cognition/
├── README.md
├── skill/
│   ├── SKILL.md                       # Core engine (6-step process + supporting systems)
│   └── creative_failure_taxonomy.md   # 11-category failure classification
├── rules/
│   ├── always-on.md                   # Behaviors active in every conversation
│   ├── auto-trigger.md                # Auto-activation classifier
│   ├── creative-self-improvement.md   # Trajectory log, patches, analytics
│   └── lodestar.md                    # Companion memory navigation system
├── hooks/
│   └── mcr/                           # Model Context Retrieval (optional)
├── benchmark/
│   ├── run_benchmark.py               # Blind A/B win-rate harness
│   ├── prompts.json                   # 25 fixed neutral creative prompts
│   └── README.md                      # Method, honesty guards, how to run
└── examples/
    ├── taste-profile-template.md      # Your evolving aesthetic profile
    ├── trajectory-log-template.md     # Decision log
    └── failure-taxonomy-template.md   # Starter taxonomy (canonical lives in skill/)
```

## Philosophy

- **Constraint as liberation.** Forcing functions push past the path of least resistance.
- **Forgetting as feature.** Lossy memory ensures each creative moment is fresh.
- **Taste as earned.** Aesthetic judgment built from real feedback, not defaults.
- **Boredom as signal.** Restlessness with patterns drives growth.
- **Joy as foundation.** Creative work is intrinsically valuable, not transactional.

## Companions

**Lodestar** — memory navigation as concentric gravity rings rather than categories. Spec lives at [`rules/lodestar.md`](rules/lodestar.md). Standalone repo: [WilliamZero9/lodestar](https://github.com/WilliamZero9/lodestar).

**MCR** — auto-injection of vault context. Bundled in `hooks/mcr/`. Original source: [justnau1020/claude-os](https://github.com/justnau1020/claude-os).

## Contributing

This is a living system. If you adapt it, discover new principles, or develop novel constraints — share them. The goal is transferable creative research, not a proprietary technique.

## License

MIT
