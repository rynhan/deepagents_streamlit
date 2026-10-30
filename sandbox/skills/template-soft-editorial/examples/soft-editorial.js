const pptxgen = require('pptxgenjs');

const pptx = new pptxgen();
pptx.layout = 'LAYOUT_WIDE';
pptx.author = 'Template example';
pptx.subject = 'Soft Editorial design-system specimen';
pptx.title = 'Soft Editorial — Example';
pptx.theme = { headFontFace: 'Cambria', bodyFontFace: 'Arial', lang: 'en-US' };

const C = { paper: 'F2EEDF', paper2: 'ECE6D2', ink: '2A241B', soft: '5C5345', pink: 'E1A4C2', lemon: 'D6DD63', blush: 'E8C9B6', sage: 'B7C7A8', lilac: 'C9B7D8', white: 'FFFFFF' };
const ST = pptx.ShapeType;
const round = (s, x, y, w, h, fill, transparency = 0) => s.addShape(ST.roundRect, {
  x, y, w, h, rectRadius: 0.16, fill: { color: fill, transparency },
  line: { color: fill, transparency: 100, width: 0.1 },
});
const text = (s, value, x, y, w, h, opts = {}) => s.addText(value, {
  x, y, w, h, margin: 0, fontFace: 'Cambria', color: C.ink, fit: 'shrink',
  valign: 'mid', ...opts,
});
const body = (s, value, x, y, w, h, opts = {}) => text(s, value, x, y, w, h, {
  fontFace: 'Arial', fontSize: 14, color: C.soft, valign: 'top', ...opts,
});
const pill = (s, value, x, y, w) => {
  round(s, x, y, w, 0.34, C.white, 10);
  text(s, value.toUpperCase(), x + 0.12, y + 0.04, w - 0.24, 0.24,
    { fontFace: 'Arial', fontSize: 8, bold: true, charSpacing: 1.0, color: C.soft, align: 'center' });
};
const base = (s) => { s.background = { color: C.paper }; };

// Cover: literary display, warm paper and quiet pill chrome.
{
  const s = pptx.addSlide(); base(s);
  pill(s, 'Field journal  /  2026', 0.72, 0.6, 2.25);
  text(s, 'A slower way\nto see clearly', 0.78, 1.55, 8.0, 2.15,
    { fontSize: 50, breakLine: false, valign: 'mid' });
  text(s, 'Notes on observation, evidence, and meaningful change.', 0.84, 4.08, 6.8, 0.7,
    { fontFace: 'Arial', fontSize: 16, color: C.soft, valign: 'top' });
  round(s, 9.25, 1.0, 3.2, 4.95, C.sage);
  text(s, '01', 9.65, 1.55, 2.35, 1.2, { fontSize: 48, color: C.ink });
  text(s, 'NOTICE\nTHE DETAIL', 9.65, 3.05, 2.5, 1.55,
    { fontSize: 24, breakLine: false, valign: 'top' });
  pill(s, 'Begin with a question', 9.65, 5.1, 2.35);
  body(s, 'Research brief   ·   October 2026', 0.85, 6.45, 5.2, 0.3, { fontSize: 10 });
}

// Method: four softly rounded pastel cards with ample breathing room.
{
  const s = pptx.addSlide(); base(s);
  pill(s, 'A gentle method', 0.72, 0.55, 1.85);
  text(s, 'From noticing to knowing', 0.75, 1.05, 9.2, 0.78, { fontSize: 33 });
  const steps = [
    ['01', 'Notice', 'Capture what happens before deciding what it means.', C.pink],
    ['02', 'Gather', 'Collect examples across people and situations.', C.lemon],
    ['03', 'Compare', 'Look for what repeats and what differs.', C.sage],
    ['04', 'Respond', 'Choose one action that tests the emerging insight.', C.lilac],
  ];
  steps.forEach((d, i) => {
    const x = 0.75 + i * 3.12;
    round(s, x, 2.25, 2.82, 3.55, d[3]);
    text(s, d[0], x + 0.25, 2.53, 0.9, 0.5, { fontSize: 19, color: C.soft });
    text(s, d[1], x + 0.25, 3.25, 2.3, 0.62, { fontSize: 25 });
    body(s, d[2], x + 0.27, 4.12, 2.25, 1.0, { fontSize: 13 });
  });
  body(s, 'A sequence, not a funnel: return to observation whenever the evidence feels thin.',
    0.78, 6.25, 9.2, 0.42, { fontSize: 12 });
}

// Quote: typographic pause with a soft paper-colored card.
{
  const s = pptx.addSlide(); base(s);
  round(s, 0.72, 0.72, 11.9, 5.95, C.white, 8);
  pill(s, 'A field note', 1.15, 1.18, 1.6);
  text(s, '“', 1.12, 1.68, 1.0, 1.1, { fontFace: 'Cambria', fontSize: 76, italic: true, color: C.pink });
  text(s, 'The useful question is not what people say they need, but what they are trying to make possible.',
    1.45, 2.28, 9.8, 1.95, { fontSize: 31, italic: true, valign: 'top' });
  body(s, 'Synthesis from twelve conversations', 1.5, 4.72, 5.2, 0.35, { fontSize: 11 });
  round(s, 1.5, 5.42, 1.18, 0.11, C.sage);
  round(s, 2.82, 5.42, 0.8, 0.11, C.lemon);
  round(s, 3.77, 5.42, 0.58, 0.11, C.lilac);
}

const out = process.argv[2] || 'soft-editorial-example.pptx';
pptx.writeFile({ fileName: out });
