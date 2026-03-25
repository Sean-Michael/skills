#!/bin/bash
# check-context.sh
# Standalone context budget checker for Claude Code sessions.
# Reads the latest session JSONL transcript and reports GREEN/YELLOW/RED.
# 
# Usage: ./check-context.sh [threshold_pct]
#   threshold_pct: RED threshold as decimal, default 0.75

set -euo pipefail

THRESHOLD="${1:-0.75}"
WARNING_THRESHOLD="${2:-0.60}"
CONTEXT_WINDOW=200000

# Find the most recent project session
PROJECTS_DIR="$HOME/.claude/projects"

if [ ! -d "$PROJECTS_DIR" ]; then
  echo "GREEN (no .claude/projects directory found)"
  exit 0
fi

# Find the most recently modified JSONL file across all projects
SESSION_FILE=$(find "$PROJECTS_DIR" -name "*.jsonl" -newer /tmp 2>/dev/null | \
  xargs ls -t 2>/dev/null | head -1)

if [ -z "$SESSION_FILE" ]; then
  # Fallback: just find any JSONL
  SESSION_FILE=$(find "$PROJECTS_DIR" -name "*.jsonl" 2>/dev/null | \
    xargs ls -t 2>/dev/null | head -1)
fi

if [ -z "$SESSION_FILE" ]; then
  echo "GREEN (no session transcripts found)"
  exit 0
fi

# Extract usage from latest assistant turn with usage data
RESULT=$(python3 - "$SESSION_FILE" "$THRESHOLD" "$WARNING_THRESHOLD" "$CONTEXT_WINDOW" << 'EOF'
import sys, json

session_file = sys.argv[1]
red_threshold = float(sys.argv[2])
yellow_threshold = float(sys.argv[3])
context_window = int(sys.argv[4])

latest_usage = None

try:
    with open(session_file, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                if obj.get('type') == 'assistant' and 'usage' in obj:
                    latest_usage = obj['usage']
            except json.JSONDecodeError:
                continue
except Exception as e:
    print(f"GREEN (could not read transcript: {e})")
    sys.exit(0)

if not latest_usage:
    print("GREEN (no usage data in transcript)")
    sys.exit(0)

cache_read = latest_usage.get('cache_read', 0)
cache_create = latest_usage.get('cache_create', 0)
input_tokens = latest_usage.get('input', 0)
total = cache_read + cache_create + input_tokens
pct = total / context_window

if pct > red_threshold:
    print(f"RED ({pct:.1%} used, {total:,}/{context_window:,} tokens) — STOP: context budget exceeded")
    sys.exit(1)
elif pct > yellow_threshold:
    print(f"YELLOW ({pct:.1%} used, {total:,}/{context_window:,} tokens) — context filling, proceed with caution")
    sys.exit(0)
else:
    print(f"GREEN ({pct:.1%} used, {total:,}/{context_window:,} tokens)")
    sys.exit(0)
EOF
)

echo "$RESULT"

# Propagate exit code from python
exit $?
