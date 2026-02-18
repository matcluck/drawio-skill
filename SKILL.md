---
name: drawio
description: Use when the user wants to create a draw.io diagram. Guides requirements gathering, generates valid draw.io XML, renders to PNG, then runs 5 Ralph Loop critique/refine cycles to progressively improve the diagram. Works for any diagram type.
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

Ask these questions **one at a time**. Wait for the answer before asking the next.

1. **Diagram type** — What kind of diagram is this? (system architecture, workflow/flowchart, org chart, network topology, ER/data model, other?)
2. **Components** — What are the main entities, services, or steps? List them.
3. **Relationships** — How do they connect? (sequential flow, parallel branches, data dependencies, hierarchy?)
4. **Detail level** — Brief overview or detailed (with commands, descriptions, tool references)?
5. **Special requirements** — Specific colour scheme (light mode, dark mode)?

After question 5, check if custom icons are available:
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
```
style="shape=image;verticalLabelPosition=bottom;labelBackgroundColor=default;verticalAlign=top;aspect=fixed;imageAspect=0;image=file:///<resolved-icon-dir>/<filename>;"
```

---

## Phase 2 — Generate the .drawio XML

### Progress Updates
**IMPORTANT:** XML generation involves heavy thinking. Keep the user informed so they don't think things are frozen:
- Before reading references: *"Reading style and structural references..."*
- Before generating XML: *"Generating diagram XML — this may take a minute for complex diagrams, hang tight."*
- After writing the file: *"XML written. Validating..."*

Output these messages as plain text **before** the tool call or thinking block that follows. Never go silent for more than one tool call without a status update.

### Filename
Name the file `<topic-slug>.drawio` (e.g., `ci-pipeline.drawio`, `network-architecture.drawio`).

### XML Boilerplate
Every diagram starts with this exact structure:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!-- 🐔 matcluck's drawio-skill | github.com/matcluck -->
<mxfile host="app.diagrams.net" agent="matcluck/drawio-skill">
<diagram name="Page-1" id="REPLACE-WITH-UNIQUE-ID">
<mxGraphModel dx="800" dy="400" grid="1" gridSize="10" guides="1" tooltips="1"
  connect="1" arrows="1" fold="1" page="1" pageScale="1"
  pageWidth="1600" pageHeight="3400" math="0" shadow="0">
<root>
<mxCell id="0" />
<mxCell id="1" parent="0" />
<!-- ALL CONTENT HERE -->
</root>
</mxGraphModel>
</diagram>
</mxfile>
```

- `pageWidth="1600"` always. Content spans ~100px to ~1500px
- `pageHeight` — adjust to fit content. Guide: ~800 for simple (< 10 nodes), ~1600 for medium, ~2400–4200 for large/complex diagrams. The boilerplate uses 3400 as a starting point; shrink or grow as needed
- **Spacing:** 40–60px horizontal gap between sibling elements, 80–120px vertical gap between levels
- **Flow direction:** top to bottom
- Generate a random UUID-style unique ID for the diagram `id` attribute

### Writing Large XML Files
For large diagrams (> 40 mxCell elements), write XML incrementally using bash heredoc append to prevent corruption:

```bash
# Write boilerplate first
cat > diagram.drawio << 'XMLEOF'
<?xml version="1.0" encoding="UTF-8"?>
...opening tags...
XMLEOF

# Append each chunk
cat >> diagram.drawio << 'XMLEOF'
<!-- chunk 1: ~40-60 mxCell elements -->
XMLEOF

cat >> diagram.drawio << 'XMLEOF'
<!-- chunk 2 -->
XMLEOF

# Append closing tags last
cat >> diagram.drawio << 'XMLEOF'
</root></mxGraphModel></diagram></mxfile>
XMLEOF
```

### Element & Edge Style Reference

Read [references/STYLE-REFERENCE.md](references/STYLE-REFERENCE.md) for all element styles (nodes, edges, section headers, colours). Load it before generating any XML.

### Layout & Structural Patterns

Read [references/STRUCTURAL-PATTERNS.md](references/STRUCTURAL-PATTERNS.md) for diagram patterns (linear, branching, hierarchical) by diagram type.

### Starter Templates

Use these pre-positioned skeletons to avoid computing coordinates from scratch. Replace labels/IDs, add/remove rows as needed, and extend the y-axis for more nodes.

**Linear (flowcharts, pipelines) — 5 steps top-to-bottom:**
```xml
<!-- Title -->
<mxCell id="t1" value="TITLE" style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;whiteSpace=wrap;fontSize=36;fontStyle=1" vertex="1" parent="1"><mxGeometry x="100" y="20" width="1400" height="50" as="geometry"/></mxCell>
<!-- START -->
<mxCell id="n1" value="START" style="shape=ellipse;whiteSpace=wrap;html=1;fillColor=#264653;strokeColor=#264653;fontSize=12;fontColor=#FFFFFF;fontStyle=1;" vertex="1" parent="1"><mxGeometry x="710" y="100" width="180" height="80" as="geometry"/></mxCell>
<!-- Step 1 -->
<mxCell id="n2" value="Step 1" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#D6E4F0;strokeColor=#264653;fontSize=11;verticalAlign=top;spacingTop=5;spacingLeft=8;" vertex="1" parent="1"><mxGeometry x="650" y="280" width="300" height="60" as="geometry"/></mxCell>
<mxCell id="e1" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeWidth=2;" edge="1" source="n1" target="n2" parent="1"><mxGeometry relative="1" as="geometry"/></mxCell>
<!-- Step 2 -->
<mxCell id="n3" value="Step 2" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#D6E4F0;strokeColor=#264653;fontSize=11;verticalAlign=top;spacingTop=5;spacingLeft=8;" vertex="1" parent="1"><mxGeometry x="650" y="440" width="300" height="60" as="geometry"/></mxCell>
<mxCell id="e2" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeWidth=2;" edge="1" source="n2" target="n3" parent="1"><mxGeometry relative="1" as="geometry"/></mxCell>
<!-- Step 3 -->
<mxCell id="n4" value="Step 3" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#D6E4F0;strokeColor=#264653;fontSize=11;verticalAlign=top;spacingTop=5;spacingLeft=8;" vertex="1" parent="1"><mxGeometry x="650" y="600" width="300" height="60" as="geometry"/></mxCell>
<mxCell id="e3" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeWidth=2;" edge="1" source="n3" target="n4" parent="1"><mxGeometry relative="1" as="geometry"/></mxCell>
<!-- END -->
<mxCell id="n5" value="END" style="shape=ellipse;whiteSpace=wrap;html=1;fillColor=#264653;strokeColor=#264653;fontSize=12;fontColor=#FFFFFF;fontStyle=1;" vertex="1" parent="1"><mxGeometry x="720" y="760" width="170" height="70" as="geometry"/></mxCell>
<mxCell id="e4" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeWidth=2;" edge="1" source="n4" target="n5" parent="1"><mxGeometry relative="1" as="geometry"/></mxCell>
```
Y-spacing: 160px per step. To add more steps, continue at y+160 and shift END down.

**Branching (3-way split and merge):**
```xml
<!-- Title -->
<mxCell id="t1" value="TITLE" style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;whiteSpace=wrap;fontSize=36;fontStyle=1" vertex="1" parent="1"><mxGeometry x="100" y="20" width="1400" height="50" as="geometry"/></mxCell>
<!-- START -->
<mxCell id="n1" value="START" style="shape=ellipse;whiteSpace=wrap;html=1;fillColor=#264653;strokeColor=#264653;fontSize=12;fontColor=#FFFFFF;fontStyle=1;" vertex="1" parent="1"><mxGeometry x="710" y="100" width="180" height="80" as="geometry"/></mxCell>
<!-- Split junction -->
<mxCell id="j1" style="shape=ellipse;whiteSpace=wrap;html=1;fillColor=#264653;strokeColor=#264653;" vertex="1" parent="1"><mxGeometry x="790" y="260" width="20" height="20" as="geometry"/></mxCell>
<mxCell id="e0" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeWidth=2;" edge="1" source="n1" target="j1" parent="1"><mxGeometry relative="1" as="geometry"/></mxCell>
<!-- Branch A (left) -->
<mxCell id="bA" value="Branch A" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#D6E4F0;strokeColor=#264653;fontSize=11;verticalAlign=top;spacingTop=5;spacingLeft=8;" vertex="1" parent="1"><mxGeometry x="250" y="360" width="280" height="60" as="geometry"/></mxCell>
<mxCell id="eA" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeWidth=2;" edge="1" source="j1" target="bA" parent="1"><mxGeometry relative="1" as="geometry"/></mxCell>
<!-- Branch B (centre) -->
<mxCell id="bB" value="Branch B" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#c9daf8;strokeColor=#3d5a80;fontSize=11;verticalAlign=top;spacingTop=5;spacingLeft=8;" vertex="1" parent="1"><mxGeometry x="660" y="360" width="280" height="60" as="geometry"/></mxCell>
<mxCell id="eB" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeWidth=2;" edge="1" source="j1" target="bB" parent="1"><mxGeometry relative="1" as="geometry"/></mxCell>
<!-- Branch C (right) -->
<mxCell id="bC" value="Branch C" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f4cccc;strokeColor=#6a040f;fontSize=11;verticalAlign=middle;align=center;" vertex="1" parent="1"><mxGeometry x="1070" y="360" width="280" height="60" as="geometry"/></mxCell>
<mxCell id="eC" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeWidth=2;" edge="1" source="j1" target="bC" parent="1"><mxGeometry relative="1" as="geometry"/></mxCell>
<!-- Merge junction -->
<mxCell id="j2" style="shape=ellipse;whiteSpace=wrap;html=1;fillColor=#264653;strokeColor=#264653;" vertex="1" parent="1"><mxGeometry x="790" y="500" width="20" height="20" as="geometry"/></mxCell>
<mxCell id="emA" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeWidth=2;" edge="1" source="bA" target="j2" parent="1"><mxGeometry relative="1" as="geometry"/></mxCell>
<mxCell id="emB" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeWidth=2;" edge="1" source="bB" target="j2" parent="1"><mxGeometry relative="1" as="geometry"/></mxCell>
<mxCell id="emC" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeWidth=2;" edge="1" source="bC" target="j2" parent="1"><mxGeometry relative="1" as="geometry"/></mxCell>
<!-- END -->
<mxCell id="n5" value="END" style="shape=ellipse;whiteSpace=wrap;html=1;fillColor=#264653;strokeColor=#264653;fontSize=12;fontColor=#FFFFFF;fontStyle=1;" vertex="1" parent="1"><mxGeometry x="720" y="600" width="170" height="70" as="geometry"/></mxCell>
<mxCell id="e9" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeWidth=2;" edge="1" source="j2" target="n5" parent="1"><mxGeometry relative="1" as="geometry"/></mxCell>
```
Branch x-positions: 250, 660, 1070 (410px apart). For 2 branches use 400 and 860. For 4+ branches, space evenly across 200–1400.

**Hierarchical (org charts, taxonomies) — root + 3 children + 4 grandchildren:**
```xml
<!-- Title -->
<mxCell id="t1" value="TITLE" style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;whiteSpace=wrap;fontSize=36;fontStyle=1" vertex="1" parent="1"><mxGeometry x="100" y="20" width="1400" height="50" as="geometry"/></mxCell>
<!-- Root -->
<mxCell id="r1" value="Root" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#264653;strokeColor=#264653;fontSize=13;fontColor=#FFFFFF;fontStyle=1;" vertex="1" parent="1"><mxGeometry x="650" y="100" width="300" height="60" as="geometry"/></mxCell>
<!-- Child A -->
<mxCell id="cA" value="Child A" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#D6E4F0;strokeColor=#264653;fontSize=11;verticalAlign=top;spacingTop=5;spacingLeft=8;" vertex="1" parent="1"><mxGeometry x="170" y="260" width="280" height="60" as="geometry"/></mxCell>
<mxCell id="erA" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeWidth=2;" edge="1" source="r1" target="cA" parent="1"><mxGeometry relative="1" as="geometry"/></mxCell>
<!-- Child B -->
<mxCell id="cB" value="Child B" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#D6E4F0;strokeColor=#264653;fontSize=11;verticalAlign=top;spacingTop=5;spacingLeft=8;" vertex="1" parent="1"><mxGeometry x="660" y="260" width="280" height="60" as="geometry"/></mxCell>
<mxCell id="erB" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeWidth=2;" edge="1" source="r1" target="cB" parent="1"><mxGeometry relative="1" as="geometry"/></mxCell>
<!-- Child C -->
<mxCell id="cC" value="Child C" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#D6E4F0;strokeColor=#264653;fontSize=11;verticalAlign=top;spacingTop=5;spacingLeft=8;" vertex="1" parent="1"><mxGeometry x="1150" y="260" width="280" height="60" as="geometry"/></mxCell>
<mxCell id="erC" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeWidth=2;" edge="1" source="r1" target="cC" parent="1"><mxGeometry relative="1" as="geometry"/></mxCell>
<!-- Grandchild A1 -->
<mxCell id="gA1" value="A1" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#c9daf8;strokeColor=#3d5a80;fontSize=11;verticalAlign=top;spacingTop=5;spacingLeft=8;" vertex="1" parent="1"><mxGeometry x="80" y="420" width="220" height="50" as="geometry"/></mxCell>
<mxCell id="eA1" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeWidth=2;" edge="1" source="cA" target="gA1" parent="1"><mxGeometry relative="1" as="geometry"/></mxCell>
<!-- Grandchild A2 -->
<mxCell id="gA2" value="A2" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#c9daf8;strokeColor=#3d5a80;fontSize=11;verticalAlign=top;spacingTop=5;spacingLeft=8;" vertex="1" parent="1"><mxGeometry x="320" y="420" width="220" height="50" as="geometry"/></mxCell>
<mxCell id="eA2" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeWidth=2;" edge="1" source="cA" target="gA2" parent="1"><mxGeometry relative="1" as="geometry"/></mxCell>
<!-- Grandchild C1 -->
<mxCell id="gC1" value="C1" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#c9daf8;strokeColor=#3d5a80;fontSize=11;verticalAlign=top;spacingTop=5;spacingLeft=8;" vertex="1" parent="1"><mxGeometry x="1060" y="420" width="220" height="50" as="geometry"/></mxCell>
<mxCell id="eC1" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeWidth=2;" edge="1" source="cC" target="gC1" parent="1"><mxGeometry relative="1" as="geometry"/></mxCell>
<!-- Grandchild C2 -->
<mxCell id="gC2" value="C2" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#c9daf8;strokeColor=#3d5a80;fontSize=11;verticalAlign=top;spacingTop=5;spacingLeft=8;" vertex="1" parent="1"><mxGeometry x="1300" y="420" width="220" height="50" as="geometry"/></mxCell>
<mxCell id="eC2" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeWidth=2;" edge="1" source="cC" target="gC2" parent="1"><mxGeometry relative="1" as="geometry"/></mxCell>
```
Level spacing: 160px vertical. Sibling spacing: ~240–490px horizontal depending on count.

Pick the closest template, then adapt: rename labels, add/remove nodes, adjust y-values. This is **much faster** than computing every coordinate from scratch.

### Validate Before Saving
After writing the file, always run:
```bash
xmllint --noout <filename>.drawio && echo "Valid XML" || echo "XML ERROR"
```

If validation fails: fix the XML, do not proceed to rendering.

### Pre-Delivery Checklist
Before proceeding to Phase 3, verify:
- [ ] Valid XML (passes `xmllint --noout`)
- [ ] All `mxCell` elements have `parent="1"`
- [ ] All nodes have `vertex="1"`, all edges have `edge="1"`
- [ ] Every edge has valid `source` and `target` IDs that exist in the file
- [ ] No orphaned cells (everything connected)
- [ ] Styles match STYLE-REFERENCE.md for all element types used
- [ ] All elements from the requirements are present

---

## Phase 3 — Render to PNG

Run the render script (`scripts/render_drawio.py` relative to this skill's directory):
```bash
python3 ~/.claude/skills/drawio/scripts/render_drawio.py <filename>.drawio
```

**If rendering fails:** Deliver the `.drawio` XML file to the user and inform them:
> "Rendering failed. The `.drawio` file is ready — open it at [app.diagrams.net](https://app.diagrams.net) or in the draw.io desktop app."
Then skip Phase 4 and stop.

After successful render, read the output PNG as a screenshot using the Read tool.
Briefly describe what you see in the rendered diagram before entering Phase 4.

---

## Phase 4 — Ralph Loop: 5 Refinement Iterations

Invoke the ralph-loop skill to begin iterative refinement.

**REQUIRED:** Use the `ralph-loop:ralph-loop` skill now with arguments. Pass the diagram filename as the prompt and set `--max-iterations 5`:
```
Skill: ralph-loop:ralph-loop
Args: Refine <filename>.drawio diagram --max-iterations 5
```

For each of the 5 iterations, follow this structure:

### Iteration Critique

Read [references/CRITIQUE-TEMPLATE.md](references/CRITIQUE-TEMPLATE.md) and critique the current PNG against each category (layout, connections, style, content).

### After Critique
List the specific changes you will make, then:
1. Edit the `.drawio` file to implement all improvements
2. Validate: `xmllint --noout <filename>.drawio`
   - If validation fails: revert the edit (restore the previous valid XML), make a more targeted fix, and re-validate before proceeding. Do not render broken XML.
3. Re-render: `python3 ~/.claude/skills/drawio/scripts/render_drawio.py <filename>.drawio`
4. Read the new PNG as a screenshot
5. State: *"Iteration N/5 complete. Changes made: [summary]"*

### After 5 Iterations
Cancel the Ralph Loop using `ralph-loop:cancel-ralph`.

### Final Adjustments

Ask the user: *"Would you like any final adjustments before I package the diagram? (e.g., colours, layout tweaks, missing labels, icon changes)"*

If the user requests changes, make them, re-validate, and re-render. Repeat until the user confirms they're happy.

### Embed Icons for Portability

Once the user is satisfied, embed all `file:///` icon URIs as base64 so the diagram is self-contained when shared:
```bash
python3 ~/.claude/skills/drawio/scripts/embed_icons.py <filename>.drawio
```
This creates a `.drawio.bak` backup and modifies the file in place. Validate after: `xmllint --noout <filename>.drawio`

Optionally rename the final PNG for clarity:
```bash
cp <filename>.png <filename>-final.png
```

Present the final output:
```
Diagram complete.

Files:
  <filename>.drawio   — draw.io source file (icons embedded, portable)
  <filename>.png      — rendered PNG

Open <filename>.drawio in draw.io (app.diagrams.net) to view and edit interactively.
```
