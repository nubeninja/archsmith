# Tab structure

- Overview tabs: the full picture (architecture, CI/CD) with layers: 1 Network and
  services, 2 EKS components, 3 Traffic flow, 4 Connectivity, 5 Security. Cells in a
  layer use the layer cell as parent and absolute coordinates.
- Slide tabs for presenting at 1:1: page 1920x1080, at most about 12 components, icon
  labels 22 px or more, titles 28 to 36 px. One topic per tab: traffic and failover,
  network (one region, 3 AZs), EKS components, security, CI/CD application,
  CI/CD infrastructure.
- Every cell id is unique within its page, layer ids included (a clash breaks export).

## Readability floors (validate.py warns below these)
- Slide pages (1920x1080): text 22 px or more, titles 28 to 36 px, icons 64 px or more.
- Overview pages: text 14 px or more, canvas at most 3000 px per side. Split into more tabs instead of growing the canvas.
- Icon labels: at most 2 short lines (about 9 words). Put longer explanations in a separate numbered list.
- Slides are part of the default output. Skip them only when `.archsmith.json` has `"slides": false` or the user asks for overview only.
