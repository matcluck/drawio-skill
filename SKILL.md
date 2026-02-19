---
name: drawio
description: Use when the user wants to create a draw.io diagram. Guides requirements gathering, generates valid draw.io XML, renders to PNG, then runs Ralph Loop refinement (min 3 iterations: 1 JSON regeneration + at least 2 XML polish passes). Override iteration count with --max-iterations N. Works for any diagram type.
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
# ralph-loop skill (required for Phase 4 refinement iterations)
# Confirm it's registered by checking the available skills list in the system prompt.
# If ralph-loop:ralph-loop does not appear in the skill list, stop and tell the user to install it.
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

### Reference diagram (optional)

If the user's command includes a path to an existing `.drawio` or `.xml` file as a reference (e.g. `/drawio ... use this as reference: path/to/diagram.drawio`), analyse it before proceeding:

1. **Read the file** with the Read tool.
2. **Extract patterns** — summarise what you observe:
   - Layout direction (vertical, horizontal, branching)
   - Node types and shapes used
   - Colour scheme (light/dark, dominant palette colours)
   - Grouping or swimlane patterns
   - Edge styles (solid, dashed, curved, coloured)
   - Typography and label conventions (detail text, icons)
3. **Briefly tell the user** what you extracted: *"From your reference diagram I can see: [summary]. I'll match this style."*
4. Carry these observations forward into Phase 2 — match the reference's layout choice, colour variant, edge style, grouping approach, and general aesthetic when writing the JSON. You do NOT need to replicate it exactly; use it as a style guide.

If no reference diagram is mentioned, skip this section entirely.

---

### Gathering requirements

If the user provided a detailed description with their `/drawio` command (e.g. `/drawio build me a system architecture with X, Y, Z connected like this...`), **skip the questions below**. Extract the answers from their description, check for icons, then go straight to the confirmation summary.

Otherwise, ask these questions **one at a time**. Wait for the answer before asking the next.

1. **Diagram type** — What kind of diagram is this? (system architecture, workflow/flowchart, org chart, network topology, ER/data model, other?)
2. **Components** — What are the main entities, services, or steps? List them.
3. **Relationships** — How do they connect? (sequential flow, parallel branches, data dependencies, hierarchy?)
4. **Detail level** — Brief overview or detailed (with commands, descriptions, tool references)?
5. **Special requirements** — Specific colour scheme (light mode, dark mode)?
6. **Display format** — How should the diagram fit on screen? Wide/landscape (nodes side-by-side, good for monitors), Tall/portrait (steps stacked top-to-bottom), or should I choose based on the content?

After question 6 (or after extracting from a batch description), check if the user already indicated they don't want icons (e.g. "no icons", "without icons", "no custom icons"). If they did, **skip the icon check entirely**. Otherwise, check if custom icons are available:
```bash
ls ~/.claude/skills/drawio/assets/icons/ 2>/dev/null | grep -v README.md
```
If icons are found, ask as a separate question: *"I found these custom icons available: [list filenames]. Would you like to use any of them in the diagram?"* If no icons are found, skip this question.

After all answers, summarise your understanding and ask: *"Does this capture what you want? Any additions or changes?"* Do not proceed until confirmed.

---

## Phase 2 — Layout Preview

Before generating any JSON, sketch **2–3 candidate layouts** in ASCII using the actual node names from Phase 1. Present them side by side with the layout name so the user can pick the one that matches their mental model.

**Rules:**
- Abbreviate long node names to ≤10 characters
- Use `┌─┐`/`└─┘` for boxes, `───▶` for directed edges, `▼` for vertical flow, `│` for vertical connections
- Label each option: **Option A — `layout_name`**
- After the sketches, ask: *"Which layout looks closest to what you want? (A/B/C or describe something different)"*
- Do not proceed to Phase 2 until the user picks a layout

**Common patterns to offer (use the ones that fit the diagram's structure):**

*Sequential pipeline (straight through):*
```
[ Start ] ──▶ [ Step 1 ] ──▶ [ Step 2 ] ──▶ [ End ]
```
→ Use `linear` (tall) or `horizontal` (wide)

*Horizontal pipeline with a stacked middle step:*
```
[ A ] ──▶ [ B ] ──▶ ┌[ C1 ]┐  ──▶ [ D ] ──▶ [ E ]
                      │[ C2 ]│
                      └[ C3 ]┘
```
→ Use `pipeline` with the middle step as an array in the `pipeline` key

*Fan-out / fan-in:*
```
         ┌──▶ [ B1 ] ──┐
[ A ] ───┼──▶ [ B2 ] ──┼──▶ [ C ]
         └──▶ [ B3 ] ──┘
```
→ Use `branching` or `hierarchical`

*Grid of parallel items:*
```
[ A1 ] [ A2 ] [ A3 ]
[ B1 ] [ B2 ] [ B3 ]
```
→ Use `grid` or `rows`

*Swimlane (cross-team/cross-system):*
```
Lane 1 │ [ A ] ──▶ [ B ]
Lane 2 │        [ C ] ──▶ [ D ]
```
→ Use `swimlane`

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
- `labelBackgroundColor` — `generate_drawio.py` sets this automatically (group fill for nodes inside groups, page bg for standalone nodes). Only set manually when editing raw XML during Ralph Loop iterations — it must match the **actual visual background at that position**. See STYLE-REFERENCE.md for colour rules.
- **Dark icon visibility**: before using an icon on a dark background, check if the icon design is dark-coloured (e.g., Github.svg has a black logo). Look for a light-coloured variant in `assets/icons/` (e.g., `github-white-icon.webp`).

---

## Phase 3 — Generate the Diagram

### How it works
You describe the diagram as **JSON** (nodes, edges, labels, types). The `generate_drawio.py` script handles all coordinate math, spacing, and style application from `config.json`. **Do NOT write raw XML yourself** — let the script do it.

### Filename
Name the file `<topic-slug>.drawio` (e.g., `ci-pipeline.drawio`, `network-architecture.drawio`).

### Step 0: Review design principles and known rendering issues

Before writing any JSON, read both reference files in parallel:
- [references/DESIGN-PRINCIPLES.md](references/DESIGN-PRINCIPLES.md) — color semantics, edge routing, whitespace, labeling standards
- [references/CRITIQUE-TEMPLATE.md](references/CRITIQUE-TEMPLATE.md) — specifically the **Quick Fixes Reference** table at the bottom, which lists known rendering issues to avoid during generation (e.g. `data_store` open sides, dashed border export failures)

### Step 1: Choose a layout

Use the user's display format preference from Phase 1 to guide your choice:
- **Wide/landscape** → prefer `flow`, `horizontal`, `grid`, `swimlane`, or `branching`
- **Tall/portrait** → prefer `linear` or `branching`
- **Auto/let me choose** → pick the layout that best fits the diagram's natural structure

| Layout | Screen fit | Use for | How it arranges nodes |
|--------|-----------|---------|----------------------|
| `linear` | Tall | Flowcharts, pipelines, sequential processes | Vertical stack, centred |
| `horizontal` | Wide | Short timelines, left-to-right pipelines (≤6 nodes) | Single row, left to right |
| `pipeline` | Wide | Horizontal pipeline where one or more steps are vertical stacks of items | Uses top-level `"pipeline"` array — each entry is a node ID (single step) or list of node IDs (vertical stack). Flow runs left-to-right; stacks grow top-to-bottom. |
| `rows` | Wide | Any diagram where you control grouping — mixed sequential/parallel flows | Nodes sharing the same `row` value appear side-by-side; row groups stack top-to-bottom. **Best for wide/landscape output.** |
| `flow` | Wide | Long sequential processes where auto-wrapping is fine | Left-to-right rows that wrap — auto-targets ~16:9. Set `flow_columns` to override. |
| `branching` | Balanced | Decision trees, parallel workflows, fan-out/fan-in | BFS levels, siblings side by side |
| `hierarchical` | Balanced | Org charts, taxonomies, tree structures | Same as branching (tree-aware) |
| `grid` | Wide | Dashboards, card layouts, inventories | Rows and columns (set `grid_columns`) |
| `swimlane` | Wide | BPMN, cross-team processes | Horizontal lanes (set `lanes` array, nodes need `lane` field) |

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
| `data_store` | DFD data store — **no vertical side borders** | Avoid for enclosed nodes. This is a DFD symbol with only top/bottom horizontal lines; both vertical sides are open. Use `cylinder` or `process` (`variant: "neutral"`) instead. |
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

**Rows layout field:**
- Each node can have a `"row"` field (any string or integer). Nodes sharing the same `row` value are placed side-by-side (left-to-right). Nodes without a `row` field each occupy their own row.
- Use this to express semantic grouping — parallel steps in the same row, sequential steps in different rows.

**Pipeline layout field:**
- Add a top-level `"pipeline"` array alongside `"nodes"`. Each entry is either a node ID string (single step) or an array of node IDs (vertical stack at that step position).
- The flow runs left-to-right; stacked entries grow top-to-bottom and are vertically centred on the tallest step.
- Example: `"pipeline": ["start", ["worker1", "worker2", "worker3"], "end"]` → start → 3 stacked workers → end

**Example JSON (pipeline):**
```json
{
  "title": "Data Processing Pipeline",
  "layout": "pipeline",
  "nodes": [
    {"id": "ingest",    "label": "Ingest",    "type": "process", "variant": "primary"},
    {"id": "validate",  "label": "Validate",  "type": "process", "variant": "primary"},
    {"id": "stage1",    "label": "Stage 1",   "type": "process", "variant": "secondary"},
    {"id": "stage2",    "label": "Stage 2",   "type": "process", "variant": "secondary"},
    {"id": "stage3",    "label": "Stage 3",   "type": "process", "variant": "secondary"},
    {"id": "output",    "label": "Output",    "type": "success"}
  ],
  "pipeline": ["ingest", "validate", ["stage1", "stage2", "stage3"], "output"],
  "edges": [
    {"from": "ingest",   "to": "validate"},
    {"from": "validate", "to": "stage1"},
    {"from": "validate", "to": "stage2"},
    {"from": "validate", "to": "stage3"},
    {"from": "stage1",   "to": "output"},
    {"from": "stage2",   "to": "output"},
    {"from": "stage3",   "to": "output"}
  ]
}
```
Renders as: `ingest` → `validate` → `stage1/stage2/stage3` (stacked vertically) → `output`

**Example JSON (rows):**
```json
{
  "title": "Deploy Pipeline",
  "layout": "rows",
  "nodes": [
    {"id": "n1", "label": "Push Code",   "type": "start",   "row": 1},
    {"id": "n2", "label": "Run Tests",   "type": "process", "row": 2},
    {"id": "n3", "label": "Lint",        "type": "process", "row": 2},
    {"id": "n4", "label": "Build Image", "type": "process", "row": 3},
    {"id": "n5", "label": "Deploy",      "type": "success", "row": 4}
  ],
  "edges": [
    {"from": "n1", "to": "n2"},
    {"from": "n1", "to": "n3"},
    {"from": "n2", "to": "n4"},
    {"from": "n3", "to": "n4"},
    {"from": "n4", "to": "n5"}
  ]
}
```
n2 and n3 appear side-by-side (row 2), everything else stacks sequentially.

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

## Phase 4 — Render to PNG

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
The renderer defaults to `--scale 2` (2× resolution) and `--border 20` for crisp output with padding.

**Use `--scale 1` during Ralph Loop iterations** — iteration renders are only read by Claude for critique; 1× produces ~75% fewer pixels than 2× for a large token saving with acceptable critique quality. Reserve higher scales for the final deliverable.

```bash
# Ralph Loop iteration renders (token-efficient)
python3 ~/.claude/skills/drawio/scripts/render_drawio.py <filename>.drawio --scale 1

# Final deliverable render (crisp output)
python3 ~/.claude/skills/drawio/scripts/render_drawio.py <filename>.drawio --scale 2

# High-res export (presentations, printing)
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

## Phase 5 — Ralph Loop: Refinement Iterations

**Minimum 3 iterations.** The user can request more by passing `--max-iterations N` (e.g. `/drawio ... --max-iterations 5`). If not specified, use 3.

**Iteration structure (enforced):**
- **Iteration 1: JSON only** — regenerate from the JSON source. No direct XML editing on this iteration.
- **Iterations 2+: XML only** — direct XML edits only. Once XML iterations begin, do not regenerate from JSON again.
- **Minimum 2 XML iterations** — iterations 2 and 3 must both be XML edits, even if the diagram looks good after iteration 2.

This ensures at least one clean JSON-based pass to resolve structural/layout issues, followed by at least two XML polish passes for fine-tuning.

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
List all the changes you will make, then apply them:

**Iteration 1 — JSON regeneration (mandatory):** Update `<filename>.json` with all structural fixes (layout, positioning, node additions/removals, edge changes) and regenerate:
```bash
python3 ~/.claude/skills/drawio/scripts/generate_drawio.py <filename>.json --output <filename>.drawio
```

**Iterations 2+ — Direct XML editing (mandatory):** Edit the `.drawio` XML directly for fine-tuning (edge styles, label tweaks, colours, spacing). Batch all changes into a single edit pass. Do not touch the JSON file.

After applying changes:
1. Validate: `xmllint --noout <filename>.drawio`
   - If validation fails: revert, make a more targeted fix, re-validate before proceeding. Do not render broken XML.
2. Re-render at `--scale 1` for token efficiency (see Phase 4 render quality note)
3. Read the new PNG as a screenshot
4. State: *"Iteration N/<max> complete [JSON|XML]. Changes made: [summary]"*

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
