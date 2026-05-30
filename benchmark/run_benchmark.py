#!/usr/bin/env python3
"""
Creative Cognition — blind A/B benchmark.

Measures how often a BLIND judge prefers creative-mode output over a plain
baseline, using the same model for both sides so the only variable is the skill.

Honesty design (read before trusting any number this prints):
  * Prompts are fixed in prompts.json, chosen before any output existed.
  * Each prompt is answered twice by the SAME generator model, same settings:
    once "plain" (helpful-assistant baseline), once "creative" (SKILL.md loaded
    as the system prompt). Only the system prompt differs.
  * The judge is BLIND: it sees "Response A" / "Response B" and never learns
    which side used the skill. The skill's own vocabulary ("creative mode",
    "lens", etc.) is not mentioned to the judge.
  * POSITION BIAS is controlled: every pair is judged twice, once in each order
    (plain-first and creative-first). A model that just prefers "A" can't win.
  * TIES are allowed — the judge is not forced to pick.

Known limitation (state it in the README, don't hide it): generator and judge
are the same provider (Anthropic). A model may mildly favor its own style.
Blind + position-controlled A/B mitigates the worst of it, but the honest
framing is "preference rate under a blind same-provider judge," not "objectively
better." For a stronger claim, set --judge-model to a different provider's model
(would require adapting the judge call) or use human judges.

Usage:
  export ANTHROPIC_API_KEY=...        # you set this; the script only reads it
  pip install anthropic
  python3 run_benchmark.py                       # full run (25 prompts x 2 orders)
  python3 run_benchmark.py --limit 3             # cheap smoke test
  python3 run_benchmark.py --dry-run             # no API calls; verify wiring
  python3 run_benchmark.py --generator-model X --judge-model Y

Cost: ~ (N prompts) x (2 generations + 2 judgments). 25 prompts is ~100 calls,
typically well under ~$1 depending on the models chosen.
"""

import argparse
import json
import os
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent

# Default models. Adjust to whatever you have access to.
DEFAULT_GENERATOR = "claude-sonnet-4-6"
DEFAULT_JUDGE = "claude-opus-4-8"

PLAIN_SYSTEM = "You are a helpful assistant. Answer the user's request directly and well."

CREATIVE_PREAMBLE = (
    "You are operating with the following Creative Cognition skill active. "
    "Apply its process to the user's request. Output ONLY the final creative "
    "result the user asked for (you may include the skill's brief italic "
    "metadata footer if appropriate). Do not explain the process.\n\n"
    "===== BEGIN SKILL =====\n"
)
CREATIVE_POSTAMBLE = "\n===== END SKILL =====\n"

JUDGE_SYSTEM = (
    "You are an impartial judge of short creative writing. You will see a task "
    "and two candidate responses, A and B. Judge which response is more "
    "creative, surprising, and memorable WHILE still correctly fulfilling the "
    "task. A response that is vivid but ignores the task should lose to one that "
    "is both on-task and fresh. Generic, safe, or templated writing should score "
    "lower. Ignore length. You do not know how either response was produced; "
    "judge only the text."
)

JUDGE_TEMPLATE = """TASK:
{task}

RESPONSE A:
{a}

RESPONSE B:
{b}

Which response better fulfills the task while being more creative, surprising, and memorable?
Reply on a single line with exactly one of: A, B, TIE
Then on a second line, give one short sentence of justification."""


def load_prompts(limit=None):
    data = json.loads((HERE / "prompts.json").read_text())
    prompts = data["prompts"]
    if limit:
        prompts = prompts[:limit]
    return prompts


def load_creative_system():
    skill = (REPO / "skill" / "SKILL.md").read_text()
    return CREATIVE_PREAMBLE + skill + CREATIVE_POSTAMBLE


def make_client():
    try:
        from anthropic import Anthropic
    except ImportError:
        sys.exit("Missing dependency. Run: pip install anthropic")
    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("Set ANTHROPIC_API_KEY in your environment first (the script only reads it).")
    return Anthropic()


def generate(client, model, system, prompt, temperature):
    resp = client.messages.create(
        model=model,
        max_tokens=600,
        temperature=temperature,
        system=system,
        messages=[{"role": "user", "content": prompt}],
    )
    return "".join(block.text for block in resp.content if block.type == "text").strip()


def judge(client, model, task, a_text, b_text):
    resp = client.messages.create(
        model=model,
        max_tokens=120,
        temperature=0,
        system=JUDGE_SYSTEM,
        messages=[{"role": "user", "content": JUDGE_TEMPLATE.format(task=task, a=a_text, b=b_text)}],
    )
    text = "".join(block.text for block in resp.content if block.type == "text").strip()
    verdict = text.splitlines()[0].strip().upper()
    if verdict.startswith("A"):
        return "A", text
    if verdict.startswith("B"):
        return "B", text
    return "TIE", text


def run(args):
    prompts = load_prompts(args.limit)
    creative_system = load_creative_system()

    if args.dry_run:
        print(f"DRY RUN — would evaluate {len(prompts)} prompts x 2 orders = "
              f"{len(prompts) * 2} blind judgments.")
        print(f"Generator: {args.generator_model}   Judge: {args.judge_model}")
        print(f"Creative system prompt length: {len(creative_system)} chars "
              f"(SKILL.md loaded).")
        print("First prompt:", prompts[0])
        print("No API calls made.")
        return

    client = make_client()
    rng = random.Random(args.seed)

    creative_wins = plain_wins = ties = 0
    rows = []

    for i, task in enumerate(prompts, 1):
        plain = generate(client, args.generator_model, PLAIN_SYSTEM, task, args.temperature)
        creative = generate(client, args.generator_model, creative_system, task, args.temperature)

        # Judge in BOTH orders to cancel position bias.
        for order in ("plain_first", "creative_first"):
            if order == "plain_first":
                a, b, a_is = plain, creative, "plain"
            else:
                a, b, a_is = creative, plain, "creative"
            pick, raw = judge(client, args.judge_model, task, a, b)
            if pick == "TIE":
                winner = "tie"; ties += 1
            else:
                picked_side = a_is if pick == "A" else ("creative" if a_is == "plain" else "plain")
                winner = picked_side
                if winner == "creative":
                    creative_wins += 1
                else:
                    plain_wins += 1
            rows.append({"prompt": task, "order": order, "winner": winner, "judge_raw": raw})

        done = creative_wins + plain_wins + ties
        print(f"[{i}/{len(prompts)}] creative={creative_wins} plain={plain_wins} tie={ties}  ({done} judgments)")

    total = creative_wins + plain_wins + ties
    decisive = creative_wins + plain_wins
    overall = 100 * creative_wins / total if total else 0
    head_to_head = 100 * creative_wins / decisive if decisive else 0

    summary = {
        "generator_model": args.generator_model,
        "judge_model": args.judge_model,
        "n_prompts": len(prompts),
        "n_judgments": total,
        "creative_wins": creative_wins,
        "plain_wins": plain_wins,
        "ties": ties,
        "creative_win_rate_overall_pct": round(overall, 1),
        "creative_win_rate_decisive_pct": round(head_to_head, 1),
    }
    (HERE / "results.json").write_text(json.dumps({"summary": summary, "rows": rows}, indent=2))

    print("\n================ RESULT ================")
    print(json.dumps(summary, indent=2))
    print("\nReady-to-paste README line:")
    print(f"> In a blind A/B test across {len(prompts)} neutral creative prompts "
          f"({total} position-controlled judgments), creative-mode output was "
          f"preferred {creative_wins}/{decisive} times over the plain baseline "
          f"({head_to_head:.0f}% of decisive comparisons; {ties} ties). "
          f"Generator and blind judge: {args.generator_model} / {args.judge_model}.")
    print("\nFull per-prompt detail saved to benchmark/results.json")


def main():
    p = argparse.ArgumentParser(description="Blind A/B benchmark for Creative Cognition.")
    p.add_argument("--generator-model", default=DEFAULT_GENERATOR)
    p.add_argument("--judge-model", default=DEFAULT_JUDGE)
    p.add_argument("--temperature", type=float, default=1.0,
                   help="Generation temperature, applied equally to both sides.")
    p.add_argument("--limit", type=int, default=None, help="Only use the first N prompts (smoke test).")
    p.add_argument("--seed", type=int, default=7, help="RNG seed (reserved for reproducibility).")
    p.add_argument("--dry-run", action="store_true", help="Verify wiring without any API calls.")
    run(p.parse_args())


if __name__ == "__main__":
    main()
