import { filterLinesByScope, splitReceiptPrice } from "../ocr/receipt-scope.js";

export function renderCurrentReading(container, countElement, noteElement, reading, { scope = "all", profile = "receipt", tr, scopeLabel = "All text" } = {}) {
  container.replaceChildren();
  const allLines = reading?.lines || [];
  const lines = filterLinesByScope(allLines, scope, profile);
  countElement.textContent = String(lines.length);

  if (!lines.length) {
    const empty = document.createElement("p");
    empty.className = "empty";
    empty.textContent = reading?.lines?.length ? tr("scopeEmpty") : tr("noText");
    container.appendChild(empty);
    noteElement.textContent = reading?.lines?.length ? `${tr("selectedScope")}: ${scopeLabel}` : tr("resultHint");
    return;
  }

  for (const line of lines) {
    const row = document.createElement("div");
    row.className = "ocr-line";
    const confidence = document.createElement("span");
    const score = line.confidence == null ? null : Math.round(line.confidence);
    confidence.className = `confidence-badge ${score == null ? "medium" : score >= 60 ? "high" : score < 40 ? "low" : "medium"}`;
    confidence.textContent = score == null ? "—%" : `${String(Math.max(0, Math.min(100, score))).padStart(2, "0")}%`;
    confidence.title = score == null ? "Confidence unavailable" : `OCR confidence: ${score}%`;
    row.appendChild(confidence);

    const content = document.createElement("div");
    content.className = "ocr-text";
    const price = profile === "receipt" ? splitReceiptPrice(line) : null;
    if (price) {
      content.classList.add("receipt-line");
      const label = document.createElement("span"); label.className = "receipt-label"; label.textContent = price.label;
      const amount = document.createElement("span"); amount.className = "receipt-price"; amount.textContent = price.price;
      content.append(label, amount);
    } else {
      content.textContent = line.text;
    }
    row.appendChild(content);
    container.appendChild(row);
  }

  const scanTime = reading?.createdAt ? new Date(reading.createdAt).toLocaleTimeString() : "";
  noteElement.textContent = `${lines.length} ${lines.length === 1 ? tr("line") : tr("lines")} · ${scopeLabel}${scanTime ? ` · ${scanTime}` : ""}`;
}

export function renderSavedObservations(container, countElement, observations, tr) {
  countElement.textContent = observations.length === 0
    ? tr("savedCount0")
    : observations.length === 1
      ? tr("savedCountOne")
      : `${observations.length} ${tr("savedCountMany")}`;
  container.replaceChildren();
  if (!observations.length) {
    const empty = document.createElement("p"); empty.className = "empty"; empty.textContent = tr("savedEmpty"); container.appendChild(empty); return;
  }
  observations.slice().reverse().forEach((observation, reverseIndex) => {
    const item = document.createElement("div"); item.className = "saved-item";
    const head = document.createElement("div"); head.className = "saved-head";
    const title = document.createElement("div"); title.className = "saved-title";
    title.textContent = `#${observations.length - reverseIndex} · ${new Date(observation.savedAt).toLocaleString()}`;
    head.appendChild(title);
    const del = document.createElement("button"); del.type = "button"; del.className = "small-icon-btn danger"; del.textContent = "×"; del.title = tr("deleteOne"); del.setAttribute("aria-label", tr("deleteOne")); del.dataset.deleteObservation = observation.id;
    head.appendChild(del); item.appendChild(head);
    if (observation.overlappingLines?.length) {
      const note = document.createElement("p"); note.className = "saved-note"; note.textContent = `${tr("overlap")}: ${observation.overlappingLines.length}`; item.appendChild(note);
    }
    const details = document.createElement("details"); const summary = document.createElement("summary"); summary.textContent = tr("savedText");
    const pre = document.createElement("pre"); pre.textContent = observation.text; details.append(summary, pre); item.appendChild(details); container.appendChild(item);
  });
}
