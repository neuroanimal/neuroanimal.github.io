const RECEIPT_MARKER = /PARAGON\s*(?:FISKALNY|NIEFISKALNY)|RECEIPT/i;
const FOOTER_MARKER = /SUMA\s+PTU|SUMA\s+PLN|SUMA|RAZEM|DO\s+ZAP[ŁL]ATY|ROZLICZENIE\s+P[ŁL]ATNO[ŚS]CI|P[ŁL]ATNO[ŚS][ĆC]|PTU\s+[A-Z0-9]|SPRZEDA[ŻZ]\s+OPODATKOWANA|PODATEK|VAT/i;
const TAX = /\b(?:PTU|VAT|PODATK|OPODATK|STAWK[AI]|SPRZEDA[ŻZ]\s+OPODATKOWANA)\b/i;
const TOTAL = /\b(?:SUMA|RAZEM|DO\s+ZAP[ŁL]ATY|TOTAL|AMOUNT\s+DUE|SUM)\b/i;
const PAYMENT = /ROZLICZENIE|P[ŁL]ATNO[ŚS]|P[ŁL]ATN|GOT[ÓO]WK|KART[ĄA]|KARTA|CARD|CASH|RESZTA|TRANSAKCJ|VISA|MASTERCARD/i;
const TIME = /\b(?:DATA|GODZ(?:INA)?|CZAS|DATE|TIME|TRANSACTION)\b|\b\d{4}[./-]\d{1,2}[./-]\d{1,2}\b|\b\d{1,2}[./-]\d{1,2}[./-]\d{2,4}\b|\b\d{1,2}:\d{2}(?::\d{2})?\b/i;
const PLACE = /MIEJSCE|INSTALACJI|NIP\b|UL\.|ULICA|AL\.|ALEJA|PL\.|PLAC|ADDRESS|STREET|SPÓ[ŁL]KA|SP\.?\s*Z\.?\s*O\.?\s*O\.?|S\.?A\.?\b|SKLEP|MARKET|STORE/i;
const PRICE_AT_END = /(?:^|\s)(?:-?\d{1,3}(?:[ .]\d{3})*|\d+)[,.]\d{2}\s*(?:PLN|ZŁ|EUR)?\s*$/i;

export function filterLinesByScope(lines, scope, profile = "receipt") {
  if (!Array.isArray(lines) || scope === "all" || !scope) return lines || [];
  if (profile !== "receipt" && ["header", "content", "footer", "nip", "items", "tax", "total", "time", "place", "payment"].includes(scope)) {
    return lines.filter(line => matchField(line.text, scope));
  }
  if (["nip", "items", "tax", "total", "time", "place", "payment"].includes(scope)) {
    return lines.filter(line => matchField(line.text, scope));
  }

  const texts = lines.map(line => line.text || "");
  const marker = texts.findIndex(text => RECEIPT_MARKER.test(text));
  const footerStart = texts.findIndex((text, index) => index > Math.max(-1, marker) && FOOTER_MARKER.test(text));

  if (scope === "header") {
    const end = marker >= 0 ? marker : Math.max(1, Math.ceil(lines.length * 0.3));
    return lines.slice(0, end);
  }
  if (scope === "content") {
    const start = marker >= 0 ? marker + 1 : 0;
    const end = footerStart >= 0 ? footerStart : lines.length;
    return lines.slice(start, Math.max(start, end)).filter(line => !FOOTER_MARKER.test(line.text));
  }
  if (scope === "footer") {
    const start = footerStart >= 0 ? footerStart : Math.max(0, lines.length - Math.max(3, Math.ceil(lines.length * 0.25)));
    return lines.slice(start);
  }
  return lines;
}

function matchField(text, scope) {
  const value = String(text || "");
  switch (scope) {
    case "nip": return /\bNIP\b/i.test(value) || /\b\d{3}[- ]?\d{2,3}[- ]?\d{2,3}[- ]?\d{2,4}\b/.test(value);
    case "items": return PRICE_AT_END.test(value) && !TOTAL.test(value) && !TAX.test(value) && !PAYMENT.test(value);
    case "tax": return TAX.test(value);
    case "total": return TOTAL.test(value);
    case "time": return TIME.test(value);
    case "place": return PLACE.test(value);
    case "payment": return PAYMENT.test(value);
    case "header": return !RECEIPT_MARKER.test(value) && !FOOTER_MARKER.test(value);
    case "content": return !FOOTER_MARKER.test(value) && !PAYMENT.test(value);
    case "footer": return FOOTER_MARKER.test(value) || PAYMENT.test(value) || TOTAL.test(value);
    default: return true;
  }
}

export function splitReceiptPrice(line) {
  const text = String(line?.text || "");
  const match = text.match(/^(.*?)(?:\s+|\t+)((?:-?\d{1,3}(?:[ .]\d{3})*|\d+)[,.]\d{2})(\s*(?:PLN|ZŁ|EUR))?\s*$/i);
  if (!match || !match[1].trim()) return null;
  const amount = `${match[2]}${match[3] || ""}`.trim();
  return { label: match[1].trim(), price: amount };
}
