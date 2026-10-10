import assert from "node:assert/strict";
import { loadSettings } from "../js/core/settings-store.js";

const storage = new Map([
  ["skill-bill-modular-settings-v2", JSON.stringify({
    uiLanguage: "pl",
    scanMode: "scanner",
    motionThreshold: 14,
    stableMs: 1250
  })]
]);
globalThis.localStorage = {
  getItem(key) { return storage.has(key) ? storage.get(key) : null; },
  setItem(key, value) { storage.set(key, String(value)); },
  removeItem(key) { storage.delete(key); }
};

const settings = loadSettings();
assert.equal(settings.uiLanguage, "pl", "keep interface-language preference from v2");
assert.equal(settings.scanMode, "scanner", "keep selected mode from v2");
assert.equal(settings.motionThreshold, 18, "migrate to the less-sensitive motion threshold");
assert.equal(settings.stableMs, 1000, "migrate to the new stillness default");
assert.equal(settings.penHeightPct, 5.5);
assert.equal(settings.scannerHeightPct, 11);
assert.equal(settings.maxScanDurationSec, 0, "default to an unlimited scanner session");
console.log("Settings migration tests passed.");
