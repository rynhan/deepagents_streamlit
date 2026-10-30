---
name: template-cobalt-grid
description: Use this design skill when the user selects Cobalt Grid or requests its cream-and-cobalt editorial, graph-paper visual style for a PowerPoint deck. Provides Cobalt Grid design rules and a PPTXGenJS example; pair it with the general pptx skill for file generation and QA.
license: Proprietary. See ../pptx/LICENSE.txt for terms.
---

# Cobalt Grid PowerPoint Design

Apply Cobalt Grid only when the user selects this style or explicitly asks for its visual language. This skill defines appearance; use `../pptx/SKILL.md` for PPTXGenJS mechanics, package handling, and required QA.

## Resources

- **Selection summary:** [references/preview.md](references/preview.md) — mood, use cases, and preview constraints.
- **Full design system:** [references/design.md](references/design.md) — canonical colors, typography, grid, rules, and components. Frontend fixed-stage guidance is not a PowerPoint canvas requirement.
- **Original visual specimen:** [assets/template.html](assets/template.html) and [assets/template.json](assets/template.json) — source layouts and structured metadata. HTML behavior is illustrative; do not copy it as a PPTX deliverable.
- **Runnable PPTXGenJS example:** [examples/cobalt-grid.js](examples/cobalt-grid.js).

## PowerPoint application

1. Use `pptx.layout = 'LAYOUT_WIDE'` and translate the source's proportions to slide coordinates. Do not rely on viewport CSS or the frontend fixed-stage scaler in a PPTX.
2. Preserve the source's warm paper and electric cobalt palette, permanent graph-paper/grid motif, editorial hierarchy, and two-color restraint. For this refined variant, omit decorative cobalt frame/underline rules, pixel-glitch columns, and QR-like blocks. Keep separators between ledger rows faint and paper-toned rather than cobalt.
3. Follow the full design system for exact colors, type roles, spacing, and layout. Vary slide compositions according to content; the source specimen's cover, index, chapter opener, chart, quote, ledger, and colophon are useful layout references.
4. For dependable rendering, the example maps Newsreader to Cambria, Hanken Grotesk to Arial, and DM Mono to Courier New. Honor user-requested fonts and apply the font QA caveats in the general PPTX skill.
5. Replace specimen content with the user's real content. Use native PowerPoint charts for chartable data; use shape-based pixel motifs only as decorative elements.

## Example

Run `node skills/template-cobalt-grid/examples/cobalt-grid.js [output.pptx]` from the repository root. The example is a visual reference, not a content template. Validate generated decks using the general PPTX skill's validation and visual QA steps.
