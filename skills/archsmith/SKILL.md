---
name: archsmith
description: Builds and refreshes draw.io (.drawio) AWS architecture and CI/CD diagrams in the official AWS shape style from Terraform, CloudFormation, CDK, Helm values and workflow files. Use for an architecture, network, EKS, security or CI/CD diagram, a draw.io file, slide tabs for presenting, or to update an existing draw.io diagram.
---

# archsmith

Build draw.io diagrams that look like AWS reference architectures, stay readable on a projector, and match the repo. Facts come from the repo, never from guesses.

Paths below are relative to this skill's folder. Run scripts with `python3` (`python` or `py` on Windows). They use only the Python standard library, so nothing needs installing.

## 1. Config (optional)
If `.archsmith.json` exists in the repo root, read it. Keys: `outputDir` (default `diagram`), `slides` (default `true`: also build slide tabs), `mode` (`skill` or `agent`, used by the Claude Code commands only). Missing file means defaults.

## 2. Pick the task
- **Analyze (default when IaC exists):** draw from the repo. Build the overview tabs and, unless `slides` is `false` or the user says "overview only", the slide tabs too.
- **Brainstorm:** no IaC, or the user says "design" or "from scratch". Ask 3 to 5 short questions (purpose, services, scale, security, traffic), propose the services and flow, then draw.
- **Refresh:** a `.drawio` file already exists and the user wants it updated. Back it up as `<name>.drawio.bak`, list what is in the code but not in the diagram and the reverse, apply the changes, keep cells the user added or moved by hand.
- **Slides:** add 1920x1080 slide tabs, one topic per tab. Do not change the overview tabs.

## 3. Gather facts (read little)
- Terraform: run `scripts/tf_summary.py <dir>` first (or `--plan plan.json` for `terraform show -json` output). It lists resources, CIDRs and modules. Then read only the files you need for CIDRs, AZ count, instance types, node group sizes, NAT per AZ or shared, instance counts.
- Also read workflow files, Helm values, CloudFormation and CDK when present.
- Ask only what you cannot find: audience (screen, projector, print), which tabs, test, prod or both.
- Every label must match the repo. Show only what the code builds. Draw prod-only or unbuilt parts faded (`opacity=35`) and label them "(prod)" or "(optional)".
- In skill mode, list the services you found in a few lines and continue unless the user objects. In agent mode, do not stop to ask: state your assumptions in the report.

## 4. Build
Load references only now, and only what the task needs:
- `references/shapes.md` always.
- `references/style-guide.md` and `references/layout.md` always.
- `references/tabs-and-slides.md` for tab structure and slide tabs.

Write a short generator script in a temp folder (not in the project) that imports `scripts/drawio_lib.py`: it builds pages, layers, groups, icons, edges, numbered badges and a legend, and refuses duplicate ids. Rebuild from the script after fixes.
Text size floors: 22 px on slide pages, 14 px on overview pages. Icon labels at most 2 short lines. Keep an overview canvas under 3000 px on each side; split into more tabs instead of growing the canvas. Slide pages are 1920x1080, built with `d.slide(...)`.
Use numbered badges (40 px circles) with a short explanation list, and a legend, when a diagram has 7 or more services. Put only CloudWatch, CloudTrail, X-Ray and IAM in an "auxiliary" group when the user asks for them; otherwise leave cross-cutting services out. A non-AWS service without an official icon is a grey rounded box with a clear label. GitHub uses `mxgraph.weblogos.github`.

## 5. Check
1. `python3 scripts/validate.py <file.drawio>`. Fix every ERROR. Fix WARNINGS about small text, long labels, big canvas and overlaps by changing the layout, then rerun. Say in the report which warnings remain and why.
2. If the draw.io CLI exists, render each page to a temp folder with `scripts/render.sh <file> <tmp/out.png> <page> 0.5`, look at the images, fix overlaps, clipped labels, missing borders and empty AZs, then render again. Previews are checks only and are not delivered.
3. No CLI: say the render was not checked and give the web link from `python3 scripts/preview_url.py <file>`. The diagram is in the URL fragment; the link works in any browser.

## 6. Output
- Deliver the `.drawio` file only. Location: the path the user gave, else `<outputDir>/` (default `diagram/`, created if missing), named in kebab-case such as `diagram/architecture.drawio`. Never write output to a temp or scratch location.
- PNG, JPEG, SVG or PDF only when asked. If a raster format is asked without a size, ask for the size. Export with `scripts/render.sh <file> <out.ext> <page|all> <1200px|scale>`; put it next to the `.drawio` file.
- Back up an existing file before editing: `<name>.drawio.bak`.

## 7. Never
- Never delete a file without asking. Name the file.
- Never run git add, commit or push.
- Never use image URLs, clip art or. Official shapes only; never invent a shape name.

## 8. Report
List the tabs and layers, what changed, and what was not checked (for example "not opened in the draw.io app"). Name faded or simplified parts and why. Give the full path of the `.drawio` file and the backup, the validation result, the web preview link when no CLI was available, and a one-line alt text under 100 characters. Offer PNG or JPEG export and ask for the size; do not export unasked.
