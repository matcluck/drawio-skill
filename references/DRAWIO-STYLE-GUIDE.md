# Draw.io Style Attribute Reference

> **Sources:** draw.io documentation (drawio.com), mxGraph JavaScript Client Manual
> (jgraph.github.io/mxgraph), diagrams.net file format specification

This reference covers style attributes beyond what is defined in `config.json`. Use this when
editing raw XML during Ralph Loop refinement or when adding elements not covered by the
standard node/edge types.

---

## XML Structure

```xml
<mxfile>
  <diagram name="Page-1">
    <mxGraphModel dx="1422" dy="762" grid="0" gridSize="10"
                  pageWidth="1169" pageHeight="827" background="#ffffff">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>

        <!-- Vertex (node) -->
        <mxCell id="2" value="Label" style="rounded=1;arcSize=24;fillColor=#DBEAFE;strokeColor=#3B82F6;"
                vertex="1" parent="1">
          <mxGeometry x="100" y="100" width="260" height="56" as="geometry"/>
        </mxCell>

        <!-- Edge (connector) -->
        <mxCell id="3" value="label" style="edgeStyle=orthogonalEdgeStyle;rounded=1;"
                edge="1" source="2" target="4" parent="1">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

**Rules:**
- Every `mxCell` needs `parent="1"` (or parent container ID)
- Nodes: `vertex="1"`, edges: `edge="1"`
- Edges need `source` and `target` referencing valid cell IDs
- Style is a semicolon-separated string of `key=value` pairs — no spaces around `=`

---

## Shape Attributes

### Shape Type

`shape=<name>` — overrides the default rectangle. Omit for standard rounded rect.

**Built-in shapes:**

| style value | Appearance |
|---|---|
| *(omit shape=)* | Rectangle |
| `ellipse` | Circle / oval |
| `rhombus` | Diamond |
| `hexagon` | Hexagon |
| `triangle` | Triangle |
| `parallelogram` | Parallelogram |
| `cylinder3` | 3D cylinder (database alt) |
| `cloud` | Cloud blob |
| `actor` | Stick figure / person |
| `image` | Custom image (requires `image=file:///...`) |
| `swimlane` | Swimlane container with header |

**Flowchart stencil shapes** (`shape=mxgraph.flowchart.<name>`):

| name | Appearance |
|---|---|
| `start_2` | Rounded terminator (start/end) |
| `process` | Rectangle |
| `decision` | Diamond |
| `data` | Parallelogram |
| `stored_data` | DFD data store |
| `database` | Cylinder |
| `document` | Document shape |
| `terminator` | Rounded rectangle |
| `delay` | Delay shape |
| `manual_input` | Manual input |
| `annotation_2` | Annotation bracket |

### Shape Styling

| Attribute | Values | Default | Notes |
|---|---|---|---|
| `rounded` | `0`, `1` | `0` | Rounded corners on rectangle |
| `arcSize` | `0`–`100` | `4` | Corner radius as % of min dimension. 24 = modern look |
| `shadow` | `0`, `1` | `0` | Drop shadow |
| `glass` | `0`, `1` | `0` | Glass overlay effect |
| `sketch` | `0`, `1` | `0` | Hand-drawn appearance |
| `aspect` | `fixed` | — | Lock aspect ratio (use with `image` shapes) |
| `imageAspect` | `0`, `1` | `1` | Preserve image aspect ratio |
| `rotation` | `-360`–`360` | `0` | Rotation in degrees |

---

## Color Attributes

| Attribute | Values | Notes |
|---|---|---|
| `fillColor` | `#RRGGBB`, `none` | Shape fill. `none` = transparent |
| `strokeColor` | `#RRGGBB`, `none` | Border color. `none` = no border |
| `fontColor` | `#RRGGBB` | Text color |
| `gradientColor` | `#RRGGBB`, `none` | Gradient end color (top→bottom by default) |
| `gradientDirection` | `south`, `north`, `east`, `west` | Direction of gradient |
| `labelBackgroundColor` | `#RRGGBB`, `none`, `default` | Background behind label text |
| `labelBorderColor` | `#RRGGBB`, `none` | Border around label background |

---

## Opacity & Transparency

| Attribute | Values | Notes |
|---|---|---|
| `opacity` | `0`–`100` | Overall opacity. 100 = fully opaque |
| `fillOpacity` | `0`–`100` | Fill only |
| `strokeOpacity` | `0`–`100` | Stroke only |

---

## Stroke Attributes

| Attribute | Values | Default | Notes |
|---|---|---|---|
| `strokeWidth` | number | `1` | Line width in pixels |
| `dashed` | `0`, `1` | `0` | Dashed border/line |
| `dashPattern` | `"8 8"`, `"4 4"`, etc. | — | On/off lengths for dashes |
| `fixDash` | `0`, `1` | `0` | Prevent dash scaling with zoom |
| `perimeterSpacing` | number | `0` | Gap between shape border and edge endpoint |

---

## Font & Label Attributes

| Attribute | Values | Default | Notes |
|---|---|---|---|
| `fontFamily` | font name | `Helvetica` | Typeface |
| `fontSize` | number (px) | `11` | Label font size |
| `fontStyle` | bitmask | `0` | 1=bold, 2=italic, 4=underline, 8=strikethrough. Add values to combine (3=bold+italic) |
| `fontColor` | `#RRGGBB` | `#000000` | Label text color |
| `align` | `left`, `center`, `right` | `center` | Horizontal text alignment |
| `verticalAlign` | `top`, `middle`, `bottom` | `middle` | Vertical text alignment within label bounds |
| `verticalLabelPosition` | `top`, `middle`, `bottom` | `middle` | Where label sits relative to shape (use `bottom` for icon nodes) |
| `labelPosition` | `left`, `center`, `right` | `center` | Horizontal position of label block relative to shape |
| `spacingTop` | number | `0` | Padding above text |
| `spacingBottom` | number | `0` | Padding below text |
| `spacingLeft` | number | `0` | Padding left of text |
| `spacingRight` | number | `0` | Padding right of text |
| `spacing` | number | `2` | General padding (all sides) |
| `whiteSpace` | `wrap`, `nowrap` | `nowrap` | Text line wrapping |
| `overflow` | `visible`, `hidden`, `fill`, `width` | `visible` | Text overflow behaviour |
| `html` | `0`, `1` | `0` | Enable HTML tags in label (bold, br, etc.) |
| `horizontal` | `0`, `1` | `1` | `0` = vertical (rotated) text |
| `autosize` | `0`, `1` | `0` | Auto-resize cell to fit text |

---

## Edge Attributes

### Routing Style

| `edgeStyle` value | Appearance |
|---|---|
| `none` | Direct straight line (default) |
| `orthogonalEdgeStyle` | Right-angle routing (preferred for clean diagrams) |
| `elbowEdgeStyle` | Single elbow bend |
| `entityRelationEdgeStyle` | ER notation routing |
| `isometricEdgeStyle` | Isometric 3D routing |
| `loopEdgeStyle` | Self-loop |
| `sideToSideEdgeStyle` | Horizontal S-curve |
| `topToBottomEdgeStyle` | Vertical S-curve |

### Edge Shape Modifiers

| Attribute | Values | Notes |
|---|---|---|
| `curved` | `0`, `1` | Curved line (when `edgeStyle=none`) |
| `rounded` | `0`, `1` | Rounded corners on orthogonal edges |
| `elbow` | `vertical`, `horizontal` | Elbow direction (for `elbowEdgeStyle`) |
| `orthogonalLoop` | `0`, `1` | Use orthogonal routing for loops |

### Connection Points (Exit/Entry)

Specify exact connection point on source/target (values 0.0–1.0, relative to shape bounds):

```
exitX=0.5;exitY=1.0;exitDx=0;exitDy=0;
entryX=0.5;entryY=0.0;entryDx=0;entryDy=0;
```

| Value | Position |
|---|---|
| `X=0, Y=0.5` | Left middle |
| `X=1, Y=0.5` | Right middle |
| `X=0.5, Y=0` | Top centre |
| `X=0.5, Y=1` | Bottom centre |

### Arrowheads

| Attribute | Notes |
|---|---|
| `startArrow=<type>` | Arrowhead at source end |
| `endArrow=<type>` | Arrowhead at target end |
| `startFill=0\|1` | Filled vs open arrowhead at source |
| `endFill=0\|1` | Filled vs open arrowhead at target |
| `startSize=8` | Arrowhead size at source |
| `endSize=8` | Arrowhead size at target |

**Arrow type values:** `classic`, `block`, `open`, `oval`, `diamond`, `none`,
`ERone`, `ERmany`, `ERmandOne`, `ERzeroToOne`, `ERoneToMany`, `ERzeroToMany`

### Edge Spacing

| Attribute | Notes |
|---|---|
| `sourcePerimeterSpacing=0` | Gap between source shape and edge start |
| `targetPerimeterSpacing=0` | Gap between edge end and target shape |
| `jettySize=auto` | Connection notch size |

---

## Container & Swimlane Attributes

### Generic Container

```
style="container=1;collapsible=0;expand=1;fillColor=#f5f5f5;strokeColor=#666666;"
```

| Attribute | Notes |
|---|---|
| `container=1` | Marks cell as a container for child cells |
| `collapsible=0` | Disable the collapse/expand button |
| `expand=1` | Start in expanded state |
| `childLayout=stackLayout` | Auto-stack children vertically |

### Swimlane Container

```
style="shape=swimlane;startSize=44;horizontal=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontStyle=1;"
```

| Attribute | Notes |
|---|---|
| `shape=swimlane` | Renders as swimlane with header |
| `startSize=44` | Header height (horizontal) or width (vertical) |
| `horizontal=1` | `1` = horizontal lanes (header on top). `0` = vertical lanes (header on left) |
| `swimlaneLine=1` | Show dividing line between header and body |
| `fillColor` | Header background color |

---

## mxGraphModel Attributes

These control canvas-level settings on the `<mxGraphModel>` element:

| Attribute | Notes |
|---|---|
| `background` | Canvas background color (e.g. `#0F172A` for dark mode, `#ffffff` for light) |
| `grid=0\|1` | Show/hide grid |
| `gridSize=10` | Grid cell size in pixels |
| `pageWidth`, `pageHeight` | Canvas dimensions |
| `shadow=0\|1` | Global shadow toggle |

---

## Common Style Patterns

### Flat modern process node (light)
```
rounded=1;arcSize=24;fillColor=#DBEAFE;strokeColor=#3B82F6;fontColor=#1E293B;
fontSize=13;fontFamily=Helvetica;strokeWidth=1.5;shadow=0;whiteSpace=wrap;html=1;
```

### Dark terminal/code block
```
rounded=1;arcSize=12;fillColor=#1E293B;strokeColor=#334155;fontColor=#E2E8F0;
fontSize=12;fontFamily=Courier New;strokeWidth=1;shadow=0;whiteSpace=wrap;html=1;
```

### Decision diamond
```
shape=rhombus;fillColor=#FEF3C7;strokeColor=#F59E0B;fontColor=#1E293B;
fontSize=13;fontFamily=Helvetica;strokeWidth=1.5;shadow=0;whiteSpace=wrap;html=1;
```

### Transparent group box
```
rounded=1;arcSize=8;fillColor=#f5f5f5;strokeColor=#d6d6d6;fontColor=#333333;
fontSize=11;fontFamily=Helvetica;strokeWidth=1;dashed=1;dashPattern=6 3;
container=1;collapsible=0;
```

### Clean orthogonal edge
```
edgeStyle=orthogonalEdgeStyle;rounded=1;strokeColor=#94A3B8;strokeWidth=1.5;
fontColor=#64748B;fontSize=11;fontFamily=Helvetica;
labelBackgroundColor=#FFFFFF;shadow=0;
```

### Icon node (image with bottom label)
```
shape=image;verticalLabelPosition=bottom;labelBackgroundColor=default;
verticalAlign=top;aspect=fixed;imageAspect=0;image=file:///path/to/icon.png;
```

### Dark mode canvas
Set on `<mxGraphModel>`: `background="#0F172A"`
Dark fills: `fillColor=#1E293B`, strokes: `strokeColor=#334155`, font: `fontColor=#E2E8F0`
