#!/usr/bin/env bash
# PreToolUse hook for Edit|Write|NotebookEdit: deny any write outside the project folder.
# Symlinks are resolved first, so a link inside the project that points outside is denied too.
set -euo pipefail

input=$(cat)
project=$(realpath -m -- "${CLAUDE_PROJECT_DIR:?}")
target=$(jq -r '.tool_input.file_path // .tool_input.notebook_path // empty' <<<"$input")
[[ -z $target ]] && exit 0

if [[ $target != /* ]]; then
    cwd=$(jq -r '.cwd // empty' <<<"$input")
    target="${cwd:-$project}/$target"
fi
target=$(realpath -m -- "$target")

case $target in
    "$project" | "$project"/*) exit 0 ;;
esac

jq -n --arg p "$target" '{
  hookSpecificOutput: {
    hookEventName: "PreToolUse",
    permissionDecision: "deny",
    permissionDecisionReason: ("Edits outside the project folder are blocked: " + $p)
  }
}'
