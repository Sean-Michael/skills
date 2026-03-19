#!/usr/bin/env bash
# install.sh — symlink personal skills into ~/.claude/skills/
set -euo pipefail

SKILLS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR="$HOME/.claude/skills"

mkdir -p "$TARGET_DIR"

for skill_dir in "$SKILLS_DIR"/*/; do
  skill_name="$(basename "$skill_dir")"
  target="$TARGET_DIR/$skill_name"

  # Skip non-skill directories (no SKILL.md present)
  [[ ! -f "$skill_dir/SKILL.md" ]] && continue

  if [[ -L "$target" ]]; then
    echo "  up to date  $skill_name"
  elif [[ -e "$target" ]]; then
    echo "  skipped     $skill_name (exists at $target, not a symlink — remove manually)"
  else
    ln -s "$skill_dir" "$target"
    echo "  linked      $skill_name"
  fi
done