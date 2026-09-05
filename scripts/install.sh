#!/usr/bin/env bash
#
# install.sh — install pk-modeling-skills into an agent skills directory.
#
# Usage:
#   ./scripts/install.sh                       auto-detect target, copy (safe default)
#   ./scripts/install.sh --list                show detected candidate targets and exit
#   ./scripts/install.sh --target DIR [--link|--copy]
#   ./scripts/install.sh --skill NAME ...      install only selected skills
#
# Auto-detection order: ~/.claude/skills, ~/.codex/skills, ~/.agents/skills,
# ./.cursor/skills (only when inside a git repository).
#
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
SKILLS_SRC="$REPO/skills"

mode="copy"
target=""
list_only=false
selected=()

usage() { sed -n '2,12p' "$0" | sed 's/^# \{0,1\}//'; }

while [[ $# -gt 0 ]]; do
  case "$1" in
    --target) target="${2:?--target needs a directory}"; shift 2 ;;
    --link)   mode="link"; shift ;;
    --copy)   mode="copy"; shift ;;
    --list)   list_only=true; shift ;;
    --skill)  selected+=("${2:?--skill needs a name}"); shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "unknown option: $1" >&2; usage >&2; exit 2 ;;
  esac
done

[[ -d "$SKILLS_SRC" ]] || { echo "error: $SKILLS_SRC not found — run from a pk-modeling-skills clone" >&2; exit 1; }

# ---------------------------------------------------------------- candidates
candidates=()
for d in "$HOME/.claude/skills" "$HOME/.codex/skills" "$HOME/.agents/skills"; do
  candidates+=("$d")
done
if git -C "$PWD" rev-parse --show-toplevel >/dev/null 2>&1; then
  candidates+=("$PWD/.cursor/skills")
fi

if $list_only; then
  echo "Candidate agent skills directories (first existing wins for auto-install):"
  found_existing=false
  for d in "${candidates[@]}"; do
    if [[ -d "$d" ]]; then
      echo "  [exists]  $d"; found_existing=true
    else
      echo "  [absent]  $d (would be created)"
    fi
  done
  $found_existing || echo "  (none exist yet; default would be ${candidates[0]})"
  exit 0
fi

if [[ -z "$target" ]]; then
  target="${candidates[0]}"
  for d in "${candidates[@]}"; do
    if [[ -d "$d" ]]; then target="$d"; break; fi
  done
fi
mkdir -p "$target"
echo "target: $target (mode: $mode)"

# -------------------------------------------------------------------- skills
skills=("${selected[@]}")
if [[ ${#skills[@]} -eq 0 ]]; then
  for d in "$SKILLS_SRC"/*/; do skills+=("$(basename "$d")"); done
fi

for name in "${skills[@]}"; do
  src="$SKILLS_SRC/$name"
  dst="$target/$name"
  [[ -d "$src" ]] || { echo "error: skill '$name' not found in $SKILLS_SRC" >&2; exit 1; }
  [[ -f "$src/SKILL.md" ]] || { echo "error: $src has no SKILL.md" >&2; exit 1; }

  rm -rf "$dst"
  if [[ "$mode" == "link" ]]; then
    ln -s "$src" "$dst"
  else
    cp -R "$src" "$dst"
  fi
  echo "installed: $name -> $dst"
done

echo
echo "done. Each skill keeps its SKILL.md at <target>/<skill>/SKILL.md."
echo "Next: run ./scripts/doctor.sh to check the modeling toolchain."
