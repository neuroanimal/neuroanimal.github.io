import { DEFAULT_SETTINGS, SETTINGS_KEY, PREVIOUS_SETTINGS_KEY, LEGACY_SETTINGS_KEY, STORAGE_KEY } from "../config.js";

export function loadSettings() {
  try {
    const currentRaw = localStorage.getItem(SETTINGS_KEY);
    const previousRaw = currentRaw ? null : localStorage.getItem(PREVIOUS_SETTINGS_KEY);
    const legacyRaw = currentRaw || previousRaw ? null : localStorage.getItem(LEGACY_SETTINGS_KEY);
    const migratedRaw = previousRaw || legacyRaw;
    const stored = JSON.parse(currentRaw || migratedRaw || "{}");
    const merged = { ...DEFAULT_SETTINGS, ...stored };

    merged.ocrLanguages = Array.isArray(merged.ocrLanguages)
      ? merged.ocrLanguages.filter(lang => ["eng", "pol"].includes(lang))
      : ["pol"];
    if (!merged.ocrLanguages.length) merged.ocrLanguages = ["pol"];

    for (const [key, min, max] of [
      ["motionThreshold", 8, 30], ["stableMs", 500, 3000], ["focusDelayMs", 0, 1800],
      ["penWidthPct", 2, 35], ["penHeightPct", 8, 60],
      ["scannerWidthPct", 70, 100], ["scannerHeightPct", 3, 25],
      ["maxScanDurationSec", 0, 180]
    ]) {
      const value = Number(merged[key]);
      merged[key] = Number.isFinite(value) ? Math.min(max, Math.max(min, value)) : DEFAULT_SETTINGS[key];
    }

    if (previousRaw) {
      // v3 used a horizontal Pen strip and a Scanner narrower than the camera image.
      // Preserve preferences but migrate these four dimensions to the new geometry.
      for (const key of ["penWidthPct", "penHeightPct", "scannerWidthPct", "scannerHeightPct"]) {
        merged[key] = DEFAULT_SETTINGS[key];
      }
    } else if (legacyRaw) {
      // v2 also had short capture defaults; migrate scan timing and geometry safely.
      for (const key of ["motionThreshold", "stableMs", "focusDelayMs", "penWidthPct", "penHeightPct", "scannerWidthPct", "scannerHeightPct", "maxScanDurationSec"]) {
        merged[key] = DEFAULT_SETTINGS[key];
      }
    }

    // Write migrated preferences under the current schema immediately, so future
    // reloads cannot repeatedly revive old dimensions.
    if (migratedRaw) saveSettings(merged);
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
