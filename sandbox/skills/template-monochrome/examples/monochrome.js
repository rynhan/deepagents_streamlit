const pptxgen = require('pptxgenjs');

const pptx = new pptxgen();
pptx.layout = 'LAYOUT_WIDE';
pptx.author = 'Template example';
pptx.subject = 'Monochrome design-system specimen';
pptx.title = 'Monochrome — Example';
pptx.theme = { headFontFace: 'Arial', bodyFontFace: 'Arial', lang: 'en-US' };

const C = { paper: 'FAFADF', paper2: 'F2F2D2', warm: 'F5F0E4', ink: '1A1A16', graph: '5E5E54', soft: '8A8A80' };
const W = 13.333, H = 7.5, ST = pptx.ShapeType;
const rule = (s, x, y, w, color = C.graph, width = 0.65) =>
  s.addShape(ST.line, { x, y, w, h: 0, line: { color, width } });
const text = (s, value, x, y, w, h, opts = {}) => s.addText(value, {
  x, y, w, h, margin: 0, fontFace: 'Arial', color: C.ink, fit: 'shrink',
  valign: 'mid', ...opts,
});
const mono = (s, value, x, y, w, h, opts = {}) => text(s, value, x, y, w, h, {
  fontFace: 'Courier New', fontSize: 9, charSpacing: 1.4, color: C.graph, ...opts,
});
const setup = (s, page) => {
  s.background = { color: C.paper };
  rule(s, 0.62, 0.38, 12.1, C.ink, 0.7);
  mono(s, `FIELD NOTES                                      RESEARCH SERIES   /   ${page}`, 0.65, 0.14, 11.9, 0.18,
    { fontSize: 8 });
  rule(s, 0.62, 7.08, 12.1, C.ink, 0.7);
};

// Cover: tactile paper, quiet title hierarchy, minimal chrome.
{
  const s = pptx.addSlide(); setup(s, '01');
  text(s, 'A study of\nsmall signals', 0.78, 1.55, 8.9, 2.35,
    { fontSize: 52, bold: false, breakLine: false, valign: 'mid' });
  text(s, 'How disciplined observation reveals the next useful move.', 0.82, 4.25, 6.4, 0.72,
    { fontSize: 17, color: C.graph, valign: 'top' });
  rule(s, 0.82, 5.5, 1.1, C.ink, 1.0);
  mono(s, 'AN EVIDENCE-LED BRIEF     /     OCTOBER 2026', 0.82, 5.72, 5.7, 0.3);
  text(s, '01', 11.15, 5.32, 1.1, 1.1, { fontSize: 50, color: C.paper2, bold: true, align: 'right' });
}

// Findings: careful two-column editorial page with a pull quote.
{
  const s = pptx.addSlide(); setup(s, '04');
  mono(s, '04     /     OBSERVATIONS', 0.78, 0.68, 4.5, 0.28);
  text(s, 'The pattern is\nnot the point', 0.78, 1.15, 5.15, 1.75,
    { fontSize: 37, breakLine: false, valign: 'top' });
  text(s, 'Patterns are useful only when they change what a team does next. The strongest signal in this review was not a single event, but the repeated gap between expressed intent and observed follow-through.',
    0.82, 3.35, 4.75, 1.7, { fontSize: 16, color: C.graph, valign: 'top', breakLine: false });
  s.addShape(ST.line, { x: 6.2, y: 1.1, w: 0, h: 4.95, line: { color: C.graph, width: 0.65 } });
  text(s, '“', 6.75, 1.28, 1.0, 0.9, { fontFace: 'Cambria', fontSize: 66, italic: true, color: C.soft });
  text(s, 'What people repeat is often more revealing than what they remember.',
    6.82, 2.1, 5.25, 1.8, { fontFace: 'Cambria', fontSize: 28, italic: true, color: C.ink, valign: 'top' });
  mono(s, 'FIELD INTERVIEW     /     PARTICIPANT 07', 6.85, 4.65, 5.2, 0.3, { fontSize: 8 });
  text(s, 'Interpretation', 6.85, 5.35, 2.4, 0.36, { fontSize: 14, bold: true });
  text(s, 'Reduce reliance on recall; observe behavior close to the decision.',
    6.85, 5.75, 5.0, 0.55, { fontSize: 13, color: C.graph, valign: 'top' });
}

// Quiet metrics: ink-only stat layout without chromatic highlighting.
{
  const s = pptx.addSlide(); setup(s, '06');
  mono(s, '06     /     MEASURES', 0.78, 0.68, 4.5, 0.28);
  text(s, 'Progress in context', 0.78, 1.08, 7.5, 0.78, { fontSize: 34 });
  const metrics = [
    ['12', 'TEAMS OBSERVED', 'Across three working sessions'],
    ['68%', 'TASK COMPLETION', 'Completed without facilitator help'],
    ['2.1×', 'RETURN VISITS', 'Compared with the prior period'],
  ];
  metrics.forEach((m, i) => {
    const x = 0.8 + i * 4.05;
    rule(s, x, 2.35, 3.55, C.ink, 0.7);
    text(s, m[0], x, 2.72, 3.45, 1.25, { fontSize: 48 });
    mono(s, m[1], x, 4.2, 3.45, 0.32, { fontSize: 9 });
    text(s, m[2], x, 4.75, 3.45, 0.85, { fontSize: 14, color: C.graph, valign: 'top' });
  });
  text(s, 'Measures describe this sample; they should not be read as population estimates.',
    0.82, 6.15, 8.8, 0.38, { fontSize: 10, color: C.soft });
}

const out = process.argv[2] || 'monochrome-example.pptx';
pptx.writeFile({ fileName: out });
