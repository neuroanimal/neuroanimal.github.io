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
- `js/core/frame-capture.js` — full-frame capture, Pen crop and overlay-coordinate correction
- `js/core/motion-detector.js` — lower-sensitivity motion detector and stillness trigger
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

- **Auto** reads one stable full frame.
- **Scanner** appends successive full-frame readings; only adjacent suffix/prefix overlap is merged to avoid deleting legitimate repeated receipt rows.
- **Pen** OCRs a central rectangular region and appends fragments; the OCR bounding boxes are shifted back to full-frame coordinates.
- OCR automatically pauses after one capture and the staged overlay sequence. Start another capture after moving the document.
- Receipt text cleanup removes common trailing OCR debris (e.g. `|`, `|.`, `o:`), normalizes a terminal company suffix such as `S.A.`, and hides obvious low-confidence keyboard-key spillover in receipt mode.
- Confidence is displayed left of each line: green `>=60%`, yellow `40–59%`, red `<40%`, with a zero-padded percentage.
- Rough gaps are reconstructed from word bounding boxes; receipt amount-like suffixes are displayed on the right where detectable.
- Scope selection filters the visible lines; the original full reading remains available for saving/export.
- Saved observations are local to that browser storage. Use export for a portable copy.

## Quick local checks

Run `node tests/ocr.test.mjs` to verify OCR cleanup, receipt-price splitting, scope filters and adjacent-frame merging.

## Known limitations

Receipt classification and field scoping are heuristic, not a certified fiscal parser. Pen is an experimental crop-based reader and does not yet track individual characters between captures. OCR language models and Tesseract.js are downloaded from the CDN, so first-run time and offline behaviour depend on browser cache and connectivity.
