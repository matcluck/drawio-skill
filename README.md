# drawio-skill

A Claude Code skill that generates draw.io diagrams from natural language. Guides you through requirements, generates valid draw.io XML, renders to PNG, then iteratively refines the diagram through 5 critique/improve cycles.

By [Matcluck](https://github.com/matcluck)

## How it works

1. **Preflight** — checks required tools are installed
2. **Requirements** — asks 5 questions to understand what you need
3. **Generate** — produces valid `.drawio` XML with proper styles and layout
4. **Render** — exports to PNG via the draw.io desktop CLI
5. **Refine** — 5 Ralph Loop iterations: critique the render, fix issues, re-render

## Setup

Install to your Claude Code skills directory:

```bash
git clone https://github.com/matcluck/drawio-skill ~/.claude/skills/drawio
```

### Requirements

| Tool | Linux | macOS | Windows |
|------|-------|-------|---------|
| drawio | `snap install drawio` | `brew install --cask drawio` | [Download](https://github.com/jgraph/drawio-desktop/releases) |
| xmllint | `sudo apt install libxml2-utils` | Pre-installed | `choco install libxml2` |
| imagemagick | `sudo apt install imagemagick` | `brew install imagemagick` | `choco install imagemagick` |
| xvfb | `sudo apt install xvfb` | Not needed | Not needed |
| python3 | Typically pre-installed | `brew install python3` | [python.org](https://python.org/downloads/) |

xvfb is only needed on headless Linux (no display server).

## Usage

```
/drawio
```

The skill will walk you through the rest.

## Custom icons

Drop PNG, WebP, or SVG files into `assets/icons/`. The skill discovers them at runtime and offers them during requirements gathering. Icons are embedded as base64 in the final `.drawio` file for portability.

## Structure

```
drawio-skill/
  SKILL.md                          # main skill definition
  assets/icons/                     # custom icons (gitignored, add your own)
  references/
    STYLE-REFERENCE.md              # element styles and colour palette
    STRUCTURAL-PATTERNS.md          # diagram layout patterns
    CRITIQUE-TEMPLATE.md            # refinement checklist
  scripts/
    render_drawio.py                # headless PNG renderer
    embed_icons.py                  # embeds file:/// icons as base64
```
