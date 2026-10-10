# Browser Camera OCR — modular GitHub Pages prototype

A no-build static prototype for camera access, staged OCR overlays, receipt-oriented OCR cleanup and line accumulation. The app uses HTML/CSS/ES modules plus Tesseract.js from a CDN; it does not require Expo, Flutter, a backend, or an Apple Developer account.

## Publish with GitHub Pages

1. Copy `index.html`, `css/`, and `js/` into the directory published by GitHub Pages (for a project site, paths are intentionally relative).
2. Commit and push the files.
3. Open the published HTTPS URL directly in Safari on iPhone or Chrome/Edge on a laptop.
4. Press the camera icon and allow camera access. Then choose a mode and press the scan icon.

No Node build step is required. ES modules are loaded by the browser directly.

## Modules

- `js/main.js` — application orchestration and action wiring
- `js/config.js`, `js/i18n.js` — settings schema, modes, scopes, translations
- `js/core/camera.js` — camera lifecycle
- `js/core/frame-capture.js` — full-frame capture, configurable centered Pen/Scanner crops and overlay-coordinate correction
- `js/core/motion-detector.js` — lower-sensitivity motion detector, configurable stillness/focus settling, repeated movement-gated capture sessions
- `js/core/settings-store.js` — local settings and saved observation storage
- `js/core/exporter.js` — TXT/TSV/CSV export
- `js/ocr/ocr-engine.js` — Tesseract worker lifecycle
- `js/ocr/result-cleanup.js` — punctuation-artifact cleanup, keyboard/UI spillover filter, confidence and approximate spacing
- `js/ocr/receipt-scope.js` — receipt scope filters and amount-at-right helper
- `js/ocr/line-merger.js` — adjacent-frame overlap detection and Pen-fragment merging
- `js/ui/overlay-renderer.js` — correctly offset OCR bounding-box overlay
- `js/ui/result-renderer.js` — confidence badges and compact OCR output
- `css/tokens.css`, `css/layout.css`, `css/components.css` — design tokens, layout and controls

## Current prototype behaviour

- **Auto** reads one stable full frame, reveals the four overlay stages, then pauses.
- **Scanner** reads a configurable wide, short strip (default 100% width × 11% height), with width configurable up to the full camera image. It keeps running until manually paused or until an optional session time limit is reached.
- **Pen** reads a configurable narrow, tall central strip (default 5.5% width × 22% height) and appends fragments; OCR boxes are shifted back to full-frame coordinates.
- In Scanner/Pen, each successful capture waits for movement before accepting another stable position, avoiding repeated appends of the same stationary frame. Motion is monitored during OCR so movements during processing are not ignored.
- Motion threshold, stillness delay, extra focus-settling time, target widths/heights and optional session limit are configurable in the target/overlay/motion panel. Changes are only committed after pressing **Save**; the button writes to the current versioned `localStorage` settings key and reports a storage error rather than silently closing. A session limit of 0 means unlimited; Scanner/Pen can be stopped with the toolbar pause button.
- Receipt text cleanup removes common trailing OCR debris (e.g. `|`, `|.`, `o:`), normalizes a terminal company suffix such as `S.A.`, and hides obvious low-confidence keyboard-key spillover in receipt mode.
- Confidence is displayed left of each line: green `>=60%`, yellow `40–59%`, red `<40%`, with a zero-padded percentage.
- Rough gaps are reconstructed from word bounding boxes; receipt amount-like suffixes are displayed on the right where detectable.
- Scope selection filters the visible lines; the original full reading remains available for saving/export.
- Saved observations are local to that browser storage. Use export for a portable copy.

## Quick local checks

Settings schema v4 migrates older v2/v3 local preferences. It preserves language/mode preferences while resetting old target geometry to the narrow/tall Pen and full-width Scanner defaults.

Run `npm test` (or the three Node test files directly) to verify OCR cleanup/merging, target cropping geometry and migration of previous settings. No dependency install is required for these checks.

## Known limitations

Receipt classification and field scoping are heuristic, not a certified fiscal parser. Pen is an experimental crop-based reader and does not yet track individual characters between captures. Scanner/Pen work best when the user moves the receipt in short passes and briefly steadies the target; extremely fast continuous motion may still skip rows because OCR needs a sharp frame. OCR language models and Tesseract.js are downloaded from the CDN, so first-run time and offline behaviour depend on browser cache and connectivity.
