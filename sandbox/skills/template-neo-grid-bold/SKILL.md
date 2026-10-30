---
name: template-neo-grid-bold
description: Use this design skill when the user selects Neo-Grid Bold or requests its punchy editorial neo-brutalist panels with a lemon accent for a PowerPoint deck. Provides design rules and a PPTXGenJS example; pair it with the general pptx skill for generation and QA.
license: Proprietary. See ../pptx/LICENSE.txt for terms.
---

# Neo-Grid Bold PowerPoint Design

Apply Neo-Grid Bold only when the user selects this style or explicitly asks for its visual language. This skill defines appearance; use `../pptx/SKILL.md` for PPTXGenJS mechanics, package handling, and required QA.

## Resources

- **Selection summary:** [references/preview.md](references/preview.md) — mood, use cases, and preview constraints.
- **Full design system:** [references/design.md](references/design.md) — canonical panel grid, palette, typography, and component rules. Frontend fixed-stage guidance is not a PowerPoint canvas requirement.
- **Original visual specimen:** [assets/template.html](assets/template.html) and [assets/template.json](assets/template.json) — source layouts and structured metadata. HTML behavior is illustrative; do not copy it as a PPTX deliverable.
- **Runnable PPTXGenJS example:** [examples/neo-grid-bold.js](examples/neo-grid-bold.js).

## PowerPoint application

1. Set `pptx.layout = 'LAYOUT_WIDE'` and translate the source 12×8 panel logic into coordinates on the 16:9 slide. Do not use CSS grid or viewport sizing as PPTX layout instructions.
2. Preserve putty/off-white, ink black, and lemon accent panels; heavy uppercase display; mono labels; rigid block compositions; and the source's small corner/block marks. Avoid adding colors or decorative styles outside the system.
3. Use the detailed reference for exact tokens and layout grammar. Source layouts include cover, contents, stats, feature cards, chart, divider, quote, findings, process, and comparison matrix.
4. For dependable rendering, the example maps Space Grotesk to Arial and JetBrains Mono to Courier New. Honor user-requested fonts and apply the font QA caveats in the general PPTX skill.
5. The HTML metadata says 13 slides while the specimen contains 12 sections; use its layouts as inspiration, not as a mandatory sequence or count. Replace all demo copy with real deck content.

## Example

Run `node skills/template-neo-grid-bold/examples/neo-grid-bold.js [output.pptx]` from the repository root. The example is a visual reference, not a content template. Validate generated decks using the general PPTX skill's validation and visual QA steps.
