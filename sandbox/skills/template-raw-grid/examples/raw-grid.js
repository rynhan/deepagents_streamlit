const pptxgen = require('pptxgenjs');

const pptx = new pptxgen();
pptx.layout = 'LAYOUT_WIDE';
pptx.author = 'Template example';
pptx.subject = 'Raw Grid design-system specimen';
pptx.title = 'Raw Grid — Example';
pptx.company = 'Design System';
pptx.lang = 'en-US';
pptx.theme = {
  headFontFace: 'Arial',
  bodyFontFace: 'Arial',
  lang: 'en-US',
};

const C = { ink: '0A0A0A', white: 'FFFFFF', pink: 'F2D4CF', green: 'E5EDD6', gray: 'F5F5F5' };
const W = 13.333, H = 7.5, BORDER = 1.7; // ≈3px on a 1920×1080 reference stage
const ST = pptx.ShapeType;
const rect = (s, x, y, w, h, fill, line = C.ink, width = BORDER) =>
  s.addShape(ST.rect, { x, y, w, h, fill: { color: fill }, line: { color: line, width } });
const txt = (s, text, x, y, w, h, opts = {}) => s.addText(text, {
  x, y, w, h, margin: 0, breakLine: false, color: C.ink, fontFace: 'Arial',
  fit: 'shrink', valign: 'mid', ...opts,
});
const label = (s, text, x, y) => {
  rect(s, x, y, 1.48, 0.31, C.ink, C.ink, 0);
  txt(s, text.toUpperCase(), x + 0.1, y + 0.025, 1.28, 0.25,
    { color: C.white, fontSize: 9, bold: true, charSpacing: 1.2, align: 'center' });
};

// Cover: hard split, blunt type, and black structural border.
{
  const s = pptx.addSlide();
  s.background = { color: C.white };
  rect(s, 0, 0, 6.2, H, C.pink);
  s.addShape(ST.line, { x: 6.2, y: 0, w: 0, h: H, line: { color: C.ink, width: BORDER } });
  label(s, 'Field Notes', 0.65, 0.65);
  txt(s, 'BUILD\nWITHOUT\nPERMISSION', 0.65, 2.05, 5.0, 3.2,
    { fontSize: 43, bold: true, charSpacing: -1.4, breakLine: false, valign: 'mid' });
  txt(s, 'A practical guide to turning a clear idea into measurable progress.', 0.68, 5.67, 4.8, 0.82,
    { fontSize: 16, breakLine: false, valign: 'top' });
  const items = ['The opportunity', 'The operating model', 'Proof of progress', 'Next actions'];
  items.forEach((item, i) => {
    const y = i * 1.875;
    if (i > 0) s.addShape(ST.line, { x: 6.2, y, w: W - 6.2, h: 0, line: { color: C.ink, width: BORDER } });
    if (i === 2) rect(s, 6.2, y, W - 6.2, 1.875, C.green, C.green, 0);
    txt(s, `→  ${item.toUpperCase()}`, 6.75, y + 0.55, 5.7, 0.7,
      { fontSize: 20, bold: true, charSpacing: 0.6 });
  });
}

// Metric slide: touching regions, pastel fills, and heavy stat typography.
{
  const s = pptx.addSlide();
  s.background = { color: C.white };
  rect(s, 0, 0, W, 0.72, C.white);
  txt(s, 'PROOF, NOT PROMISES', 0.55, 0.17, 7.5, 0.38,
    { fontSize: 20, bold: true, charSpacing: 0.6 });
  s.addShape(ST.line, { x: 0, y: 0.72, w: W, h: 0, line: { color: C.ink, width: BORDER } });
  const cards = [
    { x: 0, fill: C.pink, value: '42%', title: 'FASTER CYCLE', body: 'Time from first test to a decision.' },
    { x: W / 3, fill: C.green, value: '3.4×', title: 'MORE SIGNAL', body: 'Useful evidence per research sprint.' },
    { x: 2 * W / 3, fill: C.gray, value: '08', title: 'WEEKS', body: 'To validate the first repeatable path.' },
  ];
  cards.forEach((c, i) => {
    rect(s, c.x, 0.74, W / 3, H - 0.74, c.fill, C.ink, BORDER);
    txt(s, String(i + 1).padStart(2, '0'), c.x + 0.35, 1.15, 1.0, 0.5,
      { fontSize: 18, bold: true, transparency: 68 });
    txt(s, c.value, c.x + 0.38, 2.35, 3.5, 1.15,
      { fontSize: 48, bold: true, charSpacing: -1.5 });
    txt(s, c.title, c.x + 0.4, 3.75, 3.55, 0.45,
      { fontSize: 15, bold: true, charSpacing: 0.7 });
    txt(s, c.body, c.x + 0.4, 4.48, 3.3, 1.1,
      { fontSize: 16, valign: 'top' });
  });
}

// Comparison slide: strict black header and zebra rows.
{
  const s = pptx.addSlide();
  s.background = { color: C.white };
  label(s, 'Decision table', 0.55, 0.45);
  txt(s, 'CHOOSE THE NEXT TEST', 0.55, 1.0, 8.6, 0.7,
    { fontSize: 30, bold: true, charSpacing: -0.8 });
  const x = 0.55, y = 2.0, widths = [3.1, 4.5, 4.6], rowH = 0.86;
  const rows = [
    ['SIGNAL', 'CURRENT STATE', 'NEXT PROOF'],
    ['Activation', 'Interest is high; setup is uneven.', 'Observe 10 first-run sessions.'],
    ['Retention', 'Repeat use varies by team.', 'Compare week-two return rates.'],
    ['Economics', 'Support effort is not yet stable.', 'Measure cost per active account.'],
  ];
  rows.forEach((row, r) => {
    let xx = x;
    row.forEach((value, c) => {
      const fill = r === 0 ? C.ink : (r % 2 ? C.white : C.gray);
      rect(s, xx, y + r * rowH, widths[c], rowH, fill);
      txt(s, value, xx + 0.15, y + r * rowH + 0.08, widths[c] - 0.3, rowH - 0.16,
        { color: r === 0 ? C.white : C.ink, fontSize: r === 0 ? 11 : 14,
          bold: r === 0 || c === 0, charSpacing: r === 0 ? 0.8 : 0, valign: 'mid' });
      xx += widths[c];
    });
  });
}

const out = process.argv[2] || 'raw-grid-example.pptx';
pptx.writeFile({ fileName: out });
