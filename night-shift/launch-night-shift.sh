#!/bin/bash
# launch-night-shift.sh
# Cron-friendly launcher for autonomous night shift RUN phase.
# Usage: ./launch-night-shift.sh [/path/to/repo]
#
# Can be scheduled with cron:
#   0 7 * * 1-5 /path/to/launch-night-shift.sh /path/to/repo >> /tmp/night-shift.log 2>&1

set -euo pipefail

REPO_PATH="${1:-$(pwd)}"
cd "$REPO_PATH"

MANIFEST="NIGHT_SHIFT_MANIFEST.yaml"

# ── Preflight ─────────────────────────────────────────────────────────────────

if [ ! -f "$MANIFEST" ]; then
  echo "ERROR: $MANIFEST not found in $REPO_PATH"
  echo "Run PLAN mode first: claude 'Morning shift planning: ...'"
  exit 1
fi

# Extract task list ID from manifest
TASK_LIST_ID=$(grep 'task_list_id:' "$MANIFEST" | awk '{print $2}' | tr -d '"')

if [ -z "$TASK_LIST_ID" ]; then
  echo "ERROR: task_list_id not found in $MANIFEST"
  exit 1
fi

# ── Context check before starting ─────────────────────────────────────────────

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$SCRIPT_DIR/check-context.sh" ]; then
  CONTEXT_STATUS=$("$SCRIPT_DIR/check-context.sh" 2>/dev/null || echo "GREEN (check failed)")
  echo "[$(date -Iseconds)] Context status: $CONTEXT_STATUS"
  
  if echo "$CONTEXT_STATUS" | grep -q "^RED"; then
    echo "ERROR: Context already at budget before starting. Run /compact first."
    exit 1
  fi
fi

# ── Launch ────────────────────────────────────────────────────────────────────

echo "[$(date -Iseconds)] Starting night shift for task list: $TASK_LIST_ID"
echo "[$(date -Iseconds)] Repo: $REPO_PATH"

export CLAUDE_CODE_TASK_LIST_ID="$TASK_LIST_ID"

# Optional: risk unlock from environment
RISK_UNLOCK="${NIGHT_SHIFT_UNLOCK_RISKY:-false}"
echo "[$(date -Iseconds)] Risk unlock: $RISK_UNLOCK"

SYSTEM_PROMPT="You are running an autonomous night shift.

1. Read NIGHT_SHIFT_MANIFEST.yaml for configuration
2. Read the autonomous-night-shift skill for the full execution protocol
3. Execute RUN mode: work through all unblocked safe tasks
4. Write per-task scratchpads and update NIGHT_SHIFT_DIGEST.md
5. Respect compaction gates — stop cleanly if context > threshold
6. Risk unlock is: $RISK_UNLOCK (risky tasks: $([ "$RISK_UNLOCK" = "true" ] && echo 'ALLOWED' || echo 'BLOCKED'))

Do not ask for confirmation. Do not wait for human input. 
Write TASK_COMPLETE or TASK_BLOCKED in each scratchpad.
When done or context budget exceeded, write final DIGEST entry and exit."

claude --headless --system-prompt "$SYSTEM_PROMPT" \
  "Run the autonomous night shift for task list $TASK_LIST_ID" 2>&1

echo "[$(date -Iseconds)] Morning shift session ended"

# ── Post-run summary ──────────────────────────────────────────────────────────

DIGEST_PATH=$(grep 'digest_path:' "$MANIFEST" | awk '{print $2}' | tr -d '"')
if [ -f "$DIGEST_PATH" ]; then
  echo ""
  echo "=== DIGEST SUMMARY ==="
  head -30 "$DIGEST_PATH"
  echo "=== END DIGEST (see $DIGEST_PATH for full report) ==="
fi
