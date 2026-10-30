---
name: template-raw-grid
description: Use this design skill when the user selects Raw Grid or requests its neobrutalist, black-grid, blush-and-sage visual style for a PowerPoint deck. Provides the Raw Grid design rules and PPTXGenJS example; pair it with the general pptx skill for file generation and QA.
license: Proprietary. See ../pptx/LICENSE.txt for terms.
---

# Raw Grid PowerPoint Design

Apply Raw Grid only when the user selects this style or explicitly asks for its visual language. This skill defines appearance; use `../pptx/SKILL.md` for PPTXGenJS mechanics, package handling, and required QA.

## Resources

- **Selection summary:** [references/preview.md](references/preview.md) — mood, use cases, and preview constraints.
- **Full design system:** [references/design.md](references/design.md) — canonical palette, type roles, borders, spacing, components, and layout principles. The source's frontend-stage guidance is frontend-only, not a PowerPoint canvas requirement.
- **Original visual specimen:** [assets/template.html](assets/template.html) and [assets/template.json](assets/template.json) — source layouts and structured metadata. HTML behavior is illustrative; do not copy it as a PPTX deliverable.
- **Runnable PPTXGenJS example:** [examples/raw-grid.js](examples/raw-grid.js).

## PowerPoint application

1. Translate the source style to a 16:9 PowerPoint slide using `pptx.layout = 'LAYOUT_WIDE'`; do not use `100vw`, browser viewport behavior, or the frontend fixed-stage scaler in a PPTX.
2. Preserve the system's visual identity: white canvas, near-black structure, blush/sage surface accents, square geometry, 3px-equivalent black rules, heavy uppercase display type, sentence-case body, and hard-edged black offset shadows only when needed.
3. Use the exact token values and component rules in the full design system. Keep body content restrained within each bounded region; vary layouts based on the story rather than repeating a single grid.
4. Prefer Arial for the source's system sans stack in PPTX examples for predictable rendering. If the user requests a different font, honor that request and follow the font QA caveats in the general PPTX skill.
5. Treat HTML hover, touch, and keyboard navigation as non-applicable unless the user specifically requests interactive HTML output.
6. Use actual deck content in place of all specimen copy and placeholders. Preserve charts as native PowerPoint charts where suitable; use geometric shapes for the system's non-chart visual components.

## Example

Run `node skills/template-raw-grid/examples/raw-grid.js [output.pptx]` from the repository root. The example is a visual reference, not a content template. Validate generated decks using the general PPTX skill's validation and visual QA steps.
