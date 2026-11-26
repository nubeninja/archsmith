#!/usr/bin/env bash
# Export a .drawio file with the draw.io desktop CLI.
# Usage: render.sh file.drawio out.(png|jpg|svg|pdf) [page] [width_px|scale]
#   page:  1-based page number, or "all" (all pages, PDF only). Default 1.
#   size:  "1200px" sets the width in pixels; a plain number such as 2 sets the scale. Default scale 1.
set -euo pipefail
src="${1:?file.drawio}"; out="${2:?output file}"; page="${3:-1}"; size="${4:-1}"
fmt="${out##*.}"; [ "$fmt" = "jpeg" ] && fmt=jpg

if command -v drawio >/dev/null 2>&1; then CLI=(drawio)
elif [ -x /Applications/draw.io.app/Contents/MacOS/draw.io ]; then CLI=(/Applications/draw.io.app/Contents/MacOS/draw.io)
else echo "draw.io CLI not found. Install draw.io desktop (https://github.com/jgraph/drawio-desktop/releases) or put 'drawio' on PATH." >&2; exit 3; fi
if [ "$(uname -s)" = "Linux" ] && [ -z "${DISPLAY:-}" ] && command -v xvfb-run >/dev/null 2>&1; then
  CLI=(xvfb-run -a "${CLI[@]}" --no-sandbox)
fi

args=(-x -f "$fmt" --crop -o "$out")
case "$size" in *px) args+=(--width "${size%px}");; *) args+=(-s "$size");; esac
if [ "$page" = "all" ]; then args+=(--all-pages); else args+=(-p "$page"); fi
"${CLI[@]}" "${args[@]}" "$src"
echo "wrote $out"
