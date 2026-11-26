---
description: Choose how archsmith runs (inline skill or isolated agent) and where diagrams go
argument-hint: "[mode=skill|agent] [dir=diagram]"
---

Configure archsmith for this repo. Arguments: $ARGUMENTS

1. Parse `mode=` and `dir=` from the arguments. For anything missing, ask the user:
   - Mode: `skill` runs inside this chat (cheaper, you can steer it; best for small repos, refreshes and slides). `agent` runs in its own context (keeps this chat clean; best for large repos and full rebuilds). Recommend `skill`.
   - Output folder for diagrams. Default `diagram`.
2. Check the render tool: run `command -v drawio || ls /Applications/draw.io.app`. Report whether the draw.io CLI was found. It is optional. Without it archsmith still writes the file and gives a web preview link.
3. Write `.archsmith.json` in the repo root, for example `{"mode": "skill", "outputDir": "diagram"}`. If the file exists, show the current values and ask before changing it.
4. Print a short summary: the settings, and the three commands `/archsmith:diagram`, `/archsmith:refresh`, `/archsmith:slides`.

Do not run git commands.
