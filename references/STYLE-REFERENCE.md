# Draw.io Element & Edge Style Reference

**All cells use `parent="1"` and `vertex="1"` (nodes) or `edge="1"` (edges).**

These are common element styles to use as a starting point. Choose and adapt the styles that fit your diagram type — not every diagram needs every element.

## Colour Palette

| Colour | Hex | Used for |
|--------|-----|----------|
| Dark teal | `#264653` | Start/end nodes, junction points, primary box stroke |
| White | `#FFFFFF` | Start/end node text |
| Light blue | `#D6E4F0` | Primary box fill |
| Medium blue | `#c9daf8` | Secondary box fill |
| Slate blue | `#3d5a80` | Secondary box stroke |
| Light red | `#f4cccc` | Accent box fill |
| Dark red | `#6a040f` | Accent box stroke |
| Light green | `#d5e8d4` | Success/output box fill |
| Green | `#82b366` | Success/output box stroke |
| Orange | `#FF6B35` | Decision diamond fill |
| Dark orange | `#CC5529` | Decision diamond stroke |
| Pale yellow | `#fff3cd` | Note fill |
| Yellow | `#ffc107` | Note stroke, warning edges |
| Charcoal | `#2d2d2d` | Dark panel fill |
| Grey | `#555555` | Dark panel stroke, secondary edges |
| Light grey | `#e0e0e0` | Dark panel text |
| Edge green | `#77AB94` | Coloured edge |
| Edge orange | `#FFCE9F` | Coloured edge |
| Edge blue | `#ADD8E6` | Coloured edge |
| Edge red | `#dc3545` | Coloured edge |

## Element Styles

### Title
```
style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontSize=36;fontStyle=1"
```
- y="20", width="1400", height="50", centred on canvas

### Start / End Nodes (ellipses)
```
style="shape=ellipse;whiteSpace=wrap;html=1;fillColor=#264653;strokeColor=#264653;fontSize=12;fontColor=#FFFFFF;fontStyle=1;"
```
- START: ~180×80. END: ~170×70

### Rounded Boxes (general-purpose containers)

**Primary (light blue)**
```
style="rounded=1;whiteSpace=wrap;html=1;fillColor=#D6E4F0;strokeColor=#264653;fontSize=11;verticalAlign=top;spacingTop=5;spacingLeft=8;"
```

**Secondary (medium blue)**
```
style="rounded=1;whiteSpace=wrap;html=1;fillColor=#c9daf8;strokeColor=#3d5a80;fontSize=11;verticalAlign=top;spacingTop=5;spacingLeft=8;"
```

**Accent (light red)**
```
style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f4cccc;strokeColor=#6a040f;fontSize=11;verticalAlign=middle;align=center;"
```

**Success / output (green)**
```
style="rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;fontSize=10;fontStyle=1"
```

### Decision Diamonds
```
style="shape=rhombus;whiteSpace=wrap;html=1;fillColor=#FF6B35;strokeColor=#CC5529;fontSize=9;"
```

### Notes (yellow sticky)
```
style="shape=note;whiteSpace=wrap;html=1;backgroundOutline=1;size=15;fillColor=#fff3cd;strokeColor=#ffc107;fontSize=10;verticalAlign=middle;"
```

### Dark Panel
```
style="rounded=1;whiteSpace=wrap;html=1;fillColor=#2d2d2d;strokeColor=#555555;fontSize=9;verticalAlign=top;spacingTop=5;spacingLeft=8;"
```
- Font colour #e0e0e0

### Small Junction Points (ellipses)
```
style="shape=ellipse;whiteSpace=wrap;html=1;fillColor=#264653;strokeColor=#264653;"
```
- 20×20 — use where edges split or merge

## Edge Styles

### Standard flow
```
style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeWidth=2;"
```

### Coloured edges
```
style="edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;strokeWidth=2;curved=0;strokeColor=#77AB94;"
```
Colour options:
- Green: `strokeColor=#77AB94`
- Orange: `strokeColor=#FFCE9F`
- Blue: `strokeColor=#ADD8E6`
- Red: `strokeColor=#dc3545`

### Dashed edges
```
style="dashed=1;strokeColor=#ffc107;strokeWidth=1;"   (warning/attention)
style="dashed=1;strokeColor=#555555;strokeWidth=1;"   (secondary/info)
```

## Text Labels
```
style="text;html=1;align=center;verticalAlign=middle;strokeColor=none;fillColor=none;fontSize=14;fontStyle=1;"
```
