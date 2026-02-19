# Diagram Design Principles

> **Sources:** Microsoft Azure Well-Architected Framework (2025), C4 Model — Simon Brown (c4model.com),
> Ware & Purchase "Cognitive Measurements of Graph Aesthetics" (2002), AWS Architecture Guidelines,
> Creately Diagram Design Guide, Nielsen Norman Group Visual Design

---

## 1. Core Philosophy

A well-designed diagram communicates its content without requiring verbal explanation. Aesthetics are not decoration — research shows that visually cleaner diagrams produce measurably lower cognitive load and faster comprehension. Every design decision should serve clarity.

Design for your audience. An executive overview needs different depth than a developer implementation guide. If a single diagram is trying to serve both, split it into two.

---

## 2. Visual Hierarchy

Guide the viewer's eye from most to least important:

- **Size** — larger elements carry more visual weight; use it deliberately
- **Color saturation** — brighter fills draw attention before muted ones
- **Position** — top-left and centre are natural focal points in Western reading patterns
- **Shape distinctiveness** — start/end nodes should be visually unlike process nodes
- **Border weight** — heavier strokes emphasise; lighter strokes recede

The start and end points of any flow must be identifiable at a glance. Primary flow nodes should visually dominate supporting and annotation nodes.

---

## 3. Color

**Limit the palette to 3–4 semantic colors.** Each color must mean something — it is not decoration.

Rules:
- Assign one meaning per color and apply it consistently throughout the diagram
- Never use two different colors to mean the same thing
- Never use the same color to mean two different things
- Always pair color with a second visual indicator (shape, border style, icon) — color alone excludes colorblind viewers
- Muted fills (light tints) with saturated strokes give a modern, readable look
- Avoid red/green pairs as the primary distinction — approximately 8% of males cannot distinguish them
- **Only use the colors you need** — if the diagram has no errors, don't add red just to fill out the palette

**Semantic color conventions (established across tools and teams):**

| Color | Conventional meaning |
|-------|---------------------|
| Blue | Primary flow, default process |
| Green | Success, completion, happy path |
| Red/Pink | Error, failure, critical path, danger |
| Orange/Yellow | Warning, caution, decision, external dependency |
| Purple | Async, event-driven, highlighted/accent |
| Grey | Neutral, optional, background, disabled |

---

## 3a. Color Scheme Selection

### The tint + stroke pattern (most important)

Modern diagram color works on a **light tint fill with saturated stroke** model — never use fully saturated or dark fills as the primary node color. Dark/saturated fills compete with each other, make text hard to read, and look heavy and dated.

```
✅ Good: fillColor=#DBEAFE  strokeColor=#3B82F6   (light blue fill, saturated blue border)
❌ Bad:  fillColor=#1E40AF  strokeColor=#1E3A8A   (dark blue fill — heavy, hard to read)
❌ Bad:  fillColor=#F59E0B  strokeColor=#D97706   (saturated orange fill — garish)
```

The fill provides a soft color cue; the stroke provides the definition. Together they look intentional. Saturated fills alone look like clip art.

### Start with the built-in palette

The palette in `config.json` is already harmonized — Tailwind-inspired tints with matching saturated strokes. Use it before inventing colors.

| Name | Fill | Stroke | Use |
|------|------|--------|-----|
| Blue | `#DBEAFE` | `#3B82F6` | Primary flow, default |
| Green | `#D1FAE5` | `#10B981` | Success, completion |
| Orange | `#FEF3C7` | `#F59E0B` | Warning, decisions |
| Purple | `#EDE9FE` | `#8B5CF6` | Accent, async |
| Red | `#FFE4E6` | `#F43F5E` | Error, danger |
| Yellow | `#FEF9C3` | `#EAB308` | Notes, annotations |
| Grey | `#F1F5F9` | `#94A3B8` | Neutral, background |
| Cyan | `#CFFAFE` | `#06B6D4` | Info, data flow |

### Choosing a scheme for the diagram's tone

**Default (most diagrams):** Blue primary, grey supporting, one accent only when needed. Clean, professional, universally readable.

**Executive/stakeholder presentation:** Blue + grey only. Minimal color = easier to read quickly. Resist adding more colors just because they're available.

**Technical/developer diagram:** Full semantic palette is appropriate — blue primary, green success, red error, orange warning. Use each color only for its semantic meaning.

**Process/workflow with no error paths:** Blue + green + grey. No red or orange unless caution is genuinely needed. Diagrams that use warning colors for non-warning content create false alarm.

**Dark mode:** Invert the model — dark fills with lighter strokes and white text. Use the `dark` section of `config.json` rather than inventing dark equivalents of the light palette.

**Dark mode fill legibility rule:** Every dark fill must have enough chrominance (color saturation) to read as its intended hue against the page background (`#0F172A`). Near-black fills like `#1C1200` or `#1C0010` appear muddy and indistinguishable from the background — warm hues (amber, red) are especially prone to this because near-black warm tones read as "dirty" rather than colored. Target fills where at least one RGB channel is ≥70 (e.g. amber `#78350F` = RGB 120,53,15; red `#7F1D1D` = RGB 127,29,29) so the hue is clearly visible.

### Harmony rules when picking custom colors

If you need to go outside the built-in palette:

1. **Analogous colors** (adjacent on the color wheel) create harmony — blue + cyan + purple feel cohesive. Blue + orange + red do not.
2. **Keep saturation consistent** — mixing a pastel with a vivid color looks accidental. All fills should be at a similar tint level.
3. **One neutral always** — grey or slate anchors the palette. A diagram with only vivid colors has no visual rest points.
4. **Text contrast** — dark text (`#1E293B`) needs a light fill. Light text (`#E2E8F0`) needs a dark fill. Never put mid-grey text on a mid-grey fill.
5. **Test in greyscale** — a harmonious palette should show clear contrast differences even without color. If everything becomes the same grey, the palette isn't working.

---

## 4. Typography

- **Single font family** throughout. Mixing fonts creates visual noise.
- **Sans-serif** (Helvetica, Inter, Arial) for modern, readable diagrams — avoid serif fonts in technical contexts
- **Three size levels maximum:**
  - Title: 22–24px bold
  - Node labels: 12–14px regular
  - Detail/secondary text: 10–11px, muted color
- Use **weight** (bold vs. regular) rather than size changes for emphasis within a level
- Keep label text short — if you need more than 5 words, use a detail subtext field
- Edge labels: 10–11px, muted color, always with a background color to prevent overlap with the line

---

## 5. Layout & Flow

**Establish one reading direction and maintain it across the entire diagram.**

- Top-to-bottom is natural for sequential processes
- Left-to-right reads faster — research shows horizontal scanning is faster because the visual field is wider horizontally
- Never mix both directions in the same diagram

**Progressive disclosure — layer, don't overload:**
- One diagram = one idea at one level of abstraction
- A context overview diagram should not also contain implementation detail
- If a diagram feels crowded, it is doing too much — split it

**Grouping:**
- Use groups and containers only when they genuinely add clarity
- A group that contains only one element adds nothing — remove it
- Groups at the same level of abstraction should be visually similar

**Grid alignment:**
- Align node centers on a grid — misalignment reads as error, not style
- Consistent spacing signals structure; irregular spacing signals chaos

---

## 6. Edges & Connections

Research on graph aesthetics (Ware & Purchase, 2002) identified the following ranked by impact on readability:

1. **Minimize edge crossings** — by far the most important factor. Each crossing forces the viewer to mentally untangle which line goes where. Rearrange nodes before accepting crossings.
2. **Minimize edge bends** — each bend adds cognitive work. Prefer straight or gently curved edges over sharp right-angle detours.
3. **Maximize path continuity** — a flow that continues in the same direction is easier to follow than one that reverses or zigzags.
4. **Symmetry** — symmetric layouts aid recall but can conflict with minimizing crossings; prioritize crossing reduction.

**Directional rules:**
- Every edge must have a directional arrow — bare lines are ambiguous
- Avoid double-headed arrows; they imply mutual dependency which is usually not what you mean. Use two separate arrows instead.
- Arrow direction must match the label description (if label says "sends request to", arrow points toward the receiver)

**Labeling edges:**
- Every edge should have a label unless the relationship is completely unambiguous from context
- Label what flows, not just that something flows ("HTTP GET /users" not "calls")
- For branching paths, label each branch with its condition (Yes/No, Success/Error, 200/404)

---

## 7. Whitespace & Information Density

Whitespace is not wasted space — it reduces cognitive load by separating concerns visually.

- Minimum 40px gap between node edges (not node centers)
- Title area needs clear separation from diagram content
- Groups/containers need internal padding — content that touches the border feels trapped
- If you are tempted to shrink spacing to fit more content, that is a signal to split the diagram

**The right amount of information:** Include what the viewer needs to understand the diagram's purpose. Omit everything else. Adding detail to appear thorough usually harms comprehension.

---

## 8. Labeling & Metadata

Every diagram must have:
- **A title** that names the diagram type and scope (e.g. "Container Diagram — Payment Service")
- **A legend** if any notation is not immediately self-evident — shapes, colors, border styles, arrow types

Every element must have:
- **A name** — no unnamed boxes
- **A description** of what it does, not just what it is ("Validates JWT tokens and routes requests" not "API Gateway")
- **Technology choices** visible where relevant (language, protocol, version)

Every relationship must have:
- **A label** describing what flows or what the relationship means
- **A direction** expressed by the arrow
- **Technology/protocol** shown on inter-process connections where the viewer needs it

No diagram should contain unexplained acronyms or abbreviations.

---

## 9. Accessibility

- Ensure sufficient color contrast — minimum 4.5:1 ratio for text against its background
- Never rely on color as the only differentiator — always pair with shape, border style, or pattern
- Design to remain usable in black and white (grayscale test: print it, can you still read it?)
- Avoid red/green as the primary distinguishing pair
- Icon labels should appear as text, not be embedded in the icon only

---

## 10. Diagram Review Checklist

Work through this before declaring a diagram done. Based on C4 model review principles, rephrased as requirements.

### Overall
- [ ] The diagram has a clear, descriptive title
- [ ] The diagram type and scope are immediately obvious
- [ ] A legend is present for any non-obvious notation
- [ ] The reading direction is consistent throughout

### Elements
- [ ] Every element has a name
- [ ] Every element has a description that explains what it does
- [ ] Technology choices are visible where the viewer needs them
- [ ] No unexplained acronyms or abbreviations
- [ ] Color meaning is consistent with the legend
- [ ] Shape meaning is consistent and explained
- [ ] Border styles (solid, dashed, etc.) are explained if varied

### Relationships
- [ ] Every edge has a directional arrow
- [ ] Every edge has a label (or the relationship is truly self-evident)
- [ ] Arrow direction matches the label description
- [ ] Technology/protocol shown on inter-process connections
- [ ] Branching paths are labelled with their conditions
- [ ] Line styles are explained if varied

### Visual quality
- [ ] Edge crossings minimized — rearrange nodes if possible
- [ ] Edge bends minimized — prefer straight or gently curved paths
- [ ] Nodes are grid-aligned with consistent spacing
- [ ] Color palette is 3–4 colors maximum
- [ ] All fills use the tint + stroke pattern (light fill, saturated stroke) — no dark/saturated fills
- [ ] Colors are only used where they carry semantic meaning — no decorative color
- [ ] A single font family is used throughout
- [ ] Whitespace is sufficient — no cramped sections
- [ ] The diagram would still be readable in black and white
