# Style Reference

**Source of truth: [`scripts/config.json`](../scripts/config.json)**

All styles, colours, dimensions, and spacing are defined in config.json. The `generate_drawio.py` script reads from it automatically. During Ralph Loop XML editing, read config.json directly to look up style strings.

## Quick reference

Run this to dump all available styles:
```bash
python3 -c "import json; c=json.load(open('$HOME/.claude/skills/drawio/scripts/config.json')); [print(f'{k}: {v}') for k,v in c['styles'].items()]"
```

## Colour Palette (Tailwind-inspired)

| Name | Fill | Stroke | Use |
|------|------|--------|-----|
| Blue | `#DBEAFE` | `#3B82F6` | Primary flow, default processes |
| Green | `#D1FAE5` | `#10B981` | Success, secondary steps |
| Orange | `#FEF3C7` | `#F59E0B` | Warnings, decisions, data stores |
| Purple | `#EDE9FE` | `#8B5CF6` | Accents, highlighted steps |
| Red | `#FFE4E6` | `#F43F5E` | Errors, danger, critical paths |
| Yellow | `#FEF9C3` | `#EAB308` | Notes, annotations |
| Grey | `#F1F5F9` | `#94A3B8` | Neutral, optional, clouds |
| Cyan | `#CFFAFE` | `#06B6D4` | Info, data flow |
| Slate 800 | — | `#1E293B` | Dark fills (start/end, dark panels) |

## Edge Colours

| Name | Hex | Use |
|------|-----|-----|
| Green | `#10B981` | Success paths, happy flow |
| Orange | `#F59E0B` | Conditional, warning paths |
| Blue | `#3B82F6` | Data flow, info transfer |
| Red | `#F43F5E` | Error paths, failures |
| Purple | `#8B5CF6` | Async, event-driven |
| Grey | `#94A3B8` | Default (no semantic colour) |

## Typography Hierarchy

| Element | Size | Weight | Colour | Font |
|---------|------|--------|--------|------|
| Title | 24px | Bold | `#1E293B` | Helvetica |
| Subtitle | 13px | Normal | `#94A3B8` | Helvetica |
| Node label | 13px | Normal | `#1E293B` | Helvetica |
| Node detail | 10px | Normal | `#64748B` | Helvetica |
| Edge label | 11px | Normal | `#64748B` | Helvetica |
| Note text | 11px | Normal | `#64748B` | Helvetica |
| Dark panel | 12px | Normal | `#E2E8F0` | Courier New |

## Node Dimensions

| Type | Width × Height | Notes |
|------|---------------|-------|
| start / end | 140 × 44 | Dark ellipse |
| process | 260 × 56 | Rounded rectangle (+24px with detail) |
| decision | 200 × 120 | Diamond |
| note | 240 × 80 | Sticky note shape |
| icon | 80 × 80 | Custom image |
| dark_panel | 260 × 56 | Code/terminal block |
| success | 260 × 56 | Green highlighted box |
| data_store | 260 × 50 | DFD data store |
| cylinder | 120 × 80 | Database cylinder |
| cloud | 200 × 100 | Cloud shape |
| actor | 60 × 80 | Person silhouette |

## Design Principles

- **No shadows** — clean, flat aesthetic. Shadow=0 on all elements.
- **1.5px strokes** — consistent border weight across all shapes and edges.
- **White label backgrounds** on edges (`labelBackgroundColor=#FFFFFF`) to prevent text-on-line overlap.
- **Rounded corners** (`arcSize=24`) on process boxes for a modern feel.
- **Muted detail text** uses `#64748B` (slate-500) for visual hierarchy without distraction.

## When editing raw XML

Every `mxCell` needs:
- `parent="1"`
- `vertex="1"` (nodes) or `edge="1"` (edges)
- Edges need `source` and `target` referencing valid node IDs

When adding styles manually, always copy from config.json to maintain consistency. Do not invent new colour values — use the palette above.
