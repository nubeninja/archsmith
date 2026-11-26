---
description: Add presentation slide tabs (1920x1080, one topic per tab) to a draw.io diagram
argument-hint: "[path to .drawio file] [topics, e.g. network, security, cicd]"
---

Read `.archsmith.json` in the repo root. If `mode` is `agent`, hand this task to the archsmith agent with the request below and relay its short report. Otherwise (`skill` or no file) do it here by following the archsmith skill.

Task: add slide tabs (the skill's "Slides" task). Request: $ARGUMENTS

Default topics: traffic and failover, network, compute, security, CI/CD. No file given: use the existing .drawio file, or build the overview first.
