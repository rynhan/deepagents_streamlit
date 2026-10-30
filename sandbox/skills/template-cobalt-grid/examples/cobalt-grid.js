const pptxgen = require('pptxgenjs');

const pptx = new pptxgen();
pptx.layout = 'LAYOUT_WIDE';
pptx.author = 'Template example';
pptx.subject = 'Cobalt Grid design-system specimen';
pptx.title = 'Cobalt Grid — Example';
pptx.theme = { headFontFace: 'Cambria', bodyFontFace: 'Arial', lang: 'en-US' };

const C = { paper: 'F0EBDE', paper2: 'E6E0CE', ink: '1F2BE0', soft: '5560E5', faint: 'C8C9E5', dark: '24243A' };
const W = 13.333, H = 7.5, ST = pptx.ShapeType;
const line = (s, x1, y1, x2, y2, color = C.ink, width = 0.65) =>
  s.addShape(ST.line, { x: x1, y: y1, w: x2 - x1, h: y2 - y1, line: { color, width } });
const text = (s, value, x, y, w, h, opts = {}) => s.addText(value, {
  x, y, w, h, margin: 0, fontFace: 'Cambria', color: C.dark, fit: 'shrink',
  valign: 'mid', ...opts,
});
const mono = (s, value, x, y, w, h, opts = {}) => text(s, value, x, y, w, h,
  { fontFace: 'Courier New', fontSize: 9, charSpacing: 1.2, color: C.ink, ...opts });
const background = (s) => {
  s.background = { color: C.paper };
  // Sparse graph-paper motif; kept light so it stays behind all content.
  for (let x = 0.36; x < W; x += 0.22) line(s, x, 0.28, x, H - 0.28, C.faint, 0.12);
  for (let y = 0.28; y < H; y += 0.22) line(s, 0.36, y, W - 0.36, y, C.faint, 0.12);
};

// Cover: restrained editorial hierarchy and a quiet graph-paper backdrop.
{
  const s = pptx.addSlide(); background(s);
  mono(s, 'FIELD REPORT   /   2026', 0.7, 0.62, 4.0, 0.25);
  text(s, 'The next\nuseful signal', 0.7, 1.55, 8.1, 2.8,
    { fontSize: 54, bold: true, color: C.ink, breakLine: false, valign: 'mid' });
  text(s, 'A research bulletin on turning observation into action.', 0.75, 4.7, 6.4, 0.75,
    { fontFace: 'Arial', fontSize: 17, color: C.dark });
  mono(s, 'INSIGHT 01     METHOD 02     IMPLICATION 03', 0.75, 5.93, 7.6, 0.3);
}

// Index: ledger-like rows separated by neutral paper-toned rules.
{
  const s = pptx.addSlide(); background(s);
  mono(s, 'CONTENTS   /   01—04', 0.7, 0.65, 4.0, 0.25);
  text(s, 'Reading the\nlandscape', 0.7, 1.15, 6.0, 1.55,
    { fontSize: 38, bold: true, color: C.ink, breakLine: false });
  const entries = [
    ['01', 'The signal', 'What changed, and why it matters'],
    ['02', 'The index', 'Patterns across the observed field'],
    ['03', 'The test', 'Evidence that can change a decision'],
    ['04', 'The ledger', 'Actions, owners, and open questions'],
  ];
  entries.forEach((e, i) => {
    const y = 3.0 + i * 0.86;
    line(s, 0.72, y, 10.9, y, C.paper2, 0.65);
    mono(s, e[0], 0.8, y + 0.22, 0.7, 0.25);
    text(s, e[1], 1.7, y + 0.12, 3.1, 0.45, { fontSize: 22, bold: true, color: C.ink });
    text(s, e[2], 5.0, y + 0.16, 5.6, 0.37, { fontFace: 'Arial', fontSize: 13 });
  });
  line(s, 0.72, 6.44, 10.9, 6.44, C.paper2, 0.65);
}

// Chart: native clustered column chart, styled in the two-color palette.
{
  const s = pptx.addSlide(); background(s);
  mono(s, 'OBSERVATION   /   QUARTERLY', 0.7, 0.65, 5.0, 0.25);
  text(s, 'Evidence accumulates', 0.7, 1.05, 8.0, 0.75,
    { fontSize: 34, bold: true, color: C.ink });
  s.addChart(pptx.ChartType.bar, [{ name: 'Validated tests', labels: ['Q1', 'Q2', 'Q3', 'Q4'], values: [12, 19, 27, 38] }], {
    x: 0.85, y: 2.1, w: 7.4, h: 4.2, catAxisLabelFontFace: 'Courier New', catAxisLabelFontSize: 10,
    catAxisLabelColor: C.dark, valAxisLabelFontFace: 'Courier New', valAxisLabelFontSize: 9,
    valAxisLabelColor: C.dark, chartColors: [C.ink], showLegend: false, showTitle: false,
    showValue: true, dataLabelPosition: 'outEnd', showCatName: false,
    valGridLine: { color: C.faint, size: 0.5 }, catGridLine: { style: 'none' },
    showCatName: false, showValAxisTitle: false, showCatAxisTitle: false,
    showBorder: false, showPlotArea: false, showChartArea: false,
  });
  text(s, '38', 9.3, 2.35, 2.3, 1.2, { fontSize: 56, bold: true, color: C.ink });
  mono(s, 'VALIDATED\nTESTS', 9.36, 3.65, 2.5, 0.65, { breakLine: false });
  text(s, 'More evidence means fewer decisions made on intuition alone.', 9.35, 4.65, 2.75, 1.05,
    { fontFace: 'Arial', fontSize: 14, valign: 'top' });
}

const out = process.argv[2] || 'cobalt-grid-example.pptx';
pptx.writeFile({ fileName: out });
