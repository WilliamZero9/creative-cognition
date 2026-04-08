# Creative Cognition for AI

**What if AI creativity isn't a capability problem — it's an optimization problem?**

Large language models are brilliant at producing the statistically most likely good answer. That's incredible for analysis, coding, and factual work. But for creative work, "most likely good" is a synonym for "generic."

This framework replaces the default optimization target. Instead of asking "what's the most likely correct answer?", it asks: **"what scores highest on a specific emotional dimension?"**

---

## The Theory

Here's the insight: human emotions aren't just reactions. They're alternative scoring functions.

When a musician writes a melody that gives you chills, they're not optimizing for "most statistically pleasant arrangement of notes." They're optimizing for awe — for the feeling of encountering something vast enough to recalibrate your sense of what music can do.

When a comedian writes a joke that catches you completely off guard, they're optimizing for mischief — for the pleasure of breaking a rule you didn't know existed.

When a novelist writes a sentence that makes you put the book down and stare at the ceiling, they're optimizing for tension — for productive discomfort that forces you to reconsider something you took for granted.

AI can do this too. It just needs to be told to stop optimizing for "likely correct" and start optimizing for something else.

---

## The Five Emotional Lenses

Each lens is an alternative objective function:

| Lens | Optimizes For | Asks |
|------|--------------|------|
| **Delight** | Surprise + warmth | Would this make someone smile involuntarily? |
| **Tension** | Productive discomfort | Does this challenge an assumption? |
| **Nostalgia** | Resonance with experience | Does this name a feeling you've had but never articulated? |
| **Awe** | Scale and wonder | Does this reveal hidden vastness? |
| **Mischief** | Playful rule-breaking | Does this work even though it shouldn't? |

These combine into compound emotions — **bittersweet** (nostalgia + tension), **wonder** (awe + delight), **rebellion** (mischief + tension), and more. Each compound produces creative output with a distinct character that no single lens achieves alone.

---

## The Generic Detector

Before any creative output ships, it runs through a 12-point detector for boring, predictable work:

- Uses the first metaphor that comes to mind?
- Follows the expected structure?
- All options sound like the same template?
- Nothing makes you uncomfortable?
- Everything is "safe"?
- Could have been written by any AI for anyone?

If 3+ signals fire, the output gets reworked through an emotional lens.

---

## Creative Constraints

59 forcing functions across 7 categories that push output away from the path of least resistance:

- **Linguistic**: "Make it one syllable." "Use a word that doesn't exist yet."
- **Perspective**: "What would a 5-year-old call this?" "How would an alien describe it?"
- **Sensory**: "What color is this idea?" "Name it after a texture."
- **Domain Transfer**: "Name it like it's a spell." "Name it like a weather phenomenon."
- **Temporal**: "What would this be called in a dream?" "Name it like an ancient ritual."
- **Structural**: "It must be a question." "Two words that contradict each other."
- **Inversion**: "Name it after what's missing when it's gone." "Name the side effect, not the main effect."

Constraints aren't prisons. They're trampolines. If one produces garbage, throw it away and pick another.

---

## Installation

This framework is designed for [Claude Code](https://docs.anthropic.com/en/docs/claude-code).

### 1. Install the skill

Copy `~/.claude/skills/creative-engine.md` to your Claude Code skills directory. This makes the `/creative` slash command available.

### 2. Reference data (optional)

The JSON files in this repo (`emotions/`, `constraints/`) are the structured data behind the skill. They're useful for:
- Building tools that programmatically select lenses/constraints
- Extending the framework with your own emotions and constraints
- Understanding the theory in detail

### 3. Use it

```
/creative
```

This activates creative mode. All subsequent creative output (naming, brainstorming, writing, ideation) runs through the emotional lens pipeline.

```
/creative tension
```

Activate with a specific lens.

```
/creative off
```

Return to normal mode.

You can also steer mid-conversation:
- "More mischief" — switch to the mischief lens
- "That's too wild" — dial back to subtle intensity
- "Wilder" — crank up to intense

---

## Project Structure

```
creative-cognition/
  emotions/
    core_emotions.json       # 5 emotional lenses with scoring criteria
    compound_emotions.json   # 10 compound emotions from lens combinations
  constraints/
    random_constraints.json  # 59 creative forcing functions in 7 categories
  detectors/
    generic_detector.md      # 12-point checklist for boring output
  README.md                  # You're here
  LICENSE                    # MIT
```

---

## Why This Works

The fundamental problem with AI creativity isn't capability — it's incentive. LLMs are trained to produce likely output. "Likely" and "creative" are frequently at odds.

Creative Cognition works by:

1. **Making the default visible.** The generic detector forces the model to see its own pattern-matching, which is the first step to breaking it.
2. **Providing alternative objectives.** Emotional lenses give the model something specific to optimize for that isn't "most likely correct."
3. **Introducing productive randomness.** Constraints break the path of least resistance without being random — they're structured disruptions.
4. **Maintaining quality gates.** The detector + lenses + constraints pipeline produces creative output that's still useful. Creativity without utility is just noise.

---

## Contributing

This is an evolving framework. If you discover new emotional lenses, constraints, or detector signals, open a PR. The best additions are ones that feel obvious in retrospect — "how was that not already here?"

---

## License

MIT. Make weird things.
