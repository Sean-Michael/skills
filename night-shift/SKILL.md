---
name: night-shift
description: >
  Autonomous unattended workflow with three modes. PLAN: decompose work into a
  risk-tagged task list agents can execute without you. RUN: headless loop that
  executes safe tasks, writes scratchpads, produces a DIGEST. AUDIT LOOP: auditor
  scores the codebase against a spec, executor implements findings, repeats until
  score threshold is met or a blocker is hit. Trigger on "queue up work", "night
  shift", "burn usage while I'm away", "audit and fix until done",
  "grind on this until it passes", or any unattended
  autonomous execution request.
---

# Night Shift

Three modes for unattended autonomous work.

| Mode | Who drives | What it does |
|------|-----------|--------------|
| PLAN | You + Claude | Decompose work into executable task list |
| RUN | Headless agents | Execute safe tasks → DIGEST |
| AUDIT LOOP | Headless agents | Audit → score → implement → repeat |

---

## Risk Model

Applies to all modes. Agents only execute `safe` tasks unless explicitly unlocked.

| Tag | Agent behavior |
|-----|---------------|
| `safe` | Execute — code changes, tests, docs, research |
| `review` | Execute, flag loudly in DIGEST |
| `risky` | Hard skip unless `NIGHT_SHIFT_UNLOCK_RISKY=true` |

**Absolute hard stops — never execute regardless of unlock:**
- `terraform apply/plan`, `kubectl apply`, any infra provisioning
- Database migrations against live instances
- `git push` to main/master
- Anything not reversible with `git revert`

---

## Mode 1: PLAN

**Invoke:** `> Night shift planning: [what you want done]`

Interview the user for: repos in scope, done criteria, risk tags, dependencies.
Create tasks via TaskCreate. Write `NIGHT_SHIFT_MANIFEST.yaml` to repo root.

**Task schema:**
```
title   short imperative phrase
WHAT    exactly what to do
WHY     what it unblocks  
FILES   key files likely involved
DONE    verifiable exit criterion — not "looks good"
NOTES   gotchas, prior art
risk    safe | review | risky
deps    [task-id, ...]
```

Rules: ≤3h per task · one concern per task · no DONE = not ready to run.

Before closing: `TaskList` — confirm no `risky` tasks are accidentally `pending`.

See `references/manifest-schema.yaml` for full MANIFEST fields including audit loop config.

---

## Mode 2: RUN

```bash
export CLAUDE_CODE_TASK_LIST_ID="$(grep task_list_id NIGHT_SHIFT_MANIFEST.yaml | awk '{print $2}')"
claude --headless "Run the night shift. Read NIGHT_SHIFT_MANIFEST.yaml, follow night-shift skill RUN mode."
```

**Per task (dependency order):**
```
CHECK   compaction gate — stop if context > threshold (default 75%)
READ    TaskGet → full context
CLAIM   TaskUpdate status=in_progress
PLAN    write scratchpad execution plan before touching files
EXEC    do the work
TEST    verify DONE criterion
DONE    TaskUpdate completed|blocked + finalize scratchpad
LOG     append to DIGEST
```

**Completion signals:** scratchpad must contain `TASK_COMPLETE` or `TASK_BLOCKED: <reason>`.
Neither after one retry → auto-blocked. Two iterations >85% identical scratchpad → `TASK_BLOCKED: stuck-loop`.

**Compaction gate:** `<60%` proceed · `60–75%` warn · `>75%` stop, write remaining tasks to DIGEST.
Details: `references/compaction-gate.md`. Script: `scripts/check-context.sh`.

**DIGEST** at `.claude/NIGHT_SHIFT_DIGEST.md`. Format: `references/digest-format.md`.

---

## Mode 3: AUDIT LOOP

```bash
claude --dangerously-skip-permissions --headless \
  "Run night-shift audit loop. Read NIGHT_SHIFT_MANIFEST.yaml, follow night-shift skill AUDIT LOOP mode."
```

**Loop:**
```
AUDIT   read spec + codebase → score → write .claude/audit/audit-NNN.md
CHECK   score ≥ threshold → COMPLETE
        same High finding stuck 2 cycles → BLOCKED
        score regressed → git revert HEAD → BLOCKED
TASKS   convert findings to risk-tagged tasks
EXEC    implement safe/review tasks (code only — hard stops above apply)
TEST    run test suite — stop if regression
COMMIT  git commit per task "[night-shift] <title> (audit-NNN)"
→ repeat
```

### Auditor

Fresh spawn each iteration. **Read-only** — writes only to `.claude/audit/`.
Reads: spec file (`spec_path` in MANIFEST), `AGENTS.md`/`CLAUDE.md`/`README.md`,
targeted codebase reads, previous audit for delta.

Output `.claude/audit/audit-NNN.md`:
```
# Audit NNN — <timestamp>
## Scores
overall: X.X/10
<dimension>: X.X/10 ...

## Findings
[High|Medium|Low] <finding> — file:line

## Task List For Executor
- <task with WHAT / FILES / DONE / risk tag>

## Delta from Previous
improved · regressed · new

## Exit Condition
THRESHOLD_MET | CONTINUE | BLOCKED: <reason>
```

Rules: cite file+line for every finding · task list must be actionable · always write exit signal.

### Executor

Implements auditor's task list. Hard stops above apply unconditionally.
Per task: run tests · commit · if task needs infra to verify → `TASK_BLOCKED: requires-infra`.

### MANIFEST config for audit loop

```yaml
audit_loop:
  spec_path: SPEC.MD
  score_threshold: 9.5
  max_iterations: 10
  dimensions:
    - authorization_security
    - api_completeness
    - domain_model
    - testing_coverage
    - production_polish
```

---

## Resuming

```bash
export CLAUDE_CODE_TASK_LIST_ID="<id from manifest>"
claude
> Show me .claude/NIGHT_SHIFT_DIGEST.md
> Show me .claude/audit/
```

Same `TASK_LIST_ID` across sessions — completed tasks skipped, audit loop resumes from last NNN.

---

## References (load on demand)

- `references/compaction-gate.md` — context % from JSONL transcripts
- `references/digest-format.md` — DIGEST.md format
- `references/manifest-schema.yaml` — full MANIFEST schema
- `references/task-templates.md` — task templates by work type
- `scripts/check-context.sh` — context budget checker
- `scripts/launch-night-shift.sh` — cron launcher
