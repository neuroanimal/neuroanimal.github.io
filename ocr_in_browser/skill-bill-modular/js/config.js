export const SETTINGS_KEY = "skill-bill-modular-settings-v3";
export const LEGACY_SETTINGS_KEY = "skill-bill-modular-settings-v2";
export const STORAGE_KEY = "skill-bill-modular-observations-v2";
export const DEFAULT_SETTINGS = Object.freeze({
  uiLanguage: "en",
  documentOrientation: "auto",
  uiLayout: "auto",
  ocrLanguages: ["pol"],
  documentProfile: "receipt",
  scanMode: "auto",
  scope: "all",
  motionThreshold: 18,
  showRegions: true,
  showLines: true,
  showWords: true,
  showSymbols: true,
  showGuide: false,
  stableMs: 1000,
  focusDelayMs: 500,
  penWidthPct: 62,
  penHeightPct: 5.5,
  scannerWidthPct: 92,
  scannerHeightPct: 11,
  maxScanDurationSec: 0
});

export const MODES = Object.freeze([
  { value: "auto", icon: "◎", titleKey: "modeAuto", descriptionKey: "modeAutoDesc" },
  { value: "scanner", icon: "▤", titleKey: "modeScanner", descriptionKey: "modeScannerDesc" },
  { value: "pen", icon: "✎", titleKey: "modePen", descriptionKey: "modePenDesc" }
]);

export const PROFILES = Object.freeze([
  { value: "receipt", key: "receipt" },
  { value: "flyer", key: "flyer" },
  { value: "book-cover", key: "bookCover" },
  { value: "book-text", key: "bookText" },
  { value: "packaging", key: "packaging" },
  { value: "manual", key: "manual" },
  { value: "bottle", key: "bottle" }
]);

export const SCOPES = Object.freeze([
  { value: "all", icon: "◎", key: "scopeAll", descriptionKey: "scopeAllDesc" },
  { value: "header", icon: "⌃", key: "scopeHeader", descriptionKey: "scopeHeaderDesc" },
  { value: "content", icon: "☷", key: "scopeContent", descriptionKey: "scopeContentDesc" },
  { value: "footer", icon: "⌄", key: "scopeFooter", descriptionKey: "scopeFooterDesc" },
  { value: "nip", icon: "№", key: "scopeNip", descriptionKey: "scopeNipDesc" },
  { value: "items", icon: "▦", key: "scopeItems", descriptionKey: "scopeItemsDesc" },
  { value: "tax", icon: "%", key: "scopeTax", descriptionKey: "scopeTaxDesc" },
  { value: "total", icon: "Σ", key: "scopeTotal", descriptionKey: "scopeTotalDesc" },
  { value: "time", icon: "◷", key: "scopeTime", descriptionKey: "scopeTimeDesc" },
  { value: "place", icon: "⌖", key: "scopePlace", descriptionKey: "scopePlaceDesc" },
  { value: "payment", icon: "¤", key: "scopePayment", descriptionKey: "scopePaymentDesc" }
]);

export const STAGES = Object.freeze([
  { key: "regions", labelKey: "stageRegions", phaseKey: "phaseRegions" },
  { key: "lines", labelKey: "stageLines", phaseKey: "phaseLines" },
  { key: "words", labelKey: "stageWords", phaseKey: "phaseWords" },
  { key: "symbols", labelKey: "stageSymbols", phaseKey: "phaseSymbols" }
]);

export const OCR_SUFFIX_NOISE = /\s+(?:\|\s*[.:;]?|[|¦][.:;]?|o\s*:)\s*$/i;
