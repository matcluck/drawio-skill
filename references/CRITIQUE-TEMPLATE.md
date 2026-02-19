# Diagram Critique Template

Use this template for each Ralph Loop iteration to systematically review the rendered diagram.

## 1. Layout & Spacing
- Are elements overlapping or too cramped?
- Is the flow direction clear and consistent (top→bottom, left→right)?
- Are related elements aligned properly (centres aligned on vertical/horizontal axes)?
- Is there enough breathing room between nodes? (minimum 40px edge gap)
- Does the title area have adequate separation from the diagram content?
- Are groups/containers sized with sufficient padding around their members?

## 2. Visual Hierarchy
- Can you immediately identify the start and end points?
- Do primary flow nodes stand out from supporting/annotation nodes?
- Are decision points visually distinct (diamond shape, different fill)?
- Is there a clear reading order through the diagram?
- Do node sizes reflect their relative importance?

## 3. Connections & Edges
- Are there orphaned nodes with no edges?
- Are all logical relationships represented?
- Do edges connect to the correct source and target?
- Are edges crossing through text labels? Fix by ensuring `labelBackgroundColor` is set to match the **actual visual background at that position** (page bg for top-level nodes; group fill for nodes inside a coloured group — see STYLE-REFERENCE.md for colour rules)
- Are edge labels legible and positioned clearly?
- For branching paths, are edges labelled with the condition (Yes/No, Success/Fail)?
- Are bidirectional relationships using the bidirectional edge style?
- **Are edges defined BEFORE nodes in the XML?** Edges render behind node labels only when declared earlier in the XML. If arrows appear on top of labels, move all edge `<mxCell>` elements above all vertex `<mxCell>` elements.
- **Do fan-out edges from a single source use `edgeStyle=none;curved=1`?** Orthogonal fan-out creates a horizontal bus segment at node level that routes through sibling nodes. Use curved style to avoid this.
- **Do any edges route through unrelated nodes?** Check each edge path. Fix with explicit `<Array as="points">` waypoints to force routing around intermediate nodes.
- **Do edges FROM icon nodes carry labels?** Icon nodes use `verticalLabelPosition=bottom` — their label text renders ~50px below the cell bounds. Edge labels on edges exiting icon nodes appear in the same vertical zone, creating text-on-text overlap. **Remove labels from all edges that exit an icon node** (set `value=""`).

## 4. Colour & Style Consistency
- Are fill colours correct for each element type (check against config.json palette)?
- Are stroke colours matching their fill colour family (not mixed)?
- Are edge colours used semantically (green=success, red=error, etc.)?
- Is `strokeWidth=1.5` consistent across all shapes and edges?
- Are there any shadows that shouldn't be there? (all shadow=0)
- Are process variants used consistently (same colour = same meaning throughout)?
- **Dark mode fill legibility**: Do all coloured fills have enough chrominance to read as their intended hue on the dark background? Fills that are too close to black (e.g. `#1C1200`) look muddy/brownish — compare against well-working fills like blue `#1E3A5F`, green `#064E3B`, purple `#4C1D95`. Amber/yellow and red fills are most prone to this because near-black warm tones look identical to the dark background.

## 5. Typography
- Is font sizing consistent: 13px for node labels, 11px for edge labels, 10px for details?
- Are all fonts set to Helvetica (except dark_panel which uses Courier New)?
- Is the title rendered at 24px bold?
- Is the subtitle (if present) rendered at 13px in slate-400 (#94A3B8)?
- Are detail subtexts using the muted colour (#64748B)?

## 6. Icons (if used)
- Are icons rendering with correct transparency (no white/opaque backgrounds)?
- Are icons sharp and not pixelated or blurry?
- Is the aspect ratio preserved (not stretched or squashed)?
- Are icons consistently sized relative to each other?
- Do icon labels appear below the icon (verticalLabelPosition=bottom)?
- **For dark diagrams: are icon designs visible on the dark background?** Icons with dark-coloured artwork (black logos, dark line art) are invisible on dark backgrounds. Check with `python3 ~/.claude/skills/drawio/scripts/invert_dark_icons.py --check <icon>`. If marked DARK, create a light variant with `python3 ~/.claude/skills/drawio/scripts/invert_dark_icons.py <icon>` and update the `image=` reference in the XML.

## 7. Completeness
- Are all elements from the requirements present?
- Are labels clear, complete, and free of truncation?
- Is any supporting context needed (legend, notes, annotations)?
- For complex diagrams: would grouping improve clarity?
- For process flows: are error/exception paths shown?

## Quick Fixes Reference

| Issue | Fix |
|-------|-----|
| Edge label overlaps line | Add `labelBackgroundColor=#FFFFFF;` to edge style |
| Node text truncated | Increase node width or use `detail` for overflow |
| Colours look off | Copy exact style from config.json, don't approximate |
| Nodes misaligned | Adjust x/y to align centres (x + width/2 should match) |
| Too cramped | Increase spacing by adjusting node positions (+40px gaps) |
| Group too tight | Increase group padding (gx - 48, gy - 72, gw + 96, gh + 72) |
| Arrows render on top of labels | Move all edge mxCells before all vertex mxCells in XML |
| Icon label shows HTML as literal text | Add `html=1;` to icon node style |
| Icon aspect ratio distorted | Change `imageAspect=0` → `imageAspect=1` in icon node style |
| Label background wrong colour inside group | Set `labelBackgroundColor` to group fill colour, not page bg |
| Group clips icon labels | Icon labels overflow ~50px below cell; increase group height to cover `node_y + node_h + 50 + 40` |
| Fan-out arrows routing through siblings | Change fan-out edges to `edgeStyle=none;curved=1` |
| Edge routes through unrelated node | Add `<Array as="points">` waypoints to detour around the node |
| Dark icon invisible on dark background | Use light-coloured icon variant (e.g., `github-white-icon.webp`) or run `python3 ~/.claude/skills/drawio/scripts/invert_dark_icons.py <icon>` to create `<name>-light.<ext>` |
| Dark mode fill looks muddy/brownish | Fill is too close to black — increase chrominance so at least one RGB channel ≥70 (e.g. amber `#78350F`, red `#7F1D1D`) |
| Child not centred under parent | Align: set child `x = parent_x + (parent_w - child_w) / 2` |
| Edge label overlaps icon node's text | Icon labels render 50px below cell bounds — remove labels from edges exiting icon nodes (set `value=""`) |
| Node box missing one or both side borders | `data_store` type uses `shape=mxgraph.dfd.dataStoreID` — a DFD symbol that draws only the top and bottom horizontal lines, leaving both vertical sides open. **Never use `data_store` for nodes that need fully enclosed boxes.** Use a plain `process` node with `variant: "neutral"` instead (`rounded=1;fillColor=#F1F5F9;strokeColor=#94A3B8`). |
| Group box missing border side(s) in PNG export | `dashed=1` on rounded rectangles can fail to complete all sides during PNG export. Remove `dashed=1;dashPattern=...` and use a solid border (`strokeWidth=2`). |
