# Compaction Gate Reference

How agents check their context budget before starting a new task.

## Why This Matters

Context degradation is non-linear. A session at 80% context doesn't perform 20%
worse — it often performs dramatically worse because the model's attention is
saturated with prior tool outputs, scratchpad content, and task history. The gate
prevents starting a task you can't finish cleanly.

## Reading Context from JSONL Transcripts

Claude Code writes session transcripts to:

```bash
~/.claude/projects/<project-hash>/<session-id>.jsonl
```

Each line is a JSON object. Assistant turns include token counts:

```json
{
  "type": "assistant",
  "message": {...},
  "usage": {
    "cache_read": 45000,
    "cache_create": 12000,
    "input": 8000
  }
}
```

**Current context = `cache_read + cache_create + input`**

The context window is 200,000 tokens. Thresholds:

- `< 120,000` (60%) — Green: proceed
- `120,000–150,000` (60–75%) — Yellow: log warning, proceed
- `> 150,000` (75%) — Red: **stop loop**

## Shell Script Check

```bash
#!/bin/bash
# scripts/check-context.sh
# Returns: GREEN | YELLOW | RED and the usage percentage

PROJECT_HASH=$(ls ~/.claude/projects/ | head -1)  # adjust if multi-project
SESSION_FILE=$(ls -t ~/.claude/projects/$PROJECT_HASH/*.jsonl 2>/dev/null | head -1)

if [ -z "$SESSION_FILE" ]; then
  echo "GREEN (no transcript found, assuming fresh session)"
  exit 0
fi

# Get latest assistant turn with usage data
USAGE=$(grep '"type":"assistant"' "$SESSION_FILE" | \
  python3 -c "
import sys, json
lines = sys.stdin.readlines()
for line in reversed(lines):
    try:
        obj = json.loads(line)
        if 'usage' in obj:
            u = obj['usage']
            total = u.get('cache_read',0) + u.get('cache_create',0) + u.get('input',0)
            pct = total / 200000
            print(f'{total} {pct:.2%}')
            break
    except:
        pass
" 2>/dev/null)

if [ -z "$USAGE" ]; then
  echo "GREEN (could not parse usage)"
  exit 0
fi

TOKENS=$(echo $USAGE | cut -d' ' -f1)
PCT=$(echo $USAGE | cut -d' ' -f2)

if [ "$TOKENS" -lt 120000 ]; then
  echo "GREEN ($PCT used)"
elif [ "$TOKENS" -lt 150000 ]; then
  echo "YELLOW ($PCT used) — context filling, proceed with caution"
else
  echo "RED ($PCT used) — STOP: context budget exceeded"
  exit 1
fi
```

## Agent Behavior by Gate Status

### GREEN

Proceed. Log `[context: GREEN X%]` in scratchpad header.

### YELLOW

Log warning in DIGEST: `Context at X% — started task anyway, monitor closely`
Continue with the task but don't spawn sub-tasks or load large reference files.

### RED

Write to DIGEST:

```markdown
## Session Paused — Context Budget
Context reached X% at <timestamp>.
Completed this session: [list of task IDs]
Remaining unblocked tasks: [list from TaskList]
Resume: set CLAUDE_CODE_TASK_LIST_ID=<id> and re-run night shift
```

TaskUpdate any in_progress task back to `pending` with a note.
Exit cleanly.

## Configuring Thresholds

Override defaults in `NIGHT_SHIFT_MANIFEST.yaml`:

```yaml
compaction_threshold: 0.75   # RED threshold (default 75%)
warning_threshold: 0.60      # YELLOW threshold (default 60%)
```

## In-Context Check (no bash available)

If you can't run the shell script, estimate from conversation length:

- Short session (<10 tool calls): GREEN
- Medium session (10–30 tool calls with large outputs): YELLOW
- Long session (30+ tool calls, multiple file reads): assume RED, compact first
