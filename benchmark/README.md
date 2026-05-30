# Benchmark

A blind A/B test of whether Creative Cognition output is actually preferred over
a plain baseline — not a self-graded claim.

## What it measures

For each prompt, the **same model** answers twice with identical settings; the
only difference is the system prompt:

- **plain** — "You are a helpful assistant."
- **creative** — `skill/SKILL.md` loaded as the system prompt.

A separate **judge** model then picks the better answer **without being told
which side used the skill**. The headline number is how often the creative side
wins.

## Why you can trust the number (and where to be skeptical)

Honest design choices:

- **Prompts are fixed up front** in [`prompts.json`](prompts.json) — 25 diverse
  open-ended creative tasks chosen *before* any output existed, so they aren't
  cherry-picked to flatter the skill. None has an objectively correct answer.
- **The judge is blind.** It sees "Response A / Response B" and never learns how
  either was produced. The skill's own vocabulary is never shown to it.
- **Position bias is cancelled.** Every pair is judged twice — once plain-first,
  once creative-first. A judge that just always picks "A" wins nothing.
- **Ties are allowed.** The judge is not forced to choose.

Be skeptical because:

- **Generator and judge are the same provider (Anthropic).** A model can mildly
  favor its own house style. Blind + position-controlled A/B mitigates the worst
  of it, but the honest framing is *"preference rate under a blind same-provider
  judge,"* not *"objectively better."* For a stronger claim, use a different
  provider's model as judge, or human judges.
- **Small N.** 25 prompts is enough to see a clear signal, not enough for tight
  confidence intervals. Treat it as directional.

## How to run it

You need Python and an Anthropic API key. The script only ever *reads* the key
from your environment — never paste a key into a file or a chat.

```bash
pip install anthropic
export ANTHROPIC_API_KEY=sk-ant-...        # set in YOUR shell; the script reads it

cd benchmark

python3 run_benchmark.py --dry-run         # 1. verify wiring, no API calls, free
python3 run_benchmark.py --limit 3         # 2. cheap smoke test (~12 API calls)
python3 run_benchmark.py                    # 3. full run (25 prompts, 50 judgments)
```

The full run prints a summary, writes per-prompt detail to `results.json`, and
prints a ready-to-paste README line with the real numbers.

### Options

- `--generator-model X` / `--judge-model Y` — pick the models (defaults:
  generator `claude-sonnet-4-6`, judge `claude-opus-4-8`).
- `--temperature` — generation temperature, applied equally to both sides
  (default 1.0).
- `--limit N` — only use the first N prompts (for a cheap test).

### Cost

Full run ≈ 25 prompts × (2 generations + 2 judgments) = ~100 API calls. Usually
well under ~$1, depending on the models. The smoke test is a few cents.

## Reproducing / extending

- Swap in your own prompts by editing `prompts.json` (note in the README if they
  are maintainer-chosen rather than neutral).
- For the strongest claim, point `--judge-model` at a non-Anthropic model (you'd
  adapt the `judge()` call to that provider's SDK) so the judge has no
  home-team bias.
- `results.json` keeps every judge verdict and its one-line justification, so
  anyone can audit *why* each call went the way it did.
