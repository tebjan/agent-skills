---
name: ralph-orchestrator
description: "Orchestrates and advises on Ralph Loop automated development sessions. Use when the user wants to run ralph-loop, asks how to set up a Ralph task, wants iterative agent-driven development, says 'run this in a loop until it works', or has a task with testable acceptance criteria they want to automate. Helps write effective loop prompts, sets safe iteration limits, monitors loop progress, detects stuck loops, and advises on completion criteria. Keeps context short — the heavy work happens inside the loop."
---

# Ralph Orchestrator

Ralph Loop = a Stop hook that re-feeds the same prompt on every session exit, letting Claude iterate until a completion promise appears.

**Plugin location:** `~/.claude/plugins/cache/claude-plugins-official/ralph-loop/1.0.0/`

---

## Core Principle

The orchestrator's job is **before** and **after** the loop — not inside it. Keep this conversation context lean; the loop runs autonomously.

Three phases:
1. **Pre-flight** — define the task, write a great prompt, set limits
2. **Launch** — hand off to ralph-loop
3. **Monitor** — check progress, detect stuck loops, adjust if needed

---

## Phase 1: Pre-flight

### Assess the task

Ask if unclear (max 2 questions):
- "What's the task? One sentence."
- "How will we know it's done — tests passing, a file existing, a specific output?"

**Ralph is a good fit when:**
- Clear, verifiable completion criteria exist (tests pass, linter clean, file produced)
- Task benefits from iteration (TDD, bug fixing, code generation)
- You can walk away and let it run

**Ralph is NOT a good fit when:**
- Task requires human design decisions mid-way
- No automatic way to verify completion
- One-shot operation (use `/gsd-fast` instead)

### Draft the prompt

A good ralph prompt has four parts:

```
[TASK DESCRIPTION]
What to build/fix in concrete terms.

[SELF-CORRECTION LOOP]
Run tests after each change. If any fail, read the errors, fix them, and run again.
Check [linter/build/output] before declaring done.

[ESCAPE HATCH]
After [N-3] iterations, if still not complete:
- Document what's blocking
- List approaches tried
- Suggest alternatives

[COMPLETION PROMISE]
Output exactly: <promise>COMPLETE</promise>
Only output this when ALL criteria are unequivocally met.
```

Present the drafted prompt to the user and ask: "Does this capture what you want? Adjust anything before we launch."

### Set safe limits

Recommend `--max-iterations` based on task complexity:

| Task type | Suggested limit |
|-----------|----------------|
| Simple fix, clear criteria | 10–15 |
| Feature with tests | 20–30 |
| Greenfield small project | 30–50 |
| Complex multi-phase | 50+ (monitor closely) |

Always set a limit. Always include an escape hatch in the prompt at `limit - 3` iterations.

---

## Phase 2: Launch

Show the final command for the user to run:

```
/ralph-loop "[prompt]" --completion-promise "COMPLETE" --max-iterations N
```

Tell the user:
> "Ralph is now running. Each time Claude tries to exit, the hook re-feeds the prompt. You'll see iteration progress in git history. Come back and tell me when it finishes, gets stuck, or you want a status check."

**Do not** keep talking or consuming context during the loop. Hand off cleanly.

---

## Phase 3: Monitor

When the user reports back, check progress:

```bash
git log --oneline -20
```

### Detecting a stuck loop

Signs the loop is stuck:
- Same commit messages repeating
- Test failures not decreasing after 5+ iterations
- "attempting" the same approach repeatedly in git messages

If stuck → suggest prompt adjustment:
1. Add more specific instructions about the failing step
2. Add a hint: "The error is in [file/line] — focus there"
3. Reduce scope: break into smaller sub-tasks
4. Cancel with `/cancel-ralph` and relaunch with refined prompt

### Completion

When the completion promise fires:
- Review final state: `git log --oneline`, run tests manually
- Ask: "Was the output what you expected? Any follow-up needed?"
- Suggest: `/gsd-fast "cleanup/polish"` for any small finishing touches

---

## Windows Note

If the Stop hook fails with WSL errors, fix the hook to use Git Bash:

```json
"command": "\"C:/Program Files/Git/bin/bash.exe\" ${CLAUDE_PLUGIN_ROOT}/hooks/stop-hook.sh"
```

Edit: `~/.claude/plugins/cache/claude-plugins-official/ralph-loop/<hash>/hooks/hooks.json`
