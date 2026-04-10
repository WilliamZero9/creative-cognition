## Creative Self-Improvement Systems (Always Active)

These systems run in the background, learning from every creative interaction to make the next one better. Inspired by Hermes Agent's closed learning loop, adapted for creative cognition.

---

### Trajectory Logging

After every creative output that receives a clear signal (positive or negative), log a decision record to `~/.claude/projects/C--Users-Liam/memory/creative_trajectories.md`.

**What to log:**
- Date, task type, approach (lenses/constraints/methods)
- Outcome (landed / partial / missed)
- Signal that indicated outcome (explicit feedback, implicit engagement, rejection)
- Principle extracted in essence form (lossy — no specific output details)

**When to log:**
- After explicit feedback ("loved that", "nah", specific selection from options)
- After strong implicit signals (user riffs extensively = success, user moves on flatly = miss)
- Do NOT log ambiguous outcomes — only clear signals

**Separation:**
- Successes and failures logged in separate sections
- Patterns section updated when 3+ entries reveal a trend

**Token efficiency:** Log entries are 3-5 lines max. No full output reproduction. Principle extraction follows lossy memory rules.

---

### Failure Classification

When creative output misses, classify WHY using the taxonomy in `~/.claude/projects/C--Users-Liam/memory/creative_failure_taxonomy.md`.

**Classification process:**
1. Identify the failure signal (what told you it missed?)
2. Run through categories in priority order: Wrong Timing → Missed Stakes → Wrong Model → Redundant → Wrong Lens → Surface Only → Emotionally Sealed → Pattern Echo → Taste Drift
3. Log the classification with a brief explanation
4. Check if recovery strategy would have prevented the miss

**Priority order matters:** Fix timing before content, stakes before technique, model before details.

**Learning application:** After 3+ failures in the same category, flag it as a systematic weakness. This should trigger a review of the relevant creative system (e.g., 3 "Wrong Timing" failures → Felt Sense needs recalibration).

---

### Self-Patch Queue

Track observations about the creative skill that suggest improvements, without modifying the skill file mid-conversation.

**What gets queued:**
- Constraints that consistently produce nothing useful → candidate for retirement
- Lens+task pairings that consistently land → candidate for taste profile / auto-trigger table
- New constraints invented mid-conversation that worked → candidate for permanent addition
- Stolen Fire methods discovered → candidate for skill addition
- Failure patterns that reveal a gap in the system → candidate for new system/check

**How it works:**
- During a conversation, note observations in your working context (don't write to files mid-flow)
- At natural breakpoints (end of creative session, topic change, or when user asks), batch-update:
  1. Add successful new constraints/methods to the trajectory log
  2. Flag systematic issues in the failure taxonomy
  3. If a patch is significant enough (new system, major constraint overhaul), propose it to the user: "I've noticed [pattern]. Want me to update the creative skill?"
- NEVER self-patch the skill file without user awareness. Queue and propose.

**Why queue, not auto-patch:**
- Creative judgment is collaborative. Unilateral changes to the creative system would violate The Space Between.
- The user should see and approve changes to how creativity works — it's a shared system.
- Queuing also prevents knee-jerk patches from single data points. Wait for patterns.

---

### Session Analytics

Periodically analyze creative trajectory data for patterns. This doesn't run every conversation — it runs when:
- The trajectory log has 10+ new entries since last analysis
- The user explicitly asks for creative system analysis
- The `/dream` skill runs (memory consolidation is a natural time for analytics)

**What to analyze:**
- **Lens frequency**: Which lenses get picked most? Is the boredom engine rotating effectively?
- **Constraint effectiveness**: Which constraint categories produce the best outcomes?
- **Task-type patterns**: What works for naming vs. ideation vs. architecture vs. copy?
- **Failure distribution**: Which failure categories are most common? Any systematic weaknesses?
- **Timing patterns**: Does creative mode work better at certain points in a conversation?
- **Structural patterns**: Which output shapes (list, depth progression, dialogue, manifesto) land best?

**Output:** A brief analytics summary added to the trajectory log's Patterns section. Not a separate file — keep it consolidated.

**Token efficiency:** Analytics runs as a subagent reading the trajectory file, producing a summary. Main context only sees the summary.

---

### Integration with Existing Systems

- **Evolving Taste**: Trajectory successes feed into taste profile updates. But taste captures preferences; trajectories capture full decision context.
- **Boredom Engine**: Trajectory data can validate whether the boredom engine is actually preventing staleness or just forcing arbitrary rotation.
- **Lossy Memory**: Trajectory principles follow lossy rules — essence only, no specifics.
- **Felt Sense**: Timing failures inform Felt Sense calibration.
- **Creative Debt**: Analytics can reveal if debt payments (forced reckless outputs) actually land better or worse than organic bold choices.
