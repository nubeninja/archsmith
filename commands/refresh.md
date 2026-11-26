---
description: Update an existing draw.io diagram to match the current IaC, keeping hand-made cells
argument-hint: "[path to .drawio file]"
---

Read `.archsmith.json` in the repo root. If `mode` is `agent`, hand this task to the archsmith agent with the request below and relay its short report. Otherwise (`skill` or no file) do it here by following the archsmith skill.

Task: refresh an existing diagram (the skill's "Refresh" task). Target: $ARGUMENTS

No path given: look in the output folder, then the repo, and use the only .drawio file, or ask which one.
