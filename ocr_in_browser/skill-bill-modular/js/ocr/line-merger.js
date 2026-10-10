import { normalizeForComparison } from "./result-cleanup.js";

export function appendReading(existing, incoming, mode) {
  if (!existing?.lines?.length || mode === "auto") return incoming;
  if (!incoming?.lines?.length) return existing;
  const oldLines = [...existing.lines];
  const newLines = [...incoming.lines];
  const oldKeys = oldLines.map(line => normalizeForComparison(line.text));
  const newKeys = newLines.map(line => normalizeForComparison(line.text));

  // Match only an adjacent suffix/prefix to preserve legitimate repeated products further up a receipt.
  let overlap = 0;
  const max = Math.min(oldKeys.length, newKeys.length, mode === "pen" ? 3 : 8);
  for (let count = max; count > 0; count -= 1) {
    const left = oldKeys.slice(-count).join("\n");
    const right = newKeys.slice(0, count).join("\n");
    if (left && left === right) { overlap = count; break; }
  }
  let additions = newLines.slice(overlap);

  if (mode === "pen" && overlap === 0) {
    // Pen fragments can cut through a word/phrase; reuse the longest trailing word overlap.
    const oldTokens = oldLines.flatMap(line => String(line.text).split(/\s+/)).filter(Boolean);
    const incomingTokens = newLines.flatMap(line => String(line.text).split(/\s+/)).filter(Boolean);
    let tokenOverlap = 0;
    for (let count = Math.min(5, oldTokens.length, incomingTokens.length); count > 0; count -= 1) {
      const a = oldTokens.slice(-count).map(normalizeForComparison).join(" ");
      const b = incomingTokens.slice(0, count).map(normalizeForComparison).join(" ");
      if (a && a === b) { tokenOverlap = count; break; }
    }
    if (tokenOverlap > 0) {
      const remaining = incomingTokens.slice(tokenOverlap).join(" ");
      additions = remaining ? [{ text: remaining, confidence: newLines[0]?.confidence ?? null, words: [], bbox: null }] : [];
    }
  }

  const lines = [...oldLines, ...additions];
  return { ...incoming, lines, text: lines.map(line => line.text).join("\n"), createdAt: incoming.createdAt };
}

