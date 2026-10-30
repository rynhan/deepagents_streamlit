const pptxgen = require('pptxgenjs');

const pptx = new pptxgen();
pptx.layout = 'LAYOUT_WIDE';
pptx.author = 'Template example';
pptx.subject = 'Neo-Grid Bold design-system specimen';
pptx.title = 'Neo-Grid Bold — Example';
pptx.theme = { headFontFace: 'Arial', bodyFontFace: 'Arial', lang: 'en-US' };

const C = { paper: 'F5F4EF', bg: 'ECECE8', ink: '0A0A0A', lemon: 'E6FF3D', muted: '8A8A85', white: 'FFFFFF' };
const W = 13.333, H = 7.5, ST = pptx.ShapeType;
const rect = (s, x, y, w, h, fill, stroke = C.ink, sw = 1.25) =>
  s.addShape(ST.rect, { x, y, w, h, fill: { color: fill }, line: { color: stroke, width: sw } });
const text = (s, value, x, y, w, h, opts = {}) => s.addText(value, {
  x, y, w, h, margin: 0, fontFace: 'Arial', color: C.ink, fit: 'shrink',
  valign: 'mid', ...opts,
});
const mono = (s, value, x, y, w, h, opts = {}) => text(s, value, x, y, w, h, {
  fontFace: 'Courier New', fontSize: 8, charSpacing: 1.2, ...opts,
});
const base = (s, page) => {
  s.background = { color: C.bg };
  mono(s, 'FIELDWORK / STRATEGY                                         2026', 0.42, 0.2, 6.4, 0.2,
    { color: C.muted, fontSize: 7 });
  mono(s, page, 12.2, 7.1, 0.7, 0.18, { color: C.muted, align: 'right', fontSize: 7 });
};

// 12×8-inspired cover: the grid is translated into precise panel proportions.
{
  const s = pptx.addSlide(); base(s, '01 / 04');
  rect(s, 0.4, 0.48, 7.15, 5.95, C.paper);
  rect(s, 7.72, 0.48, 5.2, 2.5, C.lemon);
  rect(s, 7.72, 3.15, 2.5, 3.28, C.ink);
  rect(s, 10.38, 3.15, 2.54, 3.28, C.paper);
  mono(s, 'BRIEF  /  01', 0.8, 0.88, 2.0, 0.25, { color: C.muted });
  text(s, 'MAKE THE\nNEXT MOVE\nOBVIOUS.', 0.8, 1.7, 6.25, 2.7,
    { fontSize: 42, bold: true, charSpacing: -1.2, breakLine: false, valign: 'mid' });
  text(s, 'A field guide to better decisions under uncertainty.', 0.85, 5.25, 5.7, 0.6,
    { fontSize: 15, valign: 'top' });
  mono(s, 'SIGNAL → TEST → DECIDE', 8.1, 0.88, 4.25, 0.26, { bold: true, color: C.ink });
  text(s, '01', 8.08, 3.57, 1.85, 1.4, { fontSize: 50, bold: true, color: C.lemon });
  mono(s, 'THE QUESTION', 8.08, 5.65, 1.9, 0.3, { color: C.white, fontSize: 8 });
  text(s, 'What would change our mind?', 10.75, 4.0, 1.85, 1.2,
    { fontSize: 18, bold: true, valign: 'top' });
  mono(s, 'START HERE', 10.75, 5.65, 1.9, 0.3, { color: C.muted, fontSize: 8 });
}

// Research findings as bold split panels and a lemon signal block.
{
  const s = pptx.addSlide(); base(s, '02 / 04');
  rect(s, 0.4, 0.48, 4.1, 5.95, C.ink);
  rect(s, 4.67, 0.48, 4.0, 2.82, C.paper);
  rect(s, 4.67, 3.45, 4.0, 2.98, C.lemon);
  rect(s, 8.84, 0.48, 4.08, 5.95, C.paper);
  mono(s, 'FINDING / 01', 0.8, 0.9, 2.5, 0.25, { color: C.lemon });
  text(s, 'FRICTION\nHIDES IN\nHANDOFFS.', 0.8, 1.75, 3.35, 2.5,
    { color: C.white, fontSize: 31, bold: true, charSpacing: -0.6, breakLine: false });
  mono(s, 'OBSERVED ACROSS 12 TEAMS', 0.8, 5.55, 3.0, 0.3, { color: C.white, fontSize: 8 });
  mono(s, 'SIGNAL', 5.05, 0.84, 2.1, 0.22, { color: C.muted });
  text(s, 'People lose context between tools, not within a single task.',
    5.05, 1.38, 3.25, 1.2, { fontSize: 19, bold: true, valign: 'top' });
  mono(s, 'IMPLICATION', 5.05, 3.78, 2.5, 0.25);
  text(s, 'Design for the transition.', 5.05, 4.35, 3.15, 0.9,
    { fontSize: 23, bold: true, valign: 'top' });
  mono(s, 'NOT ANOTHER DASHBOARD', 5.05, 5.65, 3.0, 0.24, { fontSize: 8 });
  mono(s, 'NEXT TEST', 9.25, 0.88, 2.3, 0.25, { color: C.muted });
  text(s, 'Map every handoff and identify where the decision owner changes.',
    9.25, 1.6, 3.1, 1.5, { fontSize: 22, bold: true, valign: 'top' });
  text(s, '05', 9.25, 4.2, 2.2, 1.35, { fontSize: 48, bold: true, color: C.lemon });
  mono(s, 'WORKING DAYS', 9.28, 5.65, 2.3, 0.26, { color: C.muted });
}

// Comparison: bordered cells and the signature lemon highlight.
{
  const s = pptx.addSlide(); base(s, '03 / 04');
  text(s, 'WHAT WE TEST NEXT', 0.5, 0.55, 7.0, 0.65,
    { fontSize: 29, bold: true, charSpacing: -0.6 });
  const x = 0.5, y = 1.55, widths = [3.0, 4.45, 4.85], rowH = 1.03;
  const rows = [
    ['HYPOTHESIS', 'EVIDENCE TO SEEK', 'DECISION UNBLOCKED'],
    ['Clearer handoffs', 'Fewer missing-context moments', 'Where to redesign workflow'],
    ['Earlier ownership', 'Faster response after transfer', 'Who owns the next action'],
    ['Shorter feedback loops', 'More iteration per cycle', 'Which test to scale'],
  ];
  rows.forEach((row, r) => {
    let xx = x;
    row.forEach((v, c) => {
      const fill = r === 0 ? C.ink : (r === 2 ? C.lemon : C.paper);
      rect(s, xx, y + r * rowH, widths[c], rowH, fill);
      text(s, v, xx + 0.15, y + r * rowH + 0.1, widths[c] - 0.3, rowH - 0.2,
        { color: r === 0 ? C.white : C.ink, fontSize: r === 0 ? 9 : 14,
          bold: r === 0 || c === 0, charSpacing: r === 0 ? 0.6 : 0 });
      xx += widths[c];
    });
  });
}

const out = process.argv[2] || 'neo-grid-bold-example.pptx';
pptx.writeFile({ fileName: out });
