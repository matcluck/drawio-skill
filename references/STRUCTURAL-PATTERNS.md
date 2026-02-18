# Structural Patterns

**Source of truth: [`scripts/config.json`](../scripts/config.json)** for spacing and dimensions.

These patterns map to the `layout` field in the JSON input for `generate_drawio.py`.

## Layout Types

### `linear` — Flowcharts, pipelines, sequential processes
```
           TITLE
         Optional subtitle

         (  START  )
              ↓
         ┌──────────┐
         │  Step A   │
         └──────────┘
              ↓
         ┌──────────┐
         │  Step B   │
         └──────────┘
              ↓
         (   END   )
```
Top-to-bottom vertical stack, all nodes centred on the page. Best for simple sequential flows with minimal branching.

**Tips:**
- Keep to 5–8 nodes for readability
- Use `detail` fields for subprocess info rather than adding more nodes
- Pair with `groups` to visually section long flows

### `horizontal` — Timelines, left-to-right processes
```
TITLE
Subtitle

┌──────┐    ┌──────┐    ┌──────┐    ┌──────┐
│Step A│ →  │Step B│ →  │Step C│ →  │Step D│
└──────┘    └──────┘    └──────┘    └──────┘
```
Single row, left to right, vertically centred. Nodes are centred on the page.

**Tips:**
- Ideal for 3–6 nodes (beyond that, horizontal scrolling becomes awkward)
- Use `curved` edge style for a cleaner look
- Great for timelines with chronological labels

### `branching` — Decision trees, parallel workflows, fan-out/fan-in
```
           TITLE

         (  START  )
              ↓
         ◇ Decision ◇
        ↓      ↓      ↓
     ┌────┐ ┌────┐ ┌────┐
     │ A  │ │ B  │ │ C  │
     └────┘ └────┘ └────┘
        ↓      ↓      ↓
         ┌──────────┐
         │  MERGE   │
         └──────────┘
              ↓
         (   END   )
```
BFS level assignment. Nodes at the same depth sit side by side, centred. Merge points (multiple parents) are placed at the deepest required level.

**Tips:**
- Use `decision` type for branch points (diamond shape makes intent clear)
- Label edges at branch points (e.g. "Yes" / "No" / "Error")
- Use coloured edges to distinguish paths (green=success, red=error)
- Groups can highlight parallel branches

### `hierarchical` — Org charts, taxonomies, tree structures
```
            ┌──────────┐
            │   Root    │
            └──────────┘
          ↓       ↓       ↓
     ┌──────┐ ┌──────┐ ┌──────┐
     │  A   │ │  B   │ │  C   │
     └──────┘ └──────┘ └──────┘
      ↓    ↓              ↓    ↓
   ┌────┐┌────┐       ┌────┐┌────┐
   │ A1 ││ A2 │       │ C1 ││ C2 │
   └────┘└────┘       └────┘└────┘
```
Same engine as branching — arranges by parent→child depth. Best for trees where each node has exactly one parent.

**Tips:**
- Use `variant` colours to distinguish hierarchy levels (e.g. primary→secondary→neutral)
- Keep tree depth to 3–4 levels for visual clarity
- Use `actor` type for people in org charts

### `grid` — Dashboards, card layouts, inventories
```
┌──────┐  ┌──────┐  ┌──────┐
│  A   │  │  B   │  │  C   │
└──────┘  └──────┘  └──────┘
┌──────┐  ┌──────┐  ┌──────┐
│  D   │  │  E   │  │  F   │
└──────┘  └──────┘  └──────┘
```
Set `grid_columns` in the JSON (default: 3). Nodes fill left-to-right, top-to-bottom. Each row is vertically centred on the tallest node.

**Tips:**
- Use consistent node types per row for visual uniformity
- `icon` nodes work especially well in grid layout (service catalogs, tool inventories)
- Use `detail` for metadata under each card
- Grid + groups can create categorized dashboards

### `swimlane` — BPMN, cross-team processes, responsibility charts
```
┌─── Dev ─────────────────────────────┐
│    ┌──────┐  ┌──────┐  ┌──────┐    │
│    │ Code │→ │ Test │→ │  PR  │    │
│    └──────┘  └──────┘  └──────┘    │
├─── QA ──────────────────────────────┤
│    ┌────────┐  ┌──────────┐         │
│    │ Review │→ │ Sign off │         │
│    └────────┘  └──────────┘         │
├─── Ops ─────────────────────────────┤
│    ┌────────┐  ┌─────────┐          │
│    │ Deploy │→ │ Monitor │          │
│    └────────┘  └─────────┘          │
└─────────────────────────────────────┘
```
Each node needs a `lane` field matching a lane ID. Define lanes in the `lanes` array. Lane heights auto-adjust based on content.

**Tips:**
- Use `dashed` edges for cross-lane connections (makes handoffs visible)
- Colour-code lanes with the `color` field for quick scanning
- Keep 2–4 nodes per lane for readability
- Labels on cross-lane edges clarify what gets passed between teams

## Choosing a layout

| Diagram type | Recommended layout | Notes |
|---|---|---|
| Flowchart / process | `linear` or `branching` | Linear for sequential, branching for decisions |
| Pipeline / CI-CD | `linear` or `horizontal` | Horizontal for short pipelines |
| Org chart / taxonomy | `hierarchical` | Use `actor` nodes for people |
| System architecture | `branching` with groups | Groups highlight service boundaries |
| Decision tree | `branching` | Colour edges for branch outcomes |
| BPMN / cross-team flow | `swimlane` | One lane per team/role |
| Dashboard / inventory | `grid` | `icon` nodes for service catalogs |
| Timeline | `horizontal` | Chronological left-to-right |
| Network topology | `hierarchical` with groups | Groups for network segments |
| Data flow diagram | `branching` | Use `data_store` and `cylinder` types |
| Entity relationship | `grid` or `branching` | Grid for overview, branching for relationships |

## Spacing Reference

| Parameter | Value | Description |
|-----------|-------|-------------|
| `v_gap` | 120px | Vertical gap baseline |
| `h_gap` | 80px | Horizontal gap between nodes |
| `min_edge_gap` | 40px | Minimum space between node edges |
| `group_padding` | 48px | Padding inside group boxes |
| `title_bottom_margin` | 60px | Space below title before content |
| `swimlane_header` | 44px | Height of lane label header |
| `swimlane_padding` | 32px | Padding inside swimlane lanes |
