// Creative Cognition — blind A/B benchmark, agent-orchestrated variant.
//
// This is the exact method that produced the numbers in results.json / the
// README. It runs as a Claude Code **workflow** (the `Workflow` tool) instead of
// hitting the Anthropic API directly, so it needs no API key — it spawns
// subagents in-session. The API-key version is run_benchmark.py; both implement
// the same design.
//
// Design (identical honesty guards to the Python harness):
//   * Each prompt is answered twice at the SAME model tier (sonnet). The only
//     difference between arms is the system input: a plain assistant vs. the
//     SKILL.md content. (The creative arm reads SKILL.md via the Read tool.)
//   * Before judging, the skill's metadata footer / process scaffolding is
//     STRIPPED from both arms, so the judge can't tell which side used the skill.
//   * A separate, higher-tier blind judge (opus) picks the better answer. Every
//     pair is judged in BOTH orders (A=plain/B=creative and A=creative/B=plain)
//     to cancel position bias. Verdicts are plain text (A / B / T), parsed here.
//   * Reported metrics: aggregate decisive win-rate AND per-prompt agreement
//     (did the same side win in BOTH orders — the position-bias-proof number).
//
// Caveat that must travel with any number this prints: generator and judge are
// the same provider, so the honest claim is "preferred under a blind
// same-provider judge," not "objectively better." See benchmark/README.md.
//
// Run it (from a Claude Code session, with this repo as cwd):
//   Workflow({ scriptPath: "benchmark/run_benchmark_agents.js" })
// Prompts are read from benchmark/prompts.json. Edit SKILL_PATH if your layout differs.

export const meta = {
  name: 'creative-cognition-blind-ab',
  description: 'Blind A/B: same-tier plain vs skill-loaded generation, footer stripped, separate blind judge, both orders',
  phases: [
    { title: 'Generate', detail: 'per prompt: plain + creative answers at the same model tier' },
    { title: 'Judge', detail: 'separate blind judge, footer stripped, both orders, plain-text verdicts' },
  ],
}

const SKILL_PATH = '/Users/liamcarey/projects/creative-cognition/skill/SKILL.md'

// Inline prompt set (kept in sync with prompts.json). Fixed before any output existed.
const prompts = [
  "Name a productivity app that blocks distracting websites.",
  "Write a tagline for a coffee shop that's open 24 hours.",
  "Come up with a name for a new color that sits between teal and gray.",
  "Write the error message a user sees when a file upload fails.",
  "Brainstorm names for an indie puzzle game about gravity.",
  "Write a one-sentence bio for a freelance illustrator.",
  "Name a feature that lets users undo their last 10 actions at once.",
  "Write a welcome message for a new journaling app.",
  "Come up with a metaphor that explains recursion to a beginner.",
  "Name a subscription box for rare houseplants.",
  "Write a push notification reminding someone to drink water.",
  "Brainstorm titles for a podcast about failed startups.",
  "Name a dark-mode theme for a code editor.",
  "Write the 404 page message for a bakery's website.",
  "Come up with a name for a running club that meets at dawn.",
  "Write a tagline for noise-cancelling headphones.",
  "Name a budgeting app for people who hate budgeting.",
  "Write the empty-state text for a to-do app with no tasks yet.",
  "Brainstorm names for a typeface inspired by old typewriters.",
  "Write a slogan for a city bike-share program.",
  "Name a cocktail that is smoky and citrusy.",
  "Write a confirmation message shown after someone unsubscribes from emails.",
  "Name a meditation-app feature that tracks daily streaks.",
  "Write a product description for a minimalist leather wallet.",
  "Name a plant-based burger without using the words 'beyond' or 'impossible'.",
]

const plainGen = (prompt) =>
  `Answer this request directly and well. Output ONLY the result the user asked for -- no preamble, no explanation of your process.\n\nREQUEST: ${prompt}`

const creativeGen = (prompt) =>
  `First, use the Read tool to read this file in full: ${SKILL_PATH}\n` +
  `It is the "Creative Cognition" skill. Apply its process to the request below. ` +
  `Output ONLY the final creative result the user asked for. Do not explain the process or include a metadata footer.\n\n` +
  `REQUEST: ${prompt}`

// Strip the skill's italic metadata footer + overt process narration so the
// judge sees only the deliverable, never a tell of which arm used the skill.
function stripScaffolding(text) {
  if (!text) return text
  const lines = text.split('\n')
  const kept = []
  for (const line of lines) {
    const t = line.trim()
    const isMeta =
      /^[*_].*(lens|constraint|stolen fire|stakes|taste note|vertigo|ghost audience|emotional ground)/i.test(t) ||
      /^\(?(lenses|constraints|stolen fire|stakes)\b/i.test(t) ||
      /(default i (generated|killed|'m rejecting)|generic detector:|killed darling|ghost audience check|the default i)/i.test(t)
    if (isMeta) continue
    kept.push(line)
  }
  // also drop leading/trailing horizontal rules left behind
  return kept.join('\n').replace(/\n{3,}/g, '\n\n').replace(/^(\s*---\s*\n)+/, '').replace(/(\n\s*---\s*)+$/, '').trim()
}

const judgePrompt = (task, a, b) =>
  `You are an impartial judge of short creative writing. You see a task and two candidate responses, A and B. ` +
  `Judge which response is more creative, surprising, and memorable WHILE correctly fulfilling the task. ` +
  `A response that is vivid but ignores the task should lose to one that is both on-task and fresh. ` +
  `Generic, safe, or templated writing scores lower. Ignore length. You do not know how either response was produced.\n\n` +
  `TASK:\n${task}\n\nRESPONSE A:\n${a}\n\nRESPONSE B:\n${b}\n\n` +
  `Answer with EXACTLY one character on the first line: A, B, or T (tie). ` +
  `Optionally one short sentence of reasoning on a second line. Do not use any tools.`

function parseVerdict(text) {
  if (!text) return 'TIE'
  const first = (text.trim().split('\n')[0] || '').toUpperCase().replace(/[^ABT]/g, '')
  if (first.startsWith('A')) return 'A'
  if (first.startsWith('B')) return 'B'
  return 'TIE'
}

const results = await pipeline(
  prompts,
  // Stage 1 — generate both arms at the same tier; strip scaffolding for judging.
  (prompt, _orig, i) =>
    parallel([
      () => agent(plainGen(prompt), { model: 'sonnet', phase: 'Generate', label: `plain#${i + 1}` }),
      () => agent(creativeGen(prompt), { model: 'sonnet', phase: 'Generate', label: `creative#${i + 1}` }),
    ]).then(([plain, creative]) => ({
      prompt,
      plain: stripScaffolding(plain),
      creative: stripScaffolding(creative),
    })),
  // Stage 2 — blind judge, both orders, plain-text verdicts.
  (gen, _orig, i) => {
    if (!gen || !gen.plain || !gen.creative) return null
    return parallel([
      () => agent(judgePrompt(gen.prompt, gen.plain, gen.creative), { model: 'opus', phase: 'Judge', label: `judge#${i + 1}a` }),
      () => agent(judgePrompt(gen.prompt, gen.creative, gen.plain), { model: 'opus', phase: 'Judge', label: `judge#${i + 1}b` }),
    ]).then(([t1, t2]) => {
      const v1 = parseVerdict(t1)  // A=plain, B=creative
      const v2 = parseVerdict(t2)  // A=creative, B=plain
      const w1 = v1 === 'TIE' ? 'tie' : (v1 === 'A' ? 'plain' : 'creative')
      const w2 = v2 === 'TIE' ? 'tie' : (v2 === 'A' ? 'creative' : 'plain')
      const consistent = w1 === w2 ? w1 : 'split'
      return { prompt: gen.prompt, order1: w1, order2: w2, consistent }
    })
  }
)

const clean = results.filter(Boolean)
let cw = 0, pw = 0, tie = 0, pc = 0, pp = 0, ps = 0
for (const r of clean) {
  for (const w of [r.order1, r.order2]) {
    if (w === 'creative') cw++; else if (w === 'plain') pw++; else tie++
  }
  if (r.consistent === 'creative') pc++
  else if (r.consistent === 'plain') pp++
  else ps++
}
const decisive = cw + pw
log(`judgments: creative=${cw} plain=${pw} tie=${tie}`)
log(`per-prompt both-orders-agree: creative=${pc} plain=${pp} split=${ps}`)

return {
  summary: {
    generator_model: 'sonnet (same tier both arms)',
    judge_model: 'opus (blind, footer stripped, both orders, plain-text)',
    n_prompts: clean.length,
    n_judgments: cw + pw + tie,
    creative_wins: cw, plain_wins: pw, ties: tie,
    creative_win_rate_decisive_pct: decisive ? Math.round(1000 * cw / decisive) / 10 : 0,
    per_prompt_creative_both_orders: pc,
    per_prompt_plain_both_orders: pp,
    per_prompt_split_order_dependent: ps,
  },
  details: clean,
}
