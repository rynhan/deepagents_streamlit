---
name: template-soft-editorial
description: Use this design skill when the user selects Soft Editorial or requests its warm-paper, literary serif, soft pastel-card style for a PowerPoint deck. Provides design rules and a PPTXGenJS example; pair it with the general pptx skill for generation and QA.
license: Proprietary. See ../pptx/LICENSE.txt for terms.
---

# Soft Editorial PowerPoint Design

Apply Soft Editorial only when the user selects this style or explicitly asks for its visual language. This skill defines appearance; use `../pptx/SKILL.md` for PPTXGenJS mechanics, package handling, and required QA.

## Resources

- **Selection summary:** [references/preview.md](references/preview.md) — mood, use cases, and preview constraints.
- **Full design system:** [references/design.md](references/design.md) — canonical warm-paper palette, type roles, spacing, shapes, and layout principles. Frontend fixed-stage guidance is not a PowerPoint canvas requirement.
- **Original visual specimen:** [assets/template.html](assets/template.html), [assets/template.json](assets/template.json), and [assets/deck-stage.js](assets/deck-stage.js) — source layouts and metadata. Browser scaling/navigation is illustrative; do not copy it as PPTX output.
- **Runnable PPTXGenJS example:** [examples/soft-editorial.js](examples/soft-editorial.js).

## PowerPoint application

1. Set `pptx.layout = 'LAYOUT_WIDE'` and map the source 1920×1080 proportions onto PowerPoint coordinates. Do not implement the browser's stage scaler inside a PPTX.
2. Preserve warm cream as the canvas; use pastel colors on cards, not as general backgrounds; retain rounded containers, generous breathing room, serif-led hierarchy, and sober sans-serif body copy.
3. Follow the full reference for exact color and component tokens. Source slide patterns include cover, foreword, method, insight cards, stats, quote, findings, chart, process, and comparison.
4. For dependable rendering, the example maps Cormorant Garamond to Cambria and Work Sans to Arial. Honor user-requested fonts and apply the font QA caveats in the general PPTX skill.
5. Replace all specimen content with the user's real content. Keep generous text-box slack; this style depends on spacious compositions and should not be made dense to fit more copy.

## Example

Run `node skills/template-soft-editorial/examples/soft-editorial.js [output.pptx]` from the repository root. The example is a visual reference, not a content template. Validate generated decks using the general PPTX skill's validation and visual QA steps.
