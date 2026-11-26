<p align="center">
  <img src="docs/images/hero.jpg" alt="archsmith: draw.io AWS architecture diagrams, built from your Terraform. A Claude Code plugin and portable skill." width="720">
</p>

<p align="center">
  <a href="https://github.com/nubeninja/archsmith/actions/workflows/ci.yml"><img src="https://github.com/nubeninja/archsmith/actions/workflows/ci.yml/badge.svg" alt="CI status"></a>
  <a href="https://github.com/nubeninja/archsmith/actions/workflows/security.yml"><img src="https://github.com/nubeninja/archsmith/actions/workflows/security.yml/badge.svg" alt="Security checks status"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-Apache--2.0-blue" alt="License: Apache-2.0"></a>
</p>

# archsmith

archsmith is a Claude Code plugin and a portable skill. It reads your repository's infrastructure code and builds draw.io diagrams of your AWS architecture and CI/CD pipelines, using the official AWS shapes.

It reads Terraform, CloudFormation, CDK, Helm values and workflow files, and it writes a `.drawio` file. Every label comes from your repository, not from a guess.

## What it makes

- **Overview tabs with layers:** network and services, EKS components, traffic flow, connectivity and security.
- **Slide tabs for presenting:** 1920x1080 pages with about 12 components each, large labels and one topic per tab.
- **Numbered badges and a legend** for diagrams with seven or more services.
- **Official shapes only** (`mxgraph.aws4.*`). No clip art and no image URLs.

## Quick start

Run these commands in Claude Code:

```
/plugin marketplace add nubeninja/archsmith
/plugin install archsmith@nubeninja
```

Then open the repository you want to draw and run:

```
/archsmith:setup
/archsmith:diagram
```

The setup asks two things: run as an inline **skill** or an isolated **agent**, and which folder gets the diagrams. Non-interactive form: `/archsmith:setup mode=skill dir=diagram slides=true`. It saves `.archsmith.json` in the repo root.

## How it works

<p align="center">
  <img src="docs/images/how-it-works.png" alt="Four steps: read your repo, build the diagram, check it, review it in draw.io. The output is one .drawio file in diagram/." width="720">
</p>

1. **Read your repo.** archsmith summarizes your Terraform first, so the model reads less, and then reads the files it needs.
2. **Build the diagram.** It generates overview tabs with layers and, by default, slide tabs.
3. **Check it.** A validator checks the XML, text size, label length, canvas size and likely overlaps.
4. **Review in draw.io.** Open the file, adjust it and share it.

## Run it as a skill or an agent

<p align="center">
  <img src="docs/images/skill-vs-agent.png" alt="Skill (default): runs inside your chat, cheaper per run, you can steer it, best for small repos, refreshes and slides. Agent: runs in its own context, keeps your chat clean, uses more tokens in total, best for large repos and full rebuilds." width="720">
</p>

`/archsmith:setup` asks which mode you want and where the diagrams should go. You can also pass the answers directly:

```
/archsmith:setup mode=skill dir=diagram slides=true
```

| Mode | Runs | Best for |
| --- | --- | --- |
| `skill` (default) | In your chat | Small repositories, refreshes and slides. It is cheaper, and you can steer it. |
| `agent` | In its own context | Large repositories and full rebuilds. It keeps your chat clean but uses more tokens in total. |

## Commands

| Command | What it does |
| --- | --- |
| `/archsmith:setup` | Choose skill or agent mode, the output folder, and whether to build slides |
| `/archsmith:diagram [what to draw]` | Build a new diagram from the repository's infrastructure code |
| `/archsmith:refresh [file.drawio]` | Update a diagram to match the code and keep the cells you added by hand |
| `/archsmith:slides [file.drawio] [topics]` | Add 1920x1080 slide tabs, one topic per tab |

You can also ask in plain words, for example: "Use archsmith to draw the architecture of this repository."

## Config file

`.archsmith.json` in the repo root. It is plain JSON and safe to commit if your team wants shared settings, or to ignore if not.

```json
{ "mode": "skill", "outputDir": "diagram", "slides": true }
```

| Key | Default | Meaning |
| --- | --- | --- |
| `mode` | `skill` | `skill` runs inline, `agent` runs in its own context (Claude Code commands only) |
| `outputDir` | `diagram` | Where new `.drawio` files go when you give no path |
| `slides` | `true` | Also build 1920x1080 slide tabs. `false` for overview only |

## Output

archsmith writes one `.drawio` file to `diagram/` (it creates the folder if needed) or to the path you give. It writes a PNG or JPEG only when you ask for one and give a size, for example "export a PNG that is 1600 px wide". Before it edits an existing file, it saves a backup named `<name>.drawio.bak`.

## Install with npm (Claude Code, Codex, Cursor, others)

The skill in `skills/archsmith/` is a plain `SKILL.md` with `scripts/` and `references/`, with no Claude-only settings. The npm package copies it into your tool's skills folder:

```
npx archsmith install              # Claude Code, into ~/.claude/skills (default)
npx archsmith install codex        # or: claude, cursor, agents
npx archsmith install cursor --project   # current repo instead of your home folder
```

It never overwrites an existing install unless you add `--force`. It has no dependencies and no install scripts. Slash commands and `/archsmith:setup` come with the Claude Code plugin only. Releases are published from GitHub Actions with npm provenance, so you can verify the build with `npm audit signatures`.

The installer never overwrites an existing install unless you add `--force`. It has no dependencies and no install scripts. Releases are published from GitHub Actions with npm provenance, so you can verify a build with `npm audit signatures`.

- `drawio_lib.py`: builds pages, layers, groups, icons, edges, badges and a legend, and refuses duplicate ids.
- `validate.py`: checks the file (details below).
- `tf_summary.py`: summarizes Terraform (or `terraform show -json` output) so the model reads less.
- `preview_url.py`: prints a draw.io web link, so you can open the result with no desktop app.
- `render.sh`: exports PNG, JPEG, SVG or PDF with the draw.io desktop CLI.

## Checking a diagram yourself

archsmith runs the validator for you after every build. You can also run it on any `.drawio` file. It needs only Python 3.8 or newer and installs nothing:

```
python3 skills/archsmith/scripts/validate.py diagram/architecture.drawio
```

On Windows use `python` or `py`. If the plugin is installed through Claude Code, the script sits inside the plugin folder; ask archsmith to "validate this diagram" and it runs it for you.

- **Errors** (exit code 1): invalid XML, compressed pages, duplicate ids, edges that point at nothing, image URLs.
- **Warnings** (exit code 0): text under 20 px on slide pages or under 14 px on overview pages, labels longer than about 9 words, an overview canvas over 3000 px, likely overlapping icons or labels, shape libraries other than AWS and GitHub, a hardcoded background.
- `--strict` turns warnings into a failing exit code, so you can use it in CI. `--min-font-slide N` and `--min-font-overview N` change the text floors.

Limits: the overlap check estimates label sizes from text length, and it does not check whether an arrow crosses a label. Open the file in draw.io before you share it.

## Requirements

- Python 3.8 or newer for the scripts (standard library only). `render.sh` needs bash: on Windows use Git Bash or WSL, or call the draw.io CLI directly.
- Optional: the draw.io desktop CLI for rendering and export. macOS: install draw.io desktop. Linux or Windows: install from https://github.com/jgraph/drawio-desktop/releases and put `drawio` on PATH; headless Linux needs `xvfb-run`. Without it, archsmith still writes the file, checks the XML, and gives a web preview link.
- Optional: a draw.io MCP server, so the agent can look up shape names.

## Limits

- archsmith never deletes files without asking, and it never runs `git add`, `git commit` or `git push`.
- It draws what the repository defines. It does not read live AWS accounts.
- A model generates the layout. Open the file in draw.io and review it before you share it.

## Security and releases

See [SECURITY.md](SECURITY.md) to report a vulnerability and [docs/RELEASING.md](docs/RELEASING.md) for how releases are built and published.

## Credits

The idea of the codebase-analysis and brainstorm modes, validation, numbered badges with a legend, and a no-install preview link comes from the AWS Labs [aws-architecture-diagram](https://github.com/awslabs/agent-plugins/tree/main/plugins/deploy-on-aws/skills/aws-architecture-diagram) skill (Apache-2.0). archsmith's code and text are written separately and copy none of it.

## License

Apache-2.0. See [LICENSE](LICENSE).
