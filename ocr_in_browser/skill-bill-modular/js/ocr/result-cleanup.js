const STANDALONE_JUNK = /^[|¦!¡.,:;·•_~=`'"<>()[\]{}]+$/;
const KEYBOARD_ARTIFACT = /^(?:(?:CAPS(?:\s+LOCK)?|SHIFT|CTRL|CONTROL|FN|ALT|TAB|ESC|ENTER|SPACE|CMD|OPTION|META)(?:\s+(?:CAPS|SHIFT|CTRL|CONTROL|FN|ALT|TAB|ESC|ENTER|SPACE|CMD|OPTION|META|[A-Z]{1,3})){0,3}|U)$/i;

export function buildReading(data, { profile = "receipt" } = {}) {
  const lines = [];
  for (const block of (data?.blocks || [])) {
    for (const paragraph of (block.paragraphs || [])) {
      for (const sourceLine of (paragraph.lines || [])) {
        const line = cleanLine(sourceLine);
        if (!line.text) continue;
        // In receipt mode, hide only obvious, low-confidence keyboard/UI spillover.
        // The generic OCR path still preserves low-confidence content for inspection.
        if (profile === "receipt" && isKeyboardArtefact(line.text)) {
          const upper = line.text.trim().toUpperCase();
          const explicitKeyLabel = /^(?:CAPS(?: LOCK)?|SHIFT|CTRL|CONTROL|FN|ALT|TAB|ESC|ENTER|SPACE|CMD|OPTION|META)\b/.test(upper);
          const isolatedLetterNoise = /^U$/.test(upper) && (line.confidence ?? 0) < 25;
          if (explicitKeyLabel || isolatedLetterNoise) continue;
        }
        lines.push(line);
      }
    }
  }

  if (!lines.length && data?.text) {
    for (const raw of String(data.text).split(/\r?\n/)) {
      const text = cleanupText(raw);
      if (text) lines.push({ text, confidence: null, words: [], bbox: null });
    }
  }
  return {
    text: lines.map(line => line.text).join("\n").trim(),
    lines,
    createdAt: new Date().toISOString(),
    sourceConfidence: Number.isFinite(Number(data?.confidence)) ? Number(data.confidence) : null
  };
}

function cleanLine(sourceLine) {
  const rawWords = Array.isArray(sourceLine.words) ? sourceLine.words : [];
  let words = rawWords.map(word => ({
    text: cleanupToken(String(word.text || "")),
    confidence: confidenceValue(word.confidence),
    bbox: word.bbox || null
  })).filter(word => word.text && !STANDALONE_JUNK.test(word.text));

  // Drop trailing standalone OCR punctuation artifacts (e.g. `|`, `|.`, `o:`),
  // but keep punctuation attached to meaningful tokens.
  while (words.length > 0 && isTrailingNoiseToken(words[words.length - 1].text)) words.pop();

  const reconstructed = words.length ? reconstructSpacing(words) : String(sourceLine.text || "");
  let text = cleanupText(reconstructed || sourceLine.text || "");
  if (!text && !words.length) return { text: "", confidence: confidenceValue(sourceLine.confidence), words, bbox: sourceLine.bbox || null };

  // For common Polish-company receipt headers, OCR often turns `S.A.` into `SA. |`.
  // Normalize only a legal-form suffix at the very end of the line.
  const legalSuffix = text.match(/^(.+?)\s+S\s*\.?\s*A\s*\.?\s*$/i);
  if (legalSuffix) text = `${legalSuffix[1].trim()} S.A.`;

  let confidence = confidenceValue(sourceLine.confidence);
  if (confidence === null && words.length) {
    const valid = words.map(word => word.confidence).filter(value => value !== null);
    if (valid.length) confidence = valid.reduce((sum, value) => sum + value, 0) / valid.length;
  }

  return { text, confidence, words, bbox: sourceLine.bbox || null };
}

function cleanupToken(value) {
  return String(value || "")
    .replace(/[\u200B-\u200D\uFEFF]/g, "")
    .replace(/^[`´“”‘’]+|[`´“”‘’]+$/g, "")
    .trim();
}

export function cleanupText(value) {
  let text = String(value || "")
    .replace(/[\u200B-\u200D\uFEFF]/g, "")
    .replace(/ {4,}/g, "   ")
    .replace(/\t{2,}/g, "\t")
    .trim();
  // Typical Tesseract tails around printed separators and box edges.
  text = text.replace(/\s+(?:\|\s*[.:;,]?|[¦|][.:;,]?|o\s*:|[.:;,]\s*\|)\s*$/i, "");
  text = text.replace(/[\s|¦]+$/g, "").trim();
  if (STANDALONE_JUNK.test(text)) return "";
  return text;
}

function isTrailingNoiseToken(value) {
  return /^(?:[|¦]+[.:;,]?|[.:;,]\|+|o\s*:|[·•_~=]+)$/i.test(String(value || "").trim());
}

function reconstructSpacing(words) {
  const positioned = words.filter(word => word.bbox && Number.isFinite(Number(word.bbox.x0)) && Number.isFinite(Number(word.bbox.x1)))
    .sort((a, b) => Number(a.bbox.x0) - Number(b.bbox.x0));
  if (positioned.length < 2) return words.map(word => word.text).join(" ");
  const heights = positioned.map(word => Math.max(1, Number(word.bbox.y1) - Number(word.bbox.y0))).sort((a, b) => a - b);
  const typicalHeight = heights[Math.floor(heights.length / 2)] || 12;
  let result = positioned[0].text;
  for (let index = 1; index < positioned.length; index += 1) {
    const previous = positioned[index - 1];
    const current = positioned[index];
    const gap = Math.max(0, Number(current.bbox.x0) - Number(previous.bbox.x1));
    let separator = " ";
    if (gap > typicalHeight * 3.3) separator = "\t";
    else if (gap > typicalHeight * 1.9) separator = "   ";
    else if (gap > typicalHeight * 1.05) separator = "  ";
    result += separator + current.text;
  }
  return result.trim();
}

function confidenceValue(value) {
  if (value === null || value === undefined || value === "" || !Number.isFinite(Number(value)) || Number(value) < 0) return null;
  return Math.max(0, Math.min(100, Number(value)));
}

function isKeyboardArtefact(text) {
  const normalized = String(text || "").replace(/[^a-z0-9 ]/gi, " ").replace(/\s+/g, " ").trim();
  return KEYBOARD_ARTIFACT.test(normalized);
}

export function normalizeForComparison(text) {
  return String(text || "")
    .normalize("NFD").replace(/[\u0300-\u036f]/g, "")
    .toLowerCase().replace(/[^a-z0-9]+/g, " ").trim().replace(/\s+/g, " ");
}
