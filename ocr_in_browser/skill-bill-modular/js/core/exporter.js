export function exportObservations(observations, format = "txt", language = "en") {
  if (!observations?.length) return false;
  const now = new Date().toISOString().slice(0, 10);
  let content = "";
  let mime = "text/plain;charset=utf-8";
  let extension = "txt";

  if (format === "csv" || format === "tsv") {
    const delimiter = format === "csv" ? "," : "\t";
    const rows = [["capture", "saved_at", "line", "confidence"]];
    observations.forEach((observation, index) => {
      const lines = observation.lines?.length ? observation.lines : String(observation.text || "").split(/\r?\n/).map(text => ({ text, confidence: null }));
      lines.forEach(line => rows.push([
        index + 1,
        observation.savedAt || "",
        typeof line === "string" ? line : line.text || "",
        typeof line === "string" || line.confidence == null ? "" : Math.round(line.confidence)
      ]));
    });
    content = rows.map(row => row.map(value => escapeCell(value, delimiter)).join(delimiter)).join("\r\n");
    mime = format === "csv" ? "text/csv;charset=utf-8" : "text/tab-separated-values;charset=utf-8";
    extension = format;
  } else {
    content = observations.map((observation, index) => {
      const stamp = observation.savedAt ? new Date(observation.savedAt).toLocaleString(language === "pl" ? "pl-PL" : "en-US") : "";
      return `===== FRAGMENT ${index + 1} · ${stamp} =====\n${observation.text || ""}`;
    }).join("\n\n");
  }

  const blob = new Blob(["\uFEFF", content, "\n"], { type: mime });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `ocr-observations-${now}.${extension}`;
  document.body.appendChild(link);
  link.click();
  link.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
  return true;
}

function escapeCell(value, delimiter) {
  const text = String(value ?? "");
  const requiresQuotes = text.includes(delimiter) || /["\r\n]/.test(text) || (delimiter === "\t" && text.includes("\t"));
  return requiresQuotes ? `"${text.replace(/"/g, '""')}"` : text;
}
