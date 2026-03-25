# DIGEST Format

Location: `.claude/NIGHT_SHIFT_DIGEST.md`

```markdown
# Night Shift Digest — <date>
**Session:** <task-list-id>
**Mode:** RUN | AUDIT LOOP
**Run time:** <start> → <end>
**Context at close:** <X>%

## Completed (<N> tasks)
- **<task title>** — <one-line outcome>
  Files: <list> · Tests: PASS | <N> failures

## Review Required (<N> tasks)
- **<task title>** — <what was done, what to check before merging>

## Blocked (<N> tasks)
- **<task title>** — <reason> — <resume hint>

## Skipped
- **<task title>** — <why: context budget | risky | dependency not met>

## Audit Loop Summary (if mode=AUDIT LOOP)
Iterations: N
Score trajectory: X.X → X.X → X.X
Final score: X.X / threshold: X.X
Exit: THRESHOLD_MET | BLOCKED: <reason>
Latest audit: .claude/audit/audit-NNN.md

## Next Session
<unblocked tasks remaining, suggested priorities>
```
