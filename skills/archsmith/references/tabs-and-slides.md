# Tab structure

- Overview tabs: the full picture (architecture, CI/CD) with layers: 1 Network and
  services, 2 EKS components, 3 Traffic flow, 4 Connectivity, 5 Security. Cells in a
  layer use the layer cell as parent and absolute coordinates.
- Slide tabs for presenting at 1:1: page 1920x1080, at most about 12 components, icon
  labels 22 px or more, titles 28 to 36 px. One topic per tab: traffic and failover,
  network (one region, 3 AZs), EKS components, security, CI/CD application,
  CI/CD infrastructure.
- Every cell id is unique within its page, layer ids included (a clash breaks export).
