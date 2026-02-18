# Diagram Critique Template

Use this template for each Ralph Loop iteration to systematically review the rendered diagram.

## Layout issues
- Are elements overlapping or too cramped?
- Is the flow direction clear and consistent?
- Are related elements aligned properly?
- Are edges crossing through text labels? Fix by adding `labelBackgroundColor=` matching the diagram's background colour to the label's style

## Missing connections
- Are there orphaned nodes with no edges?
- Are all logical relationships represented?
- Do edges connect to the correct source and target?

## Style inconsistencies (compare against STYLE-REFERENCE.md)
- Are fill colours correct for each element type?
- Are edge styles consistent (stroke colour, width, dashing)?
- Are fonts consistent with the sizes defined in the reference?

## Icons (if used)
- Are icons rendering with correct transparency (no white/opaque backgrounds)?
- Are icons sharp and not pixelated or blurry?
- Is the aspect ratio preserved (not stretched or squashed)?
- Are icons consistently sized relative to each other?

## Missing content
- Are all elements from the requirements present?
- Are labels clear and complete?
- Is any supporting context (legend, notes) needed?
