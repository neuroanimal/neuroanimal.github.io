import assert from "node:assert/strict";
import { cleanupText, buildReading, normalizeForComparison } from "../js/ocr/result-cleanup.js";
import { splitReceiptPrice, filterLinesByScope } from "../js/ocr/receipt-scope.js";
import { appendReading } from "../js/ocr/line-merger.js";

const bbox = (x0, y0, x1, y1) => ({ x0, y0, x1, y1 });

assert.equal(cleanupText("Family Benefits S.A. |"), "Family Benefits S.A.");
assert.equal(cleanupText("Family Benefits SA. |."), "Family Benefits SA.");
assert.equal(cleanupText("PTU A 23% o:"), "PTU A 23%");

const sample = {
  text: "Family Benefits SA. |\nCAPS A\nNIP 1234567890\nPTU A 23% 1,87",
  confidence: 60,
  blocks: [{ paragraphs: [{ lines: [
    { text: "Family Benefits SA. |", confidence: 59, bbox: bbox(0, 0, 170, 12), words: [
      { text: "Family", confidence: 72, bbox: bbox(0, 0, 34, 12) },
      { text: "Benefits", confidence: 77, bbox: bbox(39, 0, 84, 12) },
      { text: "SA.", confidence: 60, bbox: bbox(91, 0, 110, 12) },
      { text: "|", confidence: 90, bbox: bbox(116, 0, 120, 12) }
    ] },
    { text: "CAPS A", confidence: 5, bbox: bbox(0, 20, 40, 31), words: [{text:"CAPS",confidence:20,bbox:bbox(0,20,25,31)},{text:"A",confidence:12,bbox:bbox(28,20,35,31)}] },
    { text: "NIP 1234567890", confidence: 88, bbox: bbox(0, 40, 140, 52), words: [{text:"NIP",confidence:92,bbox:bbox(0,40,22,52)},{text:"1234567890",confidence:86,bbox:bbox(27,40,88,52)}] },
    { text: "PTU A 23% 1,87", confidence: 70, bbox: bbox(0, 60, 180, 72), words: [
      {text:"PTU",confidence:80,bbox:bbox(0,60,20,72)}, {text:"A",confidence:75,bbox:bbox(23,60,30,72)},
      {text:"23%",confidence:65,bbox:bbox(34,60,55,72)}, {text:"1,87",confidence:70,bbox:bbox(140,60,163,72)}
    ] }
  ] }] }]
};
const reading = buildReading(sample, { profile: "receipt" });
assert.equal(reading.lines.length, 3, "low-confidence keyboard spillover should be hidden in receipt mode");
assert.equal(reading.lines[0].text, "Family Benefits S.A.");
assert.match(reading.lines[3 - 1].text, /PTU A 23%\t1,87|PTU A 23%   1,87/);

const split = splitReceiptPrice({ text: "PTU A 23%\t1,87" });
assert.deepEqual(split, { label: "PTU A 23%", price: "1,87" });

const lines = [
  { text: "Family Benefits S.A.", confidence: 80 },
  { text: "NIP 1234567890", confidence: 90 },
  { text: "Milk 2,99", confidence: 88 },
  { text: "PTU A 23% 1,87", confidence: 78 },
  { text: "SUMA PLN 9,99", confidence: 93 },
  { text: "ROZLICZENIE PŁATNOŚCI KARTA", confidence: 85 }
];
assert.equal(filterLinesByScope(lines, "nip", "receipt").length, 1);
assert.equal(filterLinesByScope(lines, "tax", "receipt").length, 1);
assert.equal(filterLinesByScope(lines, "total", "receipt").length, 1);
assert.equal(filterLinesByScope(lines, "payment", "receipt").length, 1);

const oldReading = { lines: [{text:"Tea 2,00"},{text:"Bread 4,00"}], text:"Tea 2,00\nBread 4,00" };
const nextReading = { lines: [{text:"Bread 4,00"},{text:"Milk 3,00"}], text:"Bread 4,00\nMilk 3,00" };
const merged = appendReading(oldReading, nextReading, "scanner");
assert.deepEqual(merged.lines.map(item => item.text), ["Tea 2,00", "Bread 4,00", "Milk 3,00"]);
assert.equal(normalizeForComparison("Suma PLN: 9,99"), "suma pln 9 99");
console.log("OCR tests passed.");
