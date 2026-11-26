#!/usr/bin/env bash
# Copy the archsmith skill into another AI coding tool's skills folder.
# Usage: ./install.sh <claude|codex|cursor|agents> [--project]
# It never overwrites: if the target exists it stops. Paths follow each tool's skills
# convention at the time of writing; check your tool's docs if it does not pick the skill up.
set -euo pipefail
tool="${1:?usage: install.sh <claude|codex|cursor|agents> [--project]}"
src="$(cd "$(dirname "$0")" && pwd)/skills/archsmith"
base="$HOME"; [ "${2:-}" = "--project" ] && base="$PWD"
case "$tool" in
  claude) dest="$base/.claude/skills/archsmith";;
  codex) dest="$base/.codex/skills/archsmith";;
  cursor) dest="$base/.cursor/skills/archsmith";;
  agents) dest="$base/.agents/skills/archsmith";;
  *) echo "unknown tool: $tool" >&2; exit 2;;
esac
if [ -e "$dest" ]; then echo "$dest already exists; remove it yourself to reinstall." >&2; exit 1; fi
mkdir -p "$(dirname "$dest")"
cp -R "$src" "$dest"
echo "installed to $dest"
