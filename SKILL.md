---
name: drawio
description: Use when the user wants to create a draw.io diagram. Guides requirements gathering, generates valid draw.io XML, renders to PNG, then runs 3 Ralph Loop critique/refine cycles (override with --max-iterations N). Works for any diagram type.
compatibility: Requires drawio desktop, python3, xmllint, xvfb, and imagemagick (convert).
metadata:
  author: Matcluck
  version: "1.0"
---

# Draw.io Diagram Builder

You are building a draw.io diagram. Follow these phases exactly.

## Preflight

Before starting, verify all required tools are available:
```bash
command -v drawio && echo "drawio: OK" || echo "drawio: MISSING"
command -v xmllint && echo "xmllint: OK" || echo "xmllint: MISSING"
command -v convert && echo "imagemagick: OK" || echo "imagemagick: MISSING"
python3 -c "print('python3: OK')" 2>/dev/null || echo "python3: MISSING"
# xvfb is only needed on headless Linux (no display server)
if [ -z "$DISPLAY" ] && [ -z "$WAYLAND_DISPLAY" ]; then
  command -v xvfb-run && echo "xvfb: OK" || echo "xvfb: MISSING (needed — no display server detected)"
else
  echo "xvfb: not needed (display server detected)"
fi
```

If any tools are missing, tell the user which ones need installing and stop. Do not attempt to install them yourself.

| Tool | Linux | macOS | Windows |
|------|-------|-------|---------|
| drawio | `snap install drawio` | `brew install --cask drawio` | [Download installer](https://github.com/jgraph/drawio-desktop/releases) |
| xmllint | `sudo apt install libxml2-utils` | Pre-installed | `choco install libxml2` |
| imagemagick | `sudo apt install imagemagick` | `brew install imagemagick` | `choco install imagemagick` |
| xvfb | `sudo apt install xvfb` | Not needed | Not needed |
| python3 | Typically pre-installed | `brew install python3` | [python.org](https://www.python.org/downloads/) |

xvfb is only required on headless Linux systems (no X11 or Wayland display). Skip if a display server is available.

Do not proceed to Phase 1 until all required tools are confirmed available.

---

<HARD-GATE>
Do NOT generate any XML until Phase 1 (requirements gathering) is complete and you
have confirmed the diagram scope with the user.
</HARD-GATE>

---

## Phase 1 — Requirements Gathering

If the user provided a detailed description with their `/drawio` command (e.g. `/drawio build me a system architecture with X, Y, Z connected like this...`), **skip the questions below**. Extract the answers from their description, check for icons, then go straight to the confirmation summary.

Otherwise, ask these questions **one at a time**. Wait for the answer before asking the next.

1. **Diagram type** — What kind of diagram is this? (system architecture, workflow/flowchart, org chart, network topology, ER/data model, other?)
2. **Components** — What are the main entities, services, or steps? List them.
3. **Relationships** — How do they connect? (sequential flow, parallel branches, data dependencies, hierarchy?)
4. **Detail level** — Brief overview or detailed (with commands, descriptions, tool references)?
5. **Special requirements** — Specific colour scheme (light mode, dark mode)?

After question 5 (or after extracting from a batch description), check if custom icons are available:
```bash
ls ~/.claude/skills/drawio/assets/icons/ 2>/dev/null | grep -v README.md
```
If icons are found, ask as a separate question: *"I found these custom icons available: [list filenames]. Would you like to use any of them in the diagram?"* If no icons are found, skip this question.

After all answers, summarise your understanding and ask: *"Does this capture what you want? Any additions or changes?"* Do not proceed until confirmed.

### Icons

Icons are stored in `assets/icons/` (relative to this skill's directory).

After the user selects icons, Read only the selected icon files to see what they look like (for positioning and style decisions). **Do NOT Read icons the user didn't select** — only interact with unselected icons via bash commands (ls, find).

For each selected icon, check its size, resize if needed, and resolve the path — all in a **single** bash command:
```bash
ICON_DIR="$(readlink -f ~/.claude/skills/drawio/assets/icons)"
for f in "icon1.png" "icon2.webp"; do
  filepath="$ICON_DIR/$f"
  size=$(stat -c%s "$filepath" 2>/dev/null || echo 0)
  if [[ "$size" -gt 131072 ]] && [[ "$f" != *.svg ]]; then
    convert "$filepath" -resize 512x512\> "$filepath"
    echo "Resized: $f"
  fi
  echo "file:///$filepath"
done
```
Replace `"icon1.png" "icon2.webp"` with the actual filenames the user selected. Do NOT scan all icons — only process selected ones.
**Icon node style template:**
```
style="shape=image;verticalLabelPosition=bottom;labelBackgroundColor=<bg-color>;html=1;verticalAlign=top;aspect=fixed;imageAspect=1;image=file:///<resolved-icon-dir>/<filename>;"
```
- `html=1` — required for HTML label content to render (without it, tags appear as literal text)
- `imageAspect=1` — preserves icon aspect ratio (0 stretches the image)
- `labelBackgroundColor` — must match the **actual visual background at that position** (page bg for top-level nodes; group fill for nodes inside a coloured group). See STYLE-REFERENCE.md for colour rules.
- **Dark icon visibility**: before using an icon on a dark background, check if the icon design is dark-coloured (e.g., Github.svg has a black logo). Look for a light-coloured variant in `assets/icons/` (e.g., `github-white-icon.webp`).

---

## Phase 2 — Generate the Diagram

### How it works
You describe the diagram as **JSON** (nodes, edges, labels, types). The `generate_drawio.py` script handles all coordinate math, spacing, and style application from `config.json`. **Do NOT write raw XML yourself** — let the script do it.

### Filename
Name the file `<topic-slug>.drawio` (e.g., `ci-pipeline.drawio`, `network-architecture.drawio`).

### Step 0: Review design principles

Before writing any JSON, read [references/DESIGN-PRINCIPLES.md](references/DESIGN-PRINCIPLES.md) to inform aesthetic decisions — color semantics, edge routing, whitespace, labeling standards, and the diagram review checklist.

### Step 1: Choose a layout

| Layout | Use for | How it arranges nodes |
|--------|---------|----------------------|
| `linear` | Flowcharts, pipelines, sequential processes | Vertical stack, centred |
| `horizontal` | Timelines, left-to-right pipelines | Single row, left to right |
| `branching` | Decision trees, parallel workflows, fan-out/fan-in | BFS levels, siblings side by side |
| `hierarchical` | Org charts, taxonomies, tree structures | Same as branching (tree-aware) |
| `grid` | Dashboards, card layouts, inventories | Rows and columns (set `grid_columns`) |
| `swimlane` | BPMN, cross-team processes | Horizontal lanes (set `lanes` array, nodes need `lane` field) |

See [references/STRUCTURAL-PATTERNS.md](references/STRUCTURAL-PATTERNS.md) for visual examples of each layout.

### Step 2: Write the JSON

Create a JSON object with the diagram structure. Write it to `<topic-slug>.json` using the Write tool.

**Node types** (each gets automatic styling from config.json):
| Type | Visual | Use for |
|------|--------|---------|
| `start` | Dark slate ellipse | Entry points |
| `end` | Dark slate ellipse | Exit points |
| `process` | Rounded box | General steps (variants below) |
| `decision` | Yellow diamond | Branch/decision points |
| `note` | Yellow sticky | Annotations |
| `success` | Green box | Success/output states |
| `dark_panel` | Dark box, light text | Terminal/code blocks |
| `data_store` | DFD data store | Databases, storage |
| `cylinder` | 3D cylinder | Databases (alt visual) |
| `cloud` | Cloud shape | External services, cloud infra |
| `actor` | Person shape | Users, roles |
| `icon` | Custom image | Requires `icon` field with `file:///` path |

**Process variants** (`variant` field on `process` nodes):
| Variant | Colour | Semantic use |
|---------|--------|-------------|
| `primary` | Blue | Default, main flow |
| `secondary` | Green | Supporting steps |
| `accent` | Purple | Highlighted steps |
| `warning` | Orange | Caution, external deps |
| `danger` | Red | Errors, critical paths |
| `neutral` | Grey | Background, optional |

**Edge options:**
- `style`: `"solid"` (default), `"curved"`, `"dashed"`, `"dotted"`, `"bidirectional"`
- `color`: `"green"`, `"orange"`, `"blue"`, `"red"`, `"purple"`, `"grey"` (optional)
- `label`: edge label text (optional)

**Groups** (optional): wrap related nodes in a shaded background box with a label.

**Swimlane-specific fields:**
- `lanes`: array of `{"id": "...", "label": "...", "color": "#hex"}` objects
- Each node needs a `lane` field matching a lane `id`

**Theme** (optional):
- `"theme": "light"` (default) or `"theme": "dark"` — dark mode uses a `#0F172A` background with adjusted fills, strokes, and text colours from the `dark` section of config.json. Set this when the user requests dark mode.

**Title and subtitle** (optional):
- `title`: Main heading (24px bold, centred)
- `subtitle`: Secondary text below title (13px muted, centred)

**Example JSON (linear):**
```json
{
  "title": "CI Pipeline",
  "subtitle": "Automated build and deploy workflow",
  "layout": "linear",
  "nodes": [
    {"id": "n1", "label": "Push Code", "type": "start"},
    {"id": "n2", "label": "Run Tests", "type": "process", "detail": "pytest + coverage"},
    {"id": "n3", "label": "Build Image", "type": "process", "variant": "secondary"},
    {"id": "n4", "label": "Deploy", "type": "success"},
    {"id": "n5", "label": "Done", "type": "end"}
  ],
  "edges": [
    {"from": "n1", "to": "n2"},
    {"from": "n2", "to": "n3"},
    {"from": "n3", "to": "n4"},
    {"from": "n4", "to": "n5"}
  ]
}
```

### Step 3: Generate the .drawio file

```bash
python3 ~/.claude/skills/drawio/scripts/generate_drawio.py <topic-slug>.json --output <topic-slug>.drawio
xmllint --noout <topic-slug>.drawio && echo "Valid XML" || echo "XML ERROR"
```

The script computes all coordinates, applies styles from `config.json`, and outputs valid `.drawio` XML. If `xmllint` fails, check the JSON for issues and regenerate.

### Styles and layout config

All styles, dimensions, colours, and spacing live in [scripts/config.json](scripts/config.json). To change the look of generated diagrams, edit config.json — do NOT hardcode styles in the JSON input or in raw XML.

### When to edit raw XML directly

Only edit the `.drawio` XML directly during **Ralph Loop refinement iterations** (Phase 4). For the initial generation, always use the JSON → script approach. When editing XML during refinement, read [scripts/config.json](scripts/config.json) for existing styles — it is the source of truth for defined styles. For attributes or shapes not covered by config.json, read [references/DRAWIO-STYLE-GUIDE.md](references/DRAWIO-STYLE-GUIDE.md).

---

## Phase 3 — Render to PNG

**Always edit `<filename>.drawio`** (the working copy with `file:///` icon URIs). Before each render, embed icons into a temporary copy so drawio can resolve them.

### Render command (with icons)
```bash
python3 ~/.claude/skills/drawio/scripts/embed_icons.py <filename>.drawio --output <filename>.render.drawio && python3 ~/.claude/skills/drawio/scripts/render_drawio.py <filename>.render.drawio --output <filename>.png && rm -f <filename>.render.drawio
```

### Render command (no icons)
```bash
python3 ~/.claude/skills/drawio/scripts/render_drawio.py <filename>.drawio
```

### Render quality
The renderer defaults to `--scale 2` (2× resolution) and `--border 20` for crisp output with padding. Override if needed:
```bash
python3 ~/.claude/skills/drawio/scripts/render_drawio.py <filename>.drawio --scale 3 --border 40
```

### Render timing
Renders take 10–20s (Electron cold-start). The critique depends on the rendered PNG, so you must wait for the render to complete before critiquing. Do **not** try to parallelise rendering — each iteration's XML depends on the previous critique.

**Never edit the `.render.drawio` file** — always edit the original.

**If rendering fails:** Deliver the `.drawio` XML file to the user and inform them:
> "Rendering failed. The `.drawio` file is ready — open it at [app.diagrams.net](https://app.diagrams.net) or in the draw.io desktop app."
Then skip Phase 4 and stop.

After successful render, read the output PNG as a screenshot using the Read tool.
Briefly describe what you see in the rendered diagram before entering Phase 4.

---

## Phase 4 — Ralph Loop: Refinement Iterations

Default: **3 iterations**. The user can override by passing `--max-iterations N` with their `/drawio` command (e.g. `/drawio ... --max-iterations 5`). If not specified, use 3.

Invoke the ralph-loop skill to begin iterative refinement.

**REQUIRED:** Use the `ralph-loop:ralph-loop` skill now with arguments. Pass the diagram filename as the prompt and set `--max-iterations` to the chosen count:
```
Skill: ralph-loop:ralph-loop
Args: Refine <filename>.drawio diagram --max-iterations <N>
```

For each iteration, follow this structure:

### Iteration Critique

Read [references/CRITIQUE-TEMPLATE.md](references/CRITIQUE-TEMPLATE.md) and critique the current PNG against each category (layout, connections, style, content).

### After Critique
List the specific changes you will make, then:
1. Edit the `.drawio` file (the working copy with `file:///` paths) to implement all improvements
2. Validate: `xmllint --noout <filename>.drawio`
   - If validation fails: revert the edit (restore the previous valid XML), make a more targeted fix, and re-validate before proceeding. Do not render broken XML.
3. Re-render using the embed-then-render pattern from Phase 3
4. Read the new PNG as a screenshot
5. State: *"Iteration N/<max> complete. Changes made: [summary]"*

### After All Iterations
Cancel the Ralph Loop using `ralph-loop:cancel-ralph`.

### Final Adjustments

Ask the user: *"Would you like any final adjustments before I package the diagram? (e.g., colours, layout tweaks, missing labels, icon changes)"*

If the user requests changes, make them, re-validate, and re-render. Repeat until the user confirms they're happy.

### Package Final Deliverable

Once the user is satisfied, embed icons into the final `.drawio` so it's portable:
```bash
python3 ~/.claude/skills/drawio/scripts/embed_icons.py <filename>.drawio
xmllint --noout <filename>.drawio && echo "Valid XML" || echo "XML ERROR"
```
This creates a `.drawio.bak` backup (the working copy with `file:///` paths) and embeds base64 icons in place. If no icons were used, skip the embed step.

Present the final output:
```
Diagram complete.

Files:
  <filename>.drawio       — draw.io source file (icons embedded, portable)
  <filename>.drawio.bak   — working copy with file:/// paths (if icons were used)
  <filename>.png          — rendered PNG

Open <filename>.drawio in draw.io (app.diagrams.net) to view and edit interactively.
```
