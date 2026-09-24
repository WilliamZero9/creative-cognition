# Creative Cognition

A project that should be able to be applied to any AI and make it more creative and not necessarily more accurate or smarter unless its a big LLM.

---

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
│   ├── run_benchmark.py               # Blind A/B win-rate harness (API key)
│   ├── run_benchmark_agents.js        # Same method as a Claude Code workflow (no key)
│   ├── prompts.json                   # 25 fixed neutral creative prompts
│   ├── results.json                   # Latest run's full per-prompt data
│   └── README.md                      # Method, honesty guards, how to run
└── examples/
    ├── taste-profile-template.md      # Your evolving aesthetic profile
    ├── trajectory-log-template.md     # Decision log
    └── failure-taxonomy-template.md   # Starter taxonomy (canonical lives in skill/)
```

## Companion

**Lodestar** — memory navigation as concentric gravity rings rather than categories. Spec lives at [`rules/lodestar.md`](rules/lodestar.md). Standalone repo: [WilliamZero9/lodestar](https://github.com/WilliamZero9/lodestar).

## Contributing

This is a living system. If you adapt it, discover new principles, or develop novel constraints — share them. The goal is transferable creative research.

## License

MIT
