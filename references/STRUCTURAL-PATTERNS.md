# Structural Patterns

Choose the pattern that fits your diagram type.

### Linear Pattern (flowcharts, pipelines, processes)

```
TITLE
[Context note — optional]
START (or top-level node)
  ↓
[Step / Node A]
  ↓
[Step / Node B]
  ↓
END (or leaf nodes)
```

### Branching Pattern (parallel workflows, decision trees)

```
TITLE
[Context note — optional]
START
  ↓
JUNCTION (split)
  ↓       ↓       ↓
[Branch] [Branch] [Branch]
  ↓       ↓       ↓
JUNCTION (merge)
  ↓
END
```

### Hierarchical Pattern (org charts, taxonomies)

```
        [Root]
       /  |  \
   [A]   [B]   [C]
  / \         / \
[A1] [A2]  [C1] [C2]
```

## Adapting by diagram type

- **System architecture:** swimlane boxes per service layer, dependency arrows between them
- **Flowchart / process:** sequential top-down with decision diamonds
- **Org chart:** hierarchical with parent→child edges
- **Network topology:** layered (internet → firewall → DMZ → internal)
- **ER / data model:** entities with relationship edges, cardinality labels
