---
description: Build a draw.io AWS architecture or CI/CD diagram from this repo's IaC
argument-hint: "[what to draw, e.g. architecture, cicd, network] [output path]"
---

Read `.archsmith.json` in the repo root. If `mode` is `agent`, hand this task to the archsmith agent with the request below and relay its short report. Otherwise (`skill` or no file) do it here by following the archsmith skill.

Task: build a new diagram. Request: $ARGUMENTS

Empty request: draw the overall architecture with an overview tab and layers.
