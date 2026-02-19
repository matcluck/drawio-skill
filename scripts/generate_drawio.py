#!/usr/bin/env python3
"""
generate_drawio.py — Convert a JSON diagram description to .drawio XML.

The LLM decides WHAT goes in the diagram (nodes, edges, labels, types).
This script decides WHERE everything goes (coordinates, spacing, styles).

All styles, dimensions, colours, and spacing are loaded from config.json
(single source of truth — edit config.json, not this script).

Usage:
    python generate_drawio.py <input.json> --output <output.drawio>
    echo '<json>' | python generate_drawio.py --output <output.drawio>

JSON schema:
{
  "title": "Diagram Title",
  "subtitle": "Optional subtitle text",
  "layout": "linear" | "horizontal" | "branching" | "hierarchical" | "swimlane" | "grid" | "rows" | "flow" | "pipeline",
  "nodes": [
    {
      "id": "unique-id",
      "label": "Display Name",
      "type": "start" | "end" | "process" | "decision" | "note" | "icon" |
              "dark_panel" | "success" | "data_store" | "actor" | "cylinder" | "cloud",
      "detail": "optional subtitle text",
      "icon": "file:///absolute/path/to/icon.png",
      "variant": "primary" | "secondary" | "accent" | "warning" | "danger" | "neutral",
      "lane": "lane-id (swimlane layout only)",
      "row": "1 (rows layout only — nodes sharing a row value appear side-by-side)"
    }
  ],
  "edges": [
    {
      "from": "source-id",
      "to": "target-id",
      "label": "optional",
      "style": "solid" | "curved" | "dashed" | "dotted" | "bidirectional",
      "color": "green" | "orange" | "blue" | "red" | "purple" | "grey"
    }
  ],
  "groups": [
    {
      "id": "group-id",
      "label": "Section Label",
      "members": ["node-id-1", "node-id-2"],
      "color": "#hex"
    }
  ],
  "lanes": [
    {
      "id": "lane-id",
      "label": "Lane Label",
      "color": "#hex (optional)"
    }
  ],
  "grid_columns": 3,
  "flow_columns": 3,
  "pipeline": ["node-id-1", ["node-id-2", "node-id-3"], "node-id-4"]
}

pipeline layout:
  Top-level "pipeline" array. Each entry is a node ID (single step) or list of node IDs
  (vertical stack at that step). Flow runs left-to-right; stacks grow top-to-bottom.
  Example: ["n1", ["n2", "n3", "n4", "n5"], "n6"]
  →  n1 alone → n2/n3/n4/n5 stacked → n6 alone  (horizontal flow, step 2 is a column)
"""
import argparse
import json
import math
import re
import sys
import uuid
from collections import defaultdict
from pathlib import Path
from xml.sax.saxutils import escape

# ── Load config ────────────────────────────────────────────────────────────────

CONFIG_PATH = Path(__file__).parent / "config.json"


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        print(f"Error: config.json not found at {CONFIG_PATH}", file=sys.stderr)
        sys.exit(1)
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


CFG = load_config()

# Unpack config into module-level vars for convenience
PAGE_WIDTH = CFG["page"]["width"]
CONTENT_LEFT = CFG["page"]["content_left"]
CONTENT_RIGHT = CFG["page"]["content_right"]
CONTENT_WIDTH = CONTENT_RIGHT - CONTENT_LEFT

V_GAP = CFG["spacing"]["v_gap"]
H_GAP = CFG["spacing"]["h_gap"]
GROUP_PAD = CFG["spacing"]["group_padding"]
MIN_EDGE_GAP = CFG["spacing"]["min_edge_gap"]
TITLE_BOTTOM_MARGIN = CFG["spacing"]["title_bottom_margin"]

DIMS = {k: tuple(v) for k, v in CFG["dimensions"].items() if isinstance(v, list)}
DETAIL_EXTRA_H = CFG["dimensions"]["detail_extra_height"]

EDGE_COLORS = CFG["colors"]["edges"]
DETAIL_TEXT_COLOR = CFG["colors"].get("detail_text", "#64748B")
STYLES = CFG["styles"]


# ── Style helpers ──────────────────────────────────────────────────────────────

def get_icon_style(icon_path: str) -> str:
    base = STYLES.get(
        "icon_base",
        "shape=image;verticalLabelPosition=bottom;labelBackgroundColor=default;"
        "verticalAlign=top;aspect=fixed;imageAspect=0;html=1;"
        "fontSize=11;fontColor=#1E293B;fontFamily=Helvetica;",
    )
    return f"{base}image={icon_path};"


def get_node_style(node: dict) -> str:
    ntype = node.get("type", "process")
    if ntype == "icon":
        return get_icon_style(node.get("icon", ""))
    if ntype in ("start", "end", "decision", "note", "dark_panel", "success",
                 "data_store", "actor", "junction", "cylinder", "cloud"):
        return STYLES[ntype]
    variant = node.get("variant", "primary")
    return STYLES.get(f"process_{variant}", STYLES["process_primary"])


def get_edge_style(edge: dict) -> str:
    style = edge.get("style", "solid")
    color = edge.get("color")
    style_key = {
        "solid": "edge_solid",
        "curved": "edge_curved",
        "dashed": "edge_dashed",
        "dotted": "edge_dotted",
        "bidirectional": "edge_bidirectional",
    }.get(style, "edge_solid")
    base = STYLES[style_key]
    if color and color in EDGE_COLORS:
        # Override strokeColor — remove existing one first, then append
        base = re.sub(r"strokeColor=#[0-9A-Fa-f]+;", "", base)
        base += f"strokeColor={EDGE_COLORS[color]};"
    return base


def get_dims(node: dict) -> tuple[int, int]:
    ntype = node.get("type", "process")
    w, h = DIMS.get(ntype, (260, 56))
    if node.get("detail"):
        h += DETAIL_EXTRA_H
    return w, h


# ── Title area ─────────────────────────────────────────────────────────────────

def get_title_height(data: dict) -> int:
    """Return total height of title area (title + optional subtitle + margin)."""
    h = 0
    if data.get("title"):
        h += 50  # title text height
    if data.get("subtitle"):
        h += 24  # subtitle text height
    if h > 0:
        h += TITLE_BOTTOM_MARGIN
    return h


def get_content_top(data: dict) -> int:
    """Return the Y coordinate where diagram content starts (below title area)."""
    title_h = get_title_height(data)
    return max(20 + title_h, 100)  # at least y=100


# ── Layout engines ─────────────────────────────────────────────────────────────

def layout_linear(nodes: list[dict], edges: list[dict], data: dict = None) -> dict[str, tuple[int, int]]:
    """Place nodes in a straight vertical line, centred on the canvas."""
    data = data or {}
    positions = {}
    y = get_content_top(data)
    for node in nodes:
        w, h = get_dims(node)
        x = (PAGE_WIDTH - w) // 2
        positions[node["id"]] = (x, y)
        # Consistent edge-to-edge gap between nodes
        y += h + MIN_EDGE_GAP
    return positions


def layout_horizontal(nodes: list[dict], edges: list[dict], data: dict = None) -> dict[str, tuple[int, int]]:
    """Place nodes in a horizontal row, left to right, vertically centred."""
    data = data or {}
    positions = {}
    content_top = get_content_top(data)

    # Calculate total width to centre the row
    total_w = sum(get_dims(n)[0] for n in nodes) + H_GAP * max(len(nodes) - 1, 0)
    start_x = max(CONTENT_LEFT, (PAGE_WIDTH - total_w) // 2)

    # Find tallest node for vertical centering
    max_h = max((get_dims(n)[1] for n in nodes), default=60)

    x = start_x
    for node in nodes:
        w, h = get_dims(node)
        y = content_top + (max_h - h) // 2  # vertically centre on tallest node
        positions[node["id"]] = (x, y)
        x += w + H_GAP
    return positions


def layout_branching(nodes: list[dict], edges: list[dict], data: dict = None) -> dict[str, tuple[int, int]]:
    """Detect fork/join points and lay out branches side by side."""
    data = data or {}
    content_top = get_content_top(data)

    children_of = defaultdict(list)
    parents_of = defaultdict(list)
    for e in edges:
        children_of[e["from"]].append(e["to"])
        parents_of[e["to"]].append(e["from"])

    node_map = {n["id"]: n for n in nodes}
    all_ids = [n["id"] for n in nodes]

    roots = [nid for nid in all_ids if nid not in parents_of]
    if not roots:
        roots = [all_ids[0]]

    # Phase 1: BFS to assign initial levels (ignore back-edges for cycles)
    levels = {}
    visit_order = {}
    order_counter = 0
    queue = [(r, 0) for r in roots]
    while queue:
        nid, lvl = queue.pop(0)
        if nid in visit_order:
            continue
        visit_order[nid] = order_counter
        order_counter += 1
        levels[nid] = lvl
        for child in children_of[nid]:
            queue.append((child, lvl + 1))

    for n in nodes:
        if n["id"] not in levels:
            levels[n["id"]] = 0
            visit_order[n["id"]] = order_counter
            order_counter += 1

    # Phase 2: push levels down for forward/cross edges (skip back-edges)
    changed = True
    while changed:
        changed = False
        for e in edges:
            s, t = e["from"], e["to"]
            if s not in visit_order or t not in visit_order:
                continue
            # Back edge: target was visited before source in BFS (cycle)
            if visit_order[t] < visit_order[s]:
                continue
            if levels[t] <= levels[s]:
                levels[t] = levels[s] + 1
                changed = True

    by_level = defaultdict(list)
    for nid, lvl in levels.items():
        by_level[lvl].append(nid)

    id_order = {nid: i for i, nid in enumerate(all_ids)}
    for lvl in by_level:
        by_level[lvl].sort(key=lambda nid: id_order.get(nid, 0))

    positions = {}
    max_level = max(by_level.keys()) if by_level else 0

    # Calculate per-level Y based on actual node heights (not fixed V_GAP)
    level_y = {}
    y = content_top
    for lvl in range(max_level + 1):
        level_nodes = by_level.get(lvl, [])
        level_y[lvl] = y
        if level_nodes:
            max_h = max(get_dims(node_map[nid])[1] for nid in level_nodes)
            y += max_h + MIN_EDGE_GAP
        else:
            y += V_GAP

    for lvl in range(max_level + 1):
        level_nodes = by_level.get(lvl, [])
        if not level_nodes:
            continue

        total_w = sum(get_dims(node_map[nid])[0] for nid in level_nodes)
        total_gaps = H_GAP * (len(level_nodes) - 1) if len(level_nodes) > 1 else 0
        total_span = total_w + total_gaps

        start_x = (PAGE_WIDTH - total_span) // 2
        x = start_x

        for nid in level_nodes:
            w, _ = get_dims(node_map[nid])
            positions[nid] = (x, level_y[lvl])
            x += w + H_GAP

    return positions


def layout_hierarchical(nodes: list[dict], edges: list[dict], data: dict = None) -> dict[str, tuple[int, int]]:
    """Tree layout — uses branching engine with same logic."""
    return layout_branching(nodes, edges, data)


def layout_grid(nodes: list[dict], edges: list[dict], data: dict = None) -> dict[str, tuple[int, int]]:
    """Arrange nodes in a grid with configurable column count."""
    data = data or {}
    columns = data.get("grid_columns", 3)
    content_top = get_content_top(data)
    positions = {}

    # Calculate max height per row for even spacing
    rows = []
    for i in range(0, len(nodes), columns):
        row_nodes = nodes[i:i + columns]
        rows.append(row_nodes)

    col_width = CONTENT_WIDTH // columns
    y = content_top

    for row_nodes in rows:
        max_h = max((get_dims(n)[1] for n in row_nodes), default=56)
        for col, node in enumerate(row_nodes):
            w, h = get_dims(node)
            x = CONTENT_LEFT + col * col_width + (col_width - w) // 2
            node_y = y + (max_h - h) // 2  # vertically centre within row
            positions[node["id"]] = (x, node_y)
        y += max_h + MIN_EDGE_GAP

    return positions


def layout_swimlane(nodes: list[dict], edges: list[dict], data: dict = None) -> dict[str, tuple[int, int]]:
    """Place nodes into horizontal swimlanes. Nodes flow left-to-right within their lane."""
    data = data or {}
    lanes = data.get("lanes", [])
    if not lanes:
        # Fallback: auto-detect lanes from node "lane" fields
        lane_ids = []
        seen = set()
        for n in nodes:
            lid = n.get("lane", "default")
            if lid not in seen:
                lane_ids.append(lid)
                seen.add(lid)
        lanes = [{"id": lid, "label": lid} for lid in lane_ids]

    lane_order = {lane["id"]: i for i, lane in enumerate(lanes)}

    # Group nodes by lane
    by_lane = defaultdict(list)
    for n in nodes:
        lid = n.get("lane", lanes[0]["id"] if lanes else "default")
        by_lane[lid].append(n)

    # Calculate lane heights based on content
    lane_header = CFG["spacing"].get("swimlane_header", 44)
    lane_pad = CFG["spacing"].get("swimlane_padding", 32)

    # Calculate per-lane height based on tallest node in that lane
    lane_heights = {}
    for lane in lanes:
        lid = lane["id"]
        lane_nodes = by_lane.get(lid, [])
        if lane_nodes:
            max_h = max(get_dims(n)[1] for n in lane_nodes)
        else:
            max_h = 56
        lane_heights[lid] = lane_header + max_h + 2 * lane_pad

    content_top = get_content_top(data)

    # Compute cumulative Y offsets per lane
    lane_y = {}
    y = content_top
    for lane in lanes:
        lid = lane["id"]
        lane_y[lid] = y
        y += lane_heights[lid]

    positions = {}
    for n in nodes:
        lid = n.get("lane", lanes[0]["id"] if lanes else "default")
        lane_idx_y = lane_y.get(lid, content_top)
        lane_nodes = by_lane[lid]
        node_idx = lane_nodes.index(n)
        w, h = get_dims(n)
        x = CONTENT_LEFT + 140 + node_idx * (w + H_GAP)
        node_y = lane_idx_y + lane_header + lane_pad + (lane_heights.get(lid, 100) - lane_header - 2 * lane_pad - h) // 2
        positions[n["id"]] = (x, node_y)

    return positions


def layout_rows(nodes: list[dict], edges: list[dict], data: dict = None) -> dict[str, tuple[int, int]]:
    """Place nodes into explicit rows defined by each node's 'row' field.

    Nodes sharing the same 'row' value appear side-by-side (left-to-right),
    centred on the canvas. Row groups stack top-to-bottom. The LLM controls
    grouping semantically — parallel steps share a row, sequential steps use
    different rows. Nodes without a 'row' field each occupy their own row.
    """
    data = data or {}
    content_top = get_content_top(data)

    # Group nodes by row, preserving first-occurrence order
    row_order = []
    by_row = defaultdict(list)
    seen_rows = set()

    for i, node in enumerate(nodes):
        row_key = node.get("row", f"_auto_{i}")
        if row_key not in seen_rows:
            row_order.append(row_key)
            seen_rows.add(row_key)
        by_row[row_key].append(node)

    positions = {}
    y = content_top

    for row_key in row_order:
        row_nodes = by_row[row_key]
        max_h = max((get_dims(n)[1] for n in row_nodes), default=56)

        total_w = sum(get_dims(n)[0] for n in row_nodes) + H_GAP * (len(row_nodes) - 1)
        start_x = max(CONTENT_LEFT, (PAGE_WIDTH - total_w) // 2)

        x = start_x
        for node in row_nodes:
            w, h = get_dims(node)
            node_y = y + (max_h - h) // 2  # vertically centre within row
            positions[node["id"]] = (x, node_y)
            x += w + H_GAP

        y += max_h + MIN_EDGE_GAP

    return positions


def layout_flow(nodes: list[dict], edges: list[dict], data: dict = None) -> dict[str, tuple[int, int]]:
    """Wrap nodes into rows (left-to-right, then down). Screen-friendly for long sequences.

    Targets ~16:9 aspect ratio by default. Override with 'flow_columns' in the JSON.
    """
    data = data or {}
    content_top = get_content_top(data)

    n = len(nodes)
    cols = data.get("flow_columns")
    if not cols:
        # Auto-calculate: target ~16:9 (cols ≈ sqrt(n * 16/9))
        cols = max(2, min(n, round(math.sqrt(n * 16 / 9))))

    positions = {}
    y = content_top

    for row_start in range(0, n, cols):
        row_nodes = nodes[row_start:row_start + cols]
        max_h = max((get_dims(nd)[1] for nd in row_nodes), default=56)

        total_w = sum(get_dims(nd)[0] for nd in row_nodes) + H_GAP * (len(row_nodes) - 1)
        start_x = max(CONTENT_LEFT, (PAGE_WIDTH - total_w) // 2)

        x = start_x
        for node in row_nodes:
            w, h = get_dims(node)
            node_y = y + (max_h - h) // 2  # vertically centre within row
            positions[node["id"]] = (x, node_y)
            x += w + H_GAP

        y += max_h + MIN_EDGE_GAP

    return positions


def layout_pipeline(nodes: list[dict], edges: list[dict], data: dict = None) -> dict[str, tuple[int, int]]:
    """Horizontal left-to-right flow where each step can be a single node or a vertical stack.

    Requires a top-level 'pipeline' array in the JSON. Each entry is either:
      - a node ID string  → single node at that step
      - a list of node IDs → vertical stack of nodes at that step (column)

    All steps are horizontally spaced and the tallest stack determines the vertical
    midpoint; shorter single nodes are centred on that midpoint.

    Example:
      "pipeline": ["n1", ["n2", "n3", "n4", "n5"], "n6"]
      →  n1 alone | n2/n3/n4/n5 stacked | n6 alone
    """
    data = data or {}
    pipeline_spec = data.get("pipeline", [])
    if not pipeline_spec:
        # Fallback: treat all nodes as individual pipeline steps
        pipeline_spec = [n["id"] for n in nodes]

    content_top = get_content_top(data)
    node_map = {n["id"]: n for n in nodes}

    # Normalise: each step becomes a list of node IDs
    steps = []
    for entry in pipeline_spec:
        if isinstance(entry, list):
            steps.append(entry)
        else:
            steps.append([entry])

    # Compute each step's bounding box: (w, h)
    # w = max node width in the step; h = sum of heights + gaps between nodes
    step_dims = []
    for step_ids in steps:
        step_nodes = [node_map[nid] for nid in step_ids if nid in node_map]
        if not step_nodes:
            step_dims.append((0, 0))
            continue
        sw = max(get_dims(n)[0] for n in step_nodes)
        sh = sum(get_dims(n)[1] for n in step_nodes) + V_GAP * max(len(step_nodes) - 1, 0)
        step_dims.append((sw, sh))

    # Max total height determines the vertical midpoint for centering single nodes
    max_total_h = max((h for _, h in step_dims), default=56)
    mid_y = content_top + max_total_h // 2

    # Centre the entire pipeline horizontally
    total_pipeline_w = sum(sw for sw, _ in step_dims) + H_GAP * max(len(steps) - 1, 0)
    start_x = max(CONTENT_LEFT, (PAGE_WIDTH - total_pipeline_w) // 2)

    positions = {}
    x = start_x

    for step_ids, (sw, sh) in zip(steps, step_dims):
        step_nodes = [node_map[nid] for nid in step_ids if nid in node_map]
        if not step_nodes:
            x += sw + H_GAP
            continue

        # Vertically centre the stack around mid_y
        stack_start_y = mid_y - sh // 2
        sy = stack_start_y
        for node in step_nodes:
            nw, nh = get_dims(node)
            # Horizontally centre narrower nodes within the step width
            nx = x + (sw - nw) // 2
            positions[node["id"]] = (nx, sy)
            sy += nh + V_GAP

        x += sw + H_GAP

    return positions


LAYOUTS = {
    "linear": layout_linear,
    "horizontal": layout_horizontal,
    "branching": layout_branching,
    "hierarchical": layout_hierarchical,
    "grid": layout_grid,
    "swimlane": layout_swimlane,
    "flow": layout_flow,
    "rows": layout_rows,
    "pipeline": layout_pipeline,
}


# ── XML generation ─────────────────────────────────────────────────────────────

def build_label(node: dict, detail_color: str = None) -> str:
    label = escape(node.get("label", ""))
    detail = node.get("detail")
    if detail:
        color = detail_color or DETAIL_TEXT_COLOR
        label += f"&lt;br&gt;&lt;font style=&apos;font-size:10px;color:{color}&apos;&gt;{escape(detail)}&lt;/font&gt;"
    return label


def generate_swimlane_xml(data: dict, positions: dict, lines: list) -> None:
    """Append swimlane container elements to the XML lines."""
    lanes = data.get("lanes", [])
    if not lanes:
        return

    nodes = data.get("nodes", [])
    node_map = {n["id"]: n for n in nodes}
    lane_header = CFG["spacing"].get("swimlane_header", 44)
    lane_pad = CFG["spacing"].get("swimlane_padding", 32)
    content_top = get_content_top(data)

    # Group nodes by lane to compute per-lane heights
    by_lane = defaultdict(list)
    for n in nodes:
        lid = n.get("lane", lanes[0]["id"] if lanes else "default")
        by_lane[lid].append(n)

    lane_heights = {}
    for lane in lanes:
        lid = lane["id"]
        lane_nodes = by_lane.get(lid, [])
        if lane_nodes:
            max_h = max(get_dims(n)[1] for n in lane_nodes)
        else:
            max_h = 56
        lane_heights[lid] = lane_header + max_h + 2 * lane_pad

    # Find total width needed
    max_x = CONTENT_LEFT + 140  # minimum
    for nid, (x, y) in positions.items():
        w, _ = get_dims(node_map.get(nid, {}))
        max_x = max(max_x, x + w + lane_pad)
    lane_w = max_x - CONTENT_LEFT + lane_pad

    y = content_top
    for lane in lanes:
        lid = lane["id"]
        llabel = escape(lane.get("label", lid))
        lcolor = lane.get("color", "")
        lane_h = lane_heights.get(lid, 100)

        style = STYLES.get("swimlane", "")
        if lcolor:
            style += f"strokeColor={lcolor};"

        lines.append(
            f'<mxCell id="lane_{lid}" value="{llabel}" '
            f'style="{style}" vertex="1" parent="1">'
            f'<mxGeometry x="{CONTENT_LEFT}" y="{y}" width="{lane_w}" height="{lane_h}" as="geometry"/>'
            f'</mxCell>'
        )
        y += lane_h


def generate_xml(data: dict) -> str:
    global STYLES, EDGE_COLORS, DETAIL_TEXT_COLOR

    # Theme support — swap styles for dark mode
    theme = data.get("theme", "light")
    bg_color = None
    detail_color = DETAIL_TEXT_COLOR

    if theme == "dark" and "dark" in CFG:
        dark = CFG["dark"]
        STYLES = dark.get("styles", STYLES)
        bg_color = dark.get("background", "#0F172A")
        dark_colors = dark.get("colors", {})
        if "edges" in dark_colors:
            EDGE_COLORS = dark_colors["edges"]
        detail_color = dark_colors.get("detail_text", "#94A3B8")

    title = data.get("title", "Diagram")
    subtitle = data.get("subtitle", "")
    layout_name = data.get("layout", "linear")
    nodes = data.get("nodes", [])
    edges = data.get("edges", [])
    groups = data.get("groups", [])

    layout_fn = LAYOUTS.get(layout_name, layout_linear)
    positions = layout_fn(nodes, edges, data)

    diagram_id = str(uuid.uuid4())[:8]

    node_map = {n["id"]: n for n in nodes}

    # Build icon label background map: icon nodes use group fill if inside a group,
    # otherwise use the page background. This prevents a mismatched coloured square
    # appearing behind icon labels when group fill ≠ page background.
    _group_style = STYLES.get("group", "")
    _group_fill_m = re.search(r"fillColor=(#[0-9A-Fa-f]{6})", _group_style)
    _group_fill = _group_fill_m.group(1) if _group_fill_m else ("#1E293B" if theme == "dark" else "#F8FAFC")
    _page_bg = bg_color or "#FFFFFF"
    node_group_fill = {}
    for _grp in groups:
        for _mid in _grp.get("members", []):
            node_group_fill[_mid] = _group_fill

    max_y = 0
    max_x = 0
    for nid, (x, y) in positions.items():
        w, h = get_dims(node_map.get(nid, {}))
        max_y = max(max_y, y + h)
        max_x = max(max_x, x + w)
    page_height = max(800, max_y + 200)
    page_width = max(PAGE_WIDTH, max_x + 200)

    bg_attr = f' background="{bg_color}"' if bg_color else ""

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<!-- \U0001f414 matcluck\'s drawio-skill | github.com/matcluck -->',
        '<mxfile host="app.diagrams.net" agent="matcluck/drawio-skill">',
        f'<diagram name="Page-1" id="{diagram_id}">',
        f'<mxGraphModel dx="800" dy="400" grid="1" gridSize="10" guides="1" tooltips="1"',
        f'  connect="1" arrows="1" fold="1" page="1" pageScale="1"',
        f'  pageWidth="{page_width}" pageHeight="{page_height}" math="0" shadow="0"{bg_attr}>',
        '<root>',
        '<mxCell id="0" />',
        '<mxCell id="1" parent="0" />',
    ]

    # Title
    title_y = 20
    if title:
        lines.append(
            f'<mxCell id="title" value="{escape(title)}" '
            f'style="{STYLES["title"]}" vertex="1" parent="1">'
            f'<mxGeometry x="{CONTENT_LEFT}" y="{title_y}" width="{CONTENT_WIDTH}" height="50" as="geometry"/>'
            f'</mxCell>'
        )
        title_y += 50

    # Subtitle
    if subtitle:
        lines.append(
            f'<mxCell id="subtitle" value="{escape(subtitle)}" '
            f'style="{STYLES["subtitle"]}" vertex="1" parent="1">'
            f'<mxGeometry x="{CONTENT_LEFT}" y="{title_y}" width="{CONTENT_WIDTH}" height="24" as="geometry"/>'
            f'</mxCell>'
        )

    # Swimlanes (before groups and nodes so they render behind)
    if layout_name == "swimlane":
        generate_swimlane_xml(data, positions, lines)

    # Groups (rendered before nodes so nodes appear on top)
    for group in groups:
        gid = group["id"]
        glabel = escape(group.get("label", ""))
        members = group.get("members", [])
        gcolor = group.get("color", "")

        if members:
            valid_members = [m for m in members if m in positions and m in node_map]
            if not valid_members:
                continue
            min_x = min(positions[m][0] for m in valid_members)
            min_y = min(positions[m][1] for m in valid_members)
            g_max_x = max(
                positions[m][0] + get_dims(node_map[m])[0]
                for m in valid_members
            )
            max_y_g = max(
                positions[m][1] + get_dims(node_map[m])[1]
                for m in valid_members
            )
        else:
            min_x, min_y, g_max_x, max_y_g = 100, 100, 400, 200

        gx = min_x - GROUP_PAD
        gy = min_y - GROUP_PAD - 24  # extra space for group label
        gw = (g_max_x - min_x) + 2 * GROUP_PAD
        gh = (max_y_g - min_y) + 2 * GROUP_PAD + 24

        style = STYLES["group"]
        if gcolor:
            style += f"strokeColor={gcolor};"
        lines.append(
            f'<mxCell id="{gid}" value="{glabel}" '
            f'style="{style}" vertex="1" parent="1">'
            f'<mxGeometry x="{gx}" y="{gy}" width="{gw}" height="{gh}" as="geometry"/>'
            f'</mxCell>'
        )

    # Nodes
    for node in nodes:
        nid = node["id"]
        style = get_node_style(node)
        # For icon nodes, set labelBackgroundColor to match the actual visual background
        # at that position (group fill or page bg) to avoid mismatched colour squares.
        if node.get("type") == "icon":
            lbg = node_group_fill.get(nid, _page_bg)
            style = re.sub(r"labelBackgroundColor=[^;]+;", f"labelBackgroundColor={lbg};", style)
        label = build_label(node, detail_color)
        w, h = get_dims(node)
        x, y = positions.get(nid, (100, 100))

        lines.append(
            f'<mxCell id="{nid}" value="{label}" '
            f'style="{style}" vertex="1" parent="1">'
            f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/>'
            f'</mxCell>'
        )

    # Edges
    for i, edge in enumerate(edges):
        eid = f"e{i}"
        style = get_edge_style(edge)
        src = edge["from"]
        tgt = edge["to"]
        label_attr = ""
        if edge.get("label"):
            label_attr = f' value="{escape(edge["label"])}"'

        lines.append(
            f'<mxCell id="{eid}"{label_attr} '
            f'style="{style}" edge="1" source="{src}" target="{tgt}" parent="1">'
            f'<mxGeometry relative="1" as="geometry"/>'
            f'</mxCell>'
        )

    lines.extend([
        '</root>',
        '</mxGraphModel>',
        '</diagram>',
        '</mxfile>',
    ])

    return "\n".join(lines)


# ── CLI ────────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate .drawio XML from a JSON diagram description."
    )
    parser.add_argument(
        "input", nargs="?", type=Path, default=None,
        help="Path to JSON file (reads stdin if omitted)"
    )
    parser.add_argument(
        "--output", type=Path, required=True,
        help="Output .drawio file path"
    )
    args = parser.parse_args()

    if args.input:
        if not args.input.exists():
            print(f"Error: file not found: {args.input}", file=sys.stderr)
            return 1
        raw = args.input.read_text(encoding="utf-8")
    else:
        raw = sys.stdin.read()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"Error: invalid JSON: {e}", file=sys.stderr)
        return 1

    if "nodes" not in data:
        print("Error: JSON must contain a 'nodes' array.", file=sys.stderr)
        return 1

    xml = generate_xml(data)

    output_path = args.output.resolve()
    output_path.write_text(xml, encoding="utf-8")
    print(f"Generated: {output_path} ({len(data['nodes'])} nodes, {len(data.get('edges', []))} edges)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
