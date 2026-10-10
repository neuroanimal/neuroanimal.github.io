import { DEFAULT_SETTINGS, SETTINGS_KEY, LEGACY_SETTINGS_KEY, STORAGE_KEY } from "../config.js";

export function loadSettings() {
  try {
    const currentRaw = localStorage.getItem(SETTINGS_KEY);
    const legacyRaw = currentRaw ? null : localStorage.getItem(LEGACY_SETTINGS_KEY);
    const stored = JSON.parse(currentRaw || legacyRaw || "{}");
    const merged = { ...DEFAULT_SETTINGS, ...stored };
    merged.ocrLanguages = Array.isArray(merged.ocrLanguages)
      ? merged.ocrLanguages.filter(lang => ["eng", "pol"].includes(lang))
      : ["pol"];
    if (!merged.ocrLanguages.length) merged.ocrLanguages = ["pol"];
    if (!Number.isFinite(Number(merged.motionThreshold))) merged.motionThreshold = DEFAULT_SETTINGS.motionThreshold;
    if (!Number.isFinite(Number(merged.stableMs))) merged.stableMs = DEFAULT_SETTINGS.stableMs;

    // The previous prototype stopped after one short capture and used an oversized Pen target.
    // Carry forward language/layout/profile preferences, but migrate scan tuning to safer defaults once.
    if (!currentRaw && legacyRaw) {
      for (const key of ["motionThreshold", "stableMs", "focusDelayMs", "penWidthPct", "penHeightPct", "scannerWidthPct", "scannerHeightPct", "maxScanDurationSec"]) {
        merged[key] = DEFAULT_SETTINGS[key];
      }
    }
    return merged;
  } catch {
    return { ...DEFAULT_SETTINGS, ocrLanguages: [...DEFAULT_SETTINGS.ocrLanguages] };
  }
}

export function saveSettings(settings) {
  try { localStorage.setItem(SETTINGS_KEY, JSON.stringify(settings)); return true; }
  catch { return false; }
}

export function loadObservations() {
  try {
    const value = JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]");
    return Array.isArray(value) ? value : [];
  } catch { return []; }
}

export function persistObservations(observations) {
  try { localStorage.setItem(STORAGE_KEY, JSON.stringify(observations)); return true; }
  catch { return false; }
}

export function clearPersistedObservations() {
  try { localStorage.removeItem(STORAGE_KEY); return true; }
  catch { return false; }
}
