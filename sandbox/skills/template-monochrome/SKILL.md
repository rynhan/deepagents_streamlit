---
name: template-monochrome
description: Use this design skill when the user selects Monochrome (Ivory Ledger) or requests its quiet cream-paper, ink-only editorial style for a PowerPoint deck. Provides design rules and a PPTXGenJS example; pair it with the general pptx skill for generation and QA.
license: Proprietary. See ../pptx/LICENSE.txt for terms.
---

# Monochrome PowerPoint Design

Apply Monochrome only when the user selects this style or explicitly asks for its visual language. This skill defines appearance; use `../pptx/SKILL.md` for PPTXGenJS mechanics, package handling, and required QA.

## Resources

- **Selection summary:** [references/preview.md](references/preview.md) — mood, use cases, and preview constraints.
- **Full design system:** [references/design.md](references/design.md) — canonical paper/ink palette, type roles, spacing, rules, and layout principles. Frontend-stage policy is not a PowerPoint canvas requirement.
- **Original visual specimen:** [assets/template.html](assets/template.html) and [assets/template.json](assets/template.json) — source layouts and structured metadata. HTML behavior is illustrative; do not copy it as a PPTX deliverable.
- **Runnable PPTXGenJS example:** [examples/monochrome.js](examples/monochrome.js).

## PowerPoint application

1. Set `pptx.layout = 'LAYOUT_WIDE'`; translate source proportions to the 16:9 slide rather than applying browser viewport rules.
2. Preserve the cream-paper field, ink/graphite-only palette, generous whitespace, fine rules, editorial labels, and limited serif italic moments. Do not add chromatic accents or shadows.
3. Read the full design system for type-role distinctions. The metadata and preview summary have a font-role inconsistency; follow the full design document and source HTML: Jost-style sans for display/body, Lora-style serif italic only for specified quote/insight moments, and mono for chrome.
4. For predictable output, the example maps Jost to Arial, Lora to Cambria, and JetBrains Mono to Courier New. Honor user-requested fonts and apply the font QA caveats in the general PPTX skill.
5. The HTML metadata reports 18 slides while the specimen has 16 sections. Treat its layouts as examples, not a required slide count. Replace all specimen copy with user content.

## Example

Run `node skills/template-monochrome/examples/monochrome.js [output.pptx]` from the repository root. The example is a visual reference, not a content template. Validate generated decks using the general PPTX skill's validation and visual QA steps.
