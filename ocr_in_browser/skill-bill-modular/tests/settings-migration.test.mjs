import assert from "node:assert/strict";
import { DEFAULT_SETTINGS, SETTINGS_KEY, PREVIOUS_SETTINGS_KEY, LEGACY_SETTINGS_KEY } from "../js/config.js";
import { loadSettings, saveSettings } from "../js/core/settings-store.js";

function makeStorage(seed = []) {
  const storage = new Map(seed);
  globalThis.localStorage = {
    getItem(key) { return storage.has(key) ? storage.get(key) : null; },
    setItem(key, value) { storage.set(key, String(value)); },
    removeItem(key) { storage.delete(key); }
  };
  return storage;
}

// Legacy v2: retain intentional preferences, reset old scan-tuning defaults.
let storage = makeStorage([[LEGACY_SETTINGS_KEY, JSON.stringify({
  uiLanguage: "pl", scanMode: "scanner", motionThreshold: 14, stableMs: 1250
})]]);
let settings = loadSettings();
assert.equal(settings.uiLanguage, "pl", "keep interface-language preference from v2");
assert.equal(settings.scanMode, "scanner", "keep selected mode from v2");
assert.equal(settings.motionThreshold, DEFAULT_SETTINGS.motionThreshold);
assert.equal(settings.stableMs, DEFAULT_SETTINGS.stableMs);
assert.equal(settings.penWidthPct, 5.5);
assert.equal(settings.penHeightPct, 22);
assert.equal(settings.scannerWidthPct, 100);
assert.equal(settings.scannerHeightPct, 11);
assert.equal(settings.maxScanDurationSec, 0);
assert.ok(storage.has(SETTINGS_KEY), "migrated settings are persisted under the current schema");

// v3: preserve ordinary preferences and timing, migrate only the now-reversed guide geometry.
storage = makeStorage([[PREVIOUS_SETTINGS_KEY, JSON.stringify({
  uiLanguage: "pl", scanMode: "pen", motionThreshold: 14, stableMs: 1250,
  penWidthPct: 62, penHeightPct: 5.5, scannerWidthPct: 92, scannerHeightPct: 11
})]]);
settings = loadSettings();
assert.equal(settings.uiLanguage, "pl");
assert.equal(settings.scanMode, "pen");
assert.equal(settings.motionThreshold, 14);
assert.equal(settings.stableMs, 1250);
assert.equal(settings.penWidthPct, 5.5);
assert.equal(settings.penHeightPct, 22);
assert.equal(settings.scannerWidthPct, 100);

// Save/reload round trip.
settings.scannerWidthPct = 84;
settings.penHeightPct = 30;
assert.equal(saveSettings(settings), true);
const loadedAgain = loadSettings();
assert.equal(loadedAgain.scannerWidthPct, 84);
assert.equal(loadedAgain.penHeightPct, 30);
console.log("Settings migration and persistence tests passed.");
