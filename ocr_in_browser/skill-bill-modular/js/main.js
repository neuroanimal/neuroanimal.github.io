import { DEFAULT_SETTINGS, MODES, PROFILES, SCOPES, STAGES } from "./config.js";
import { translator } from "./i18n.js";
import { CameraController } from "./core/camera.js";
import { MotionDetector } from "./core/motion-detector.js";
import { loadSettings, saveSettings, loadObservations, persistObservations, clearPersistedObservations } from "./core/settings-store.js";
import { exportObservations } from "./core/exporter.js";
import { OcrEngine } from "./ocr/ocr-engine.js";
import { normalizeForComparison } from "./ocr/result-cleanup.js";
import { filterLinesByScope } from "./ocr/receipt-scope.js";
import { appendReading } from "./ocr/line-merger.js";
import { captureFrame, cropTarget, translateBoundingBoxes } from "./core/frame-capture.js";
import { OverlayRenderer } from "./ui/overlay-renderer.js";
import { renderCurrentReading, renderSavedObservations } from "./ui/result-renderer.js";

const $ = (id) => document.getElementById(id);
const elements = {
  video: $("camera"), stage: $("cameraStage"), overlay: $("overlay"), status: $("status"), stability: $("stabilityLabel"), motion: $("motionLabel"), meter: $("stabilityMeter"),
  cameraState: $("cameraState"), cameraLed: $("cameraLed"), modeState: $("modeState"), scopeState: $("scopeState"), currentLines: $("currentLines"), lineCount: $("lineCount"), resultsNote: $("resultsNote"),
  readingMeta: $("readingMeta"), saveReading: $("saveReading"), savedCount: $("savedCount"), savedList: $("savedList"), exportSaved: $("exportSaved"), clearSaved: $("clearSaved"),
  popover: $("popover"), backdrop: $("popoverBackdrop"), popoverTitle: $("popoverTitle"), popoverDescription: $("popoverDescription"), popoverBody: $("popoverBody"), popoverFooter: $("popoverFooter")
};

const settings = { ...loadSettings() };
const camera = new CameraController(elements.video, { onChange: updateCameraUI });
const detector = new MotionDetector(elements.video);
const ocr = new OcrEngine();
const overlay = new OverlayRenderer(elements.video, elements.overlay, elements.stage);
let currentData = null;
let currentReading = null;
let scannerBuffer = null;
let savedObservations = loadObservations();
let scanning = false;
let scanInFlight = false;
let stageRunId = 0;
let activePopover = null;
let draft = null;
let pendingScope = settings.scope || "all";
let exportFormat = "txt";
let scanLimitTimer = null;
let frameMovedDuringCapture = false;

const tr = (key) => translator(settings.uiLanguage)(key);

bindEvents();
applySettingsToDom();
renderEverything();
setStatus(tr("ready"));

function bindEvents() {
  document.querySelectorAll("[data-menu]").forEach(button => button.addEventListener("click", () => openPopover(button.dataset.menu)));
  document.querySelectorAll("[data-scope]").forEach(button => button.addEventListener("click", () => openScopePopover(button.dataset.scope)));
  $("closePopover").addEventListener("click", closePopover);
  elements.backdrop.addEventListener("click", closePopover);
  document.addEventListener("keydown", event => { if (event.key === "Escape" && activePopover) closePopover(); });
  elements.popoverFooter.addEventListener("click", handlePopoverAction);
  elements.popoverBody.addEventListener("click", handlePopoverAction);
  elements.popoverBody.addEventListener("change", updateDraftFromInput);
  elements.popoverBody.addEventListener("input", event => { if (event.target.type === "range") updateDraftFromInput(event); });
  $("copyReading").addEventListener("click", () => openPopover("copy"));
  $("clearResults").addEventListener("click", () => openPopover("clear-results"));
  elements.saveReading.addEventListener("click", () => openPopover("save"));
  elements.exportSaved.addEventListener("click", () => openPopover("saved"));
  elements.clearSaved.addEventListener("click", () => openPopover("saved"));
  elements.savedList.addEventListener("click", event => {
    const button = event.target.closest("[data-delete-observation]");
    if (button) deleteObservation(button.dataset.deleteObservation);
  });
  window.addEventListener("resize", () => { overlay.draw(); updateImageGuides(); });
  elements.video.addEventListener("loadedmetadata", updateImageGuides);
  document.addEventListener("visibilitychange", () => {
    if (document.hidden && scanning) {
      pauseScanning();
      setStatus(settings.uiLanguage === "pl" ? "Pauza — strona jest w tle." : "Paused — page is in the background.");
    }
  });
}

function updateCameraUI(isOn = camera.isOn) {
  $("cameraMenuBtn").classList.toggle("active", isOn);
  elements.cameraLed.classList.toggle("on", isOn);
  elements.cameraState.textContent = isOn ? tr("cameraReady") : tr("cameraOff");
  if (!isOn && scanning) pauseScanning();
}

function setStatus(message) {
  elements.status.textContent = message;
  elements.status.title = message;
}

function applySettingsToDom() {
  document.documentElement.lang = settings.uiLanguage;
  document.body.dataset.uiLanguage = settings.uiLanguage;
  document.body.dataset.uiLayout = settings.uiLayout;
  document.body.dataset.documentOrientation = settings.documentOrientation;
  elements.stage.dataset.documentOrientation = settings.documentOrientation;
  elements.stage.dataset.mode = settings.scanMode;
  elements.stage.dataset.guide = String(Boolean(settings.showGuide));
  requestAnimationFrame(updateImageGuides);

  $("cameraMenuBtn").title = tr("camera");
  $("modeMenuBtn").title = tr("mode");
  $("modeMenuBtn").textContent = MODES.find(mode => mode.value === settings.scanMode)?.icon || "◎";
  $("modeMenuBtn").classList.toggle("active", settings.scanMode !== "auto");
  $("scanMenuBtn").title = scanning ? tr("pauseScan") : tr("startScan");
  $("scanMenuBtn").textContent = scanning ? "Ⅱ" : "▶";
  $("scanMenuBtn").classList.toggle("active", scanning);
  $("documentMenuBtn").title = tr("document");
  $("documentMenuBtn").textContent = settings.documentOrientation === "portrait" ? "▯" : "▭";
  $("documentMenuBtn").classList.toggle("active", settings.documentOrientation !== "auto");
  $("layoutMenuBtn").title = tr("layout");
  $("layoutMenuBtn").textContent = settings.uiLayout === "vertical" ? "↕" : "↔";
  $("layoutMenuBtn").classList.toggle("active", settings.uiLayout !== "auto");
  $("uiLanguageBtn").title = tr("uiLanguage");
  $("uiLanguageBtn").textContent = settings.uiLanguage === "pl" ? "🇵🇱" : "🇬🇧";
  $("ocrLanguageBtn").title = tr("ocrLanguage");
  $("ocrLanguageBtn").textContent = settings.ocrLanguages.length > 1 ? "A文" : settings.ocrLanguages[0] === "eng" ? "A" : "文";
  $("layersMenuBtn").title = tr("layers");
  $("profileMenuBtn").title = tr("profile");
  $("helpMenuBtn").title = tr("help");
  $("copyReading").title = tr("copy");
  $("clearResults").title = tr("clearResults");
  $("savedMenuBtn").title = tr("saved");
  $("closePopover").title = tr("close");
  elements.readingMeta.textContent = tr("currentResult");
  document.querySelector(".scope-caption").textContent = tr("scope");
  elements.cameraState.textContent = camera.isOn ? tr("cameraReady") : tr("cameraOff");
  elements.modeState.textContent = tr(MODES.find(mode => mode.value === settings.scanMode)?.titleKey || "modeAuto");
  elements.scopeState.textContent = tr(SCOPES.find(scope => scope.value === settings.scope)?.key || "scopeAll");
  document.querySelectorAll("[data-scope]").forEach(button => {
    const active = button.dataset.scope === settings.scope;
    button.classList.toggle("active", active);
    button.setAttribute("aria-pressed", String(active));
    const scope = SCOPES.find(item => item.value === button.dataset.scope);
    if (scope) { button.title = tr(scope.key); button.setAttribute("aria-label", tr(scope.key)); }
  });
  overlay.setOptions({ showRegions: settings.showRegions, showLines: settings.showLines, showWords: settings.showWords, showSymbols: settings.showSymbols });
  renderCurrent();
  renderSaved();
  if (activePopover) openPopover(activePopover, { keepDraft: true });
}

function renderEverything() {
  applySettingsToDom();
  elements.saveReading.disabled = !currentReading?.text?.trim();
  elements.exportSaved.disabled = savedObservations.length === 0;
  elements.clearSaved.disabled = savedObservations.length === 0;
  elements.clearSaved.title = tr("clearSaved");
}

function renderCurrent() {
  const scopeItem = SCOPES.find(item => item.value === settings.scope);
  renderCurrentReading(elements.currentLines, elements.lineCount, elements.resultsNote, currentReading, {
    scope: settings.scope, profile: settings.documentProfile, tr, scopeLabel: tr(scopeItem?.key || "scopeAll")
  });
  elements.saveReading.disabled = !filterLinesByScope(currentReading?.lines || [], settings.scope, settings.documentProfile).length;
}

function renderSaved() {
  renderSavedObservations(elements.savedList, elements.savedCount, savedObservations, tr);
  elements.exportSaved.disabled = savedObservations.length === 0;
  elements.clearSaved.disabled = savedObservations.length === 0;
}

function openScopePopover(scopeValue) {
  pendingScope = scopeValue;
  openPopover("scope", { scopeValue });
}

function openPopover(name, extra = {}) {
  const keepDraft = extra.keepDraft === true && name === activePopover && draft;
  activePopover = name;
  if (!keepDraft) draft = { ...settings, ocrLanguages: [...settings.ocrLanguages], pendingScope: extra.scopeValue || settings.scope, exportFormat };
  elements.popoverTitle.textContent = popoverTitle(name, extra);
  elements.popoverDescription.textContent = popoverDescription(name, extra);
  elements.popoverBody.replaceChildren();
  elements.popoverFooter.replaceChildren();

  switch (name) {
    case "camera": renderCameraMenu(); break;
    case "mode": renderModeMenu(); break;
    case "scan": renderScanMenu(); break;
    case "document": renderRadioMenu("documentOrientation", [{ value: "auto", key: "auto" }, { value: "portrait", key: "portrait" }, { value: "landscape", key: "landscape" }]); break;
    case "layout": renderRadioMenu("uiLayout", [{ value: "auto", key: "auto" }, { value: "vertical", key: "vertical" }, { value: "horizontal", key: "horizontal" }]); break;
    case "ui-language": renderRadioMenu("uiLanguage", [{ value: "en", label: "🇬🇧 English" }, { value: "pl", label: "🇵🇱 Polski" }]); break;
    case "ocr-language": renderOcrLanguages(); break;
    case "layers": renderLayerSettings(); break;
    case "profile": renderProfileMenu(); break;
    case "help": renderHelpMenu(); break;
    case "scope": renderScopeMenu(extra.scopeValue || settings.scope); break;
    case "save": renderSaveMenu(); break;
    case "saved": renderSavedMenu(); break;
    case "copy": renderCopyMenu(); break;
    case "clear-results": renderClearResultsMenu(); break;
    default: renderHelpMenu(); break;
  }
  elements.backdrop.hidden = false;
  elements.popover.hidden = false;
}

function popoverTitle(name, extra) {
  if (name === "scope") return tr(SCOPES.find(item => item.value === (extra.scopeValue || pendingScope || settings.scope))?.key || "scopeAll");
  const keys = { "ui-language": "uiLanguage", "ocr-language": "ocrLanguage", "clear-results": "clearResults" };
  return tr(keys[name] || name);
}

function popoverDescription(name, extra) {
  if (name === "scope") return `${tr("scopeDesc")} ${tr(SCOPES.find(item => item.value === (extra.scopeValue || pendingScope || settings.scope))?.descriptionKey || "scopeAllDesc")}`;
  const keys = {
    camera: "cameraDesc", mode: MODES.find(item => item.value === settings.scanMode)?.descriptionKey || "modeAutoDesc", scan: "scanDesc",
    document: "documentDesc", layout: "layoutDesc", "ui-language": "uiLanguageDesc", "ocr-language": "ocrLanguageDesc", layers: "layersDesc", profile: "profileDesc",
    help: "helpDesc", save: "saveDesc", saved: "savedDesc", copy: "copyDesc", "clear-results": "confirmClear"
  };
  return tr(keys[name] || "helpDesc");
}

function addNote(text) {
  const node = document.createElement("p"); node.className = "popover-note"; node.textContent = text; elements.popoverBody.appendChild(node); return node;
}
function addButton(parent, label, action, style = "") {
  const button = document.createElement("button"); button.type = "button"; button.className = `action-btn ${style}`.trim(); button.dataset.action = action; button.textContent = label; parent.appendChild(button); return button;
}
function addApplyCancel() { addButton(elements.popoverFooter, tr("cancel"), "cancel"); addButton(elements.popoverFooter, tr("apply"), "apply", "primary"); }
function addChoice(setting, value, label, type = "radio", checked = false, description = "") {
  const wrapper = document.createElement("label"); wrapper.className = "choice";
  const input = document.createElement("input"); input.type = type; input.name = setting; input.value = value; input.checked = checked; input.dataset.setting = setting;
  const text = document.createElement("span"); text.textContent = label;
  wrapper.append(input, text);
  if (description) { const small = document.createElement("small"); small.className = "popover-note"; small.textContent = description; wrapper.appendChild(small); }
  elements.popoverBody.appendChild(wrapper);
}
function addSettingRange(setting, label, min, max, step, value, displayValue) {
  const wrap = document.createElement("label"); wrap.className = "range-row";
  const text = document.createElement("span"); text.textContent = label;
  const input = document.createElement("input"); input.type = "range"; input.min = String(min); input.max = String(max); input.step = String(step); input.value = String(value); input.dataset.setting = setting;
  const output = document.createElement("output"); output.dataset.output = setting; output.textContent = displayValue ?? String(value);
  wrap.append(text, input, output); elements.popoverBody.appendChild(wrap);
}

function renderCameraMenu() {
  addNote(camera.isOn ? tr("cameraReady") : tr("cameraOff"));
  addButton(elements.popoverFooter, camera.isOn ? tr("stopCamera") : tr("startCamera"), camera.isOn ? "stop-camera" : "start-camera", "primary");
}
function renderModeMenu() {
  MODES.forEach(mode => addChoice("scanMode", mode.value, `${mode.icon}  ${tr(mode.titleKey)}`, "radio", draft.scanMode === mode.value, tr(mode.descriptionKey)));
  addApplyCancel();
}
function renderScanMenu() {
  addNote(camera.isOn ? (scanning ? tr("waitingStill") : tr("scanDesc")) : tr("cameraRequired"));
  addButton(elements.popoverFooter, scanning ? tr("pauseScan") : tr("startScan"), scanning ? "pause-scan" : "start-scan", "primary");
}
function renderRadioMenu(setting, options) {
  options.forEach(option => addChoice(setting, option.value, option.label || tr(option.key), "radio", draft[setting] === option.value));
  addApplyCancel();
}
function renderOcrLanguages() {
  addChoice("ocrLanguages", "eng", "English (eng)", "checkbox", draft.ocrLanguages.includes("eng"));
  addChoice("ocrLanguages", "pol", "Polski (pol)", "checkbox", draft.ocrLanguages.includes("pol"));
  addNote(tr("ocrLanguageDesc"));
  addApplyCancel();
}
function renderLayerSettings() {
  addChoice("showRegions", "true", tr("regions"), "checkbox", Boolean(draft.showRegions));
  addChoice("showLines", "true", tr("lines"), "checkbox", Boolean(draft.showLines));
  addChoice("showWords", "true", tr("words"), "checkbox", Boolean(draft.showWords));
  addChoice("showSymbols", "true", tr("symbols"), "checkbox", Boolean(draft.showSymbols));
  addChoice("showGuide", "true", tr("guide"), "checkbox", Boolean(draft.showGuide));
  addSettingRange("motionThreshold", tr("motion"), 8, 30, 1, draft.motionThreshold, formatRangeValue("motionThreshold", draft.motionThreshold));
  addSettingRange("stableMs", tr("stableTime"), 500, 3000, 100, draft.stableMs, formatRangeValue("stableMs", draft.stableMs));
  addSettingRange("focusDelayMs", tr("focusDelay"), 0, 1800, 100, draft.focusDelayMs, formatRangeValue("focusDelayMs", draft.focusDelayMs));
  addSettingRange("penWidthPct", tr("penWidth"), 2, 35, 0.5, draft.penWidthPct, formatRangeValue("penWidthPct", draft.penWidthPct));
  addSettingRange("penHeightPct", tr("penHeight"), 8, 60, 1, draft.penHeightPct, formatRangeValue("penHeightPct", draft.penHeightPct));
  addSettingRange("scannerWidthPct", tr("scannerWidth"), 70, 100, 1, draft.scannerWidthPct, formatRangeValue("scannerWidthPct", draft.scannerWidthPct));
  addSettingRange("scannerHeightPct", tr("scannerHeight"), 3, 25, 0.5, draft.scannerHeightPct, formatRangeValue("scannerHeightPct", draft.scannerHeightPct));
  addSettingRange("maxScanDurationSec", tr("maxScanDuration"), 0, 180, 15, draft.maxScanDurationSec, formatRangeValue("maxScanDurationSec", draft.maxScanDurationSec));
  addNote(tr("layersDesc"));
  addButton(elements.popoverFooter, tr("cancel"), "cancel");
  addButton(elements.popoverFooter, tr("saveSettings"), "save-settings", "primary");
}
function renderProfileMenu() {
  PROFILES.forEach(profile => addChoice("documentProfile", profile.value, tr(profile.key), "radio", draft.documentProfile === profile.value));
  addApplyCancel();
}
function renderScopeMenu(scopeValue) {
  pendingScope = scopeValue;
  SCOPES.forEach(scope => addChoice("pendingScope", scope.value, `${scope.icon}  ${tr(scope.key)}`, "radio", scopeValue === scope.value));
  addButton(elements.popoverFooter, tr("cancel"), "cancel");
  addButton(elements.popoverFooter, tr("setScope"), "apply-scope", "primary");
}
function renderHelpMenu() {
  addNote(tr("helpDesc"));
  addNote(tr("cameraPermissionNote"));
  addButton(elements.popoverFooter, tr("close"), "cancel", "primary");
}
function renderCopyMenu() { addButton(elements.popoverFooter, tr("cancel"), "cancel"); addButton(elements.popoverFooter, tr("copy"), "copy-reading", "primary"); }
function renderClearResultsMenu() { addButton(elements.popoverFooter, tr("cancel"), "cancel"); addButton(elements.popoverFooter, tr("yesClear"), "clear-results", "danger"); }
function renderSaveMenu() { addNote(tr("saveDesc")); addButton(elements.popoverFooter, tr("cancel"), "cancel"); addButton(elements.popoverFooter, tr("saveFragment"), "save-current", "primary"); }
function renderSavedMenu() {
  addNote(tr("savedDesc"));
  const formatWrap = document.createElement("label"); formatWrap.className = "choice";
  const label = document.createElement("span"); label.textContent = `${tr("format")}:`;
  const select = document.createElement("select"); select.className = "select-control"; select.dataset.setting = "exportFormat";
  [{value:"txt",key:"text"},{value:"tsv",key:"tsv"},{value:"csv",key:"csv"}].forEach(option => { const node=document.createElement("option"); node.value=option.value; node.textContent=tr(option.key); node.selected=exportFormat===option.value; select.appendChild(node); });
  formatWrap.append(label,select); elements.popoverBody.appendChild(formatWrap);
  addButton(elements.popoverFooter, tr("cancel"), "cancel");
  const exportButton = addButton(elements.popoverFooter, tr("export"), "export-saved", "primary"); exportButton.disabled = savedObservations.length === 0;
  const clearButton = addButton(elements.popoverFooter, tr("clearSaved"), "clear-saved", "danger"); clearButton.disabled = savedObservations.length === 0;
}

function formatRangeValue(setting, value) {
  const number = Number(value);
  if (setting === "stableMs" || setting === "focusDelayMs") return `${(number / 1000).toFixed(1)} s`;
  if (setting === "penWidthPct" || setting === "penHeightPct" || setting === "scannerWidthPct" || setting === "scannerHeightPct") return `${number.toFixed(number % 1 ? 1 : 0)}%`;
  if (setting === "maxScanDurationSec") return number === 0 ? tr("unlimited") : `${number} s`;
  return number.toFixed(1);
}

function updateDraftFromInput(event) {
  const input = event.target;
  if (!input?.dataset?.setting || !draft) return;
  const setting = input.dataset.setting;
  if (setting === "ocrLanguages") {
    draft.ocrLanguages = [...elements.popoverBody.querySelectorAll('input[data-setting="ocrLanguages"]:checked')].map(item => item.value);
  } else if (input.type === "checkbox") {
    draft[setting] = input.checked;
  } else if (input.tagName === "SELECT") {
    if (setting === "exportFormat") { exportFormat = input.value; draft.exportFormat = input.value; }
  } else {
    draft[setting] = input.value;
  }
  const output = elements.popoverBody.querySelector(`[data-output="${setting}"]`);
  if (output) output.textContent = formatRangeValue(setting, input.value);
}

async function handlePopoverAction(event) {
  const button = event.target.closest("[data-action]");
  if (!button) return;
  const action = button.dataset.action;
  if (action === "cancel") { closePopover(); return; }
  if (action === "apply") { if (applyDraft()) closePopover(); return; }
  if (action === "save-settings") { if (applyDraft()) closePopover(); return; }
  if (action === "apply-scope") {
    const selected = elements.popoverBody.querySelector('input[data-setting="pendingScope"]:checked');
    settings.scope = selected?.value || pendingScope || "all";
    saveSettings(settings); applySettingsToDom(); closePopover(); return;
  }
  if (action === "start-camera") {
    closePopover(); setStatus(settings.uiLanguage === "pl" ? "Uruchamianie aparatu…" : "Starting camera…");
    try { await camera.start(); setStatus(tr("cameraReady")); updateCameraUI(); requestAnimationFrame(updateImageGuides); }
    catch (error) { setStatus(`${tr("cameraFailed")}: ${error.message || tr("unknown")}`); }
    return;
  }
  if (action === "stop-camera") { pauseScanning(); camera.stop(); setStatus(tr("cameraOff")); closePopover(); return; }
  if (action === "start-scan") { closePopover(); startScanning(); return; }
  if (action === "pause-scan") { pauseScanning(); setStatus(tr("scanPaused")); closePopover(); return; }
  if (action === "toggle-scan") { closePopover(); scanning ? pauseScanning() : startScanning(); return; }
  if (action === "copy-reading") { closePopover(); await copyCurrentReading(); return; }
  if (action === "clear-results") { clearCurrentResults(); closePopover(); return; }
  if (action === "save-current") { saveCurrentObservation(); closePopover(); return; }
  if (action === "export-saved") { exportObservations(savedObservations, exportFormat, settings.uiLanguage); closePopover(); return; }
  if (action === "clear-saved") { clearSavedConfirmation(); return; }
}

function applyDraft() {
  if (!draft) return false;
  const previousMode = settings.scanMode;
  const previousLanguage = settings.uiLanguage;
  const allowedLanguages = (draft.ocrLanguages || settings.ocrLanguages).filter(language => ["eng", "pol"].includes(language));
  const { pendingScope: _pendingScope, exportFormat: _format, ...changes } = draft;
  const nextSettings = { ...settings, ...changes };
  nextSettings.ocrLanguages = allowedLanguages.length ? allowedLanguages : ["pol"];
  nextSettings.motionThreshold = clampNumber(nextSettings.motionThreshold, 8, 30, DEFAULT_SETTINGS.motionThreshold);
  nextSettings.stableMs = clampNumber(nextSettings.stableMs, 500, 3000, DEFAULT_SETTINGS.stableMs);
  nextSettings.focusDelayMs = clampNumber(nextSettings.focusDelayMs, 0, 1800, DEFAULT_SETTINGS.focusDelayMs);
  nextSettings.penWidthPct = clampNumber(nextSettings.penWidthPct, 2, 35, DEFAULT_SETTINGS.penWidthPct);
  nextSettings.penHeightPct = clampNumber(nextSettings.penHeightPct, 8, 60, DEFAULT_SETTINGS.penHeightPct);
  nextSettings.scannerWidthPct = clampNumber(nextSettings.scannerWidthPct, 70, 100, DEFAULT_SETTINGS.scannerWidthPct);
  nextSettings.scannerHeightPct = clampNumber(nextSettings.scannerHeightPct, 3, 25, DEFAULT_SETTINGS.scannerHeightPct);
  nextSettings.maxScanDurationSec = clampNumber(nextSettings.maxScanDurationSec, 0, 180, DEFAULT_SETTINGS.maxScanDurationSec);

  // Persist first. Do not close the panel or silently pretend settings were saved
  // when this browser refuses localStorage writes.
  if (!saveSettings(nextSettings)) {
    setStatus(tr("settingsSaveFailed"));
    return false;
  }

  Object.assign(settings, nextSettings);
  if (previousMode !== settings.scanMode) scannerBuffer = null;
  if (previousLanguage !== settings.uiLanguage) setStatus(tr(scanning ? "waitingStill" : camera.isOn ? "cameraReady" : "ready"));
  else setStatus(tr("settingsSaved"));
  overlay.setOptions({ showRegions: settings.showRegions, showLines: settings.showLines, showWords: settings.showWords, showSymbols: settings.showSymbols });
  // Synchronize the draft before the panel is re-rendered by applySettingsToDom().
  draft = { ...settings, ocrLanguages: [...settings.ocrLanguages], pendingScope: settings.scope, exportFormat };
  applySettingsToDom();
  return true;
}

function closePopover() {
  activePopover = null; draft = null;
  elements.popover.hidden = true; elements.backdrop.hidden = true;
}

function updateImageGuides() {
  const video = elements.video;
  const stage = elements.stage;
  if (!video.videoWidth || !video.videoHeight) return;
  const videoRect = video.getBoundingClientRect();
  const stageRect = stage.getBoundingClientRect();
  if (!videoRect.width || !videoRect.height || !stageRect.width || !stageRect.height) return;
  const scale = Math.min(videoRect.width / video.videoWidth, videoRect.height / video.videoHeight);
  const imageWidth = video.videoWidth * scale;
  const imageHeight = video.videoHeight * scale;
  const imageLeft = videoRect.left - stageRect.left + (videoRect.width - imageWidth) / 2;
  const imageTop = videoRect.top - stageRect.top + (videoRect.height - imageHeight) / 2;
  const centerX = imageLeft + imageWidth / 2;
  const centerY = imageTop + imageHeight / 2;
  const guide = $("documentGuide");
  const target = $("scanGuide");
  guide.style.left = `${centerX}px`; guide.style.top = `${centerY}px`;
  const guideSize = settings.documentOrientation === "portrait" ? [0.47, 0.84] : settings.documentOrientation === "landscape" ? [0.84, 0.55] : [0.66, 0.76];
  guide.style.width = `${imageWidth * guideSize[0]}px`;
  guide.style.height = `${imageHeight * guideSize[1]}px`;
  target.style.left = `${centerX}px`; target.style.top = `${centerY}px`;
  const mode = settings.scanMode;
  const targetWidth = mode === "scanner" ? settings.scannerWidthPct : settings.penWidthPct;
  const targetHeight = mode === "scanner" ? settings.scannerHeightPct : settings.penHeightPct;
  target.style.width = `${imageWidth * Number(targetWidth || 62) / 100}px`;
  target.style.height = `${imageHeight * Number(targetHeight || (mode === "scanner" ? 11 : 5.5)) / 100}px`;
}

function startScanning() {
  if (!camera.isOn) { openPopover("camera"); return; }
  if (scanning || scanInFlight) return;
  scanning = true;
  stageRunId += 1;
  if (scanLimitTimer) clearTimeout(scanLimitTimer);
  scanLimitTimer = null;
  overlay.clear();
  elements.stage.dataset.mode = settings.scanMode;
  applySettingsToDom();
  setStatus(tr("waitingStill"));
  elements.meter.value = 0; elements.stability.textContent = "STB —"; elements.motion.textContent = "MOV —";

  const repeatingMode = settings.scanMode === "scanner" || settings.scanMode === "pen";
  detector.start(() => runOcrCapture(), {
    repeatAfterMovement: repeatingMode,
    getThreshold: () => Number(settings.motionThreshold),
    stableMs: Number(settings.stableMs ?? 1000),
    captureDelayMs: Number(settings.focusDelayMs ?? 500),
    onStatus: status => {
      if (status === "moving" && repeatingMode) {
        if (scanInFlight) frameMovedDuringCapture = true;
        overlay.clear();
      }
      if (!scanning || scanInFlight) return;
      setStatus(tr(status));
    },
    onMetrics: metrics => {
      elements.motion.textContent = `MOV ${Number(metrics.score || 0).toFixed(1)}`;
      elements.meter.value = metrics.stablePercent;
      elements.stability.textContent = metrics.awaitingMovement
        ? (settings.uiLanguage === "pl" ? "PRZESUŃ" : "MOVE")
        : `STB ${(metrics.stableFor / 1000).toFixed(1)}s`;
    },
    onError: error => { setStatus(`${tr("unknown")}: ${error.message || error}`); pauseScanning(); }
  });

  const durationSeconds = Number(settings.maxScanDurationSec || 0);
  if (durationSeconds > 0) {
    scanLimitTimer = setTimeout(() => {
      if (scanning) {
        pauseScanning();
        setStatus(tr("scanLimitReached"));
      }
    }, durationSeconds * 1000);
  }
}

function pauseScanning() {
  scanning = false;
  detector.stop();
  if (scanLimitTimer) clearTimeout(scanLimitTimer);
  scanLimitTimer = null;
  stageRunId += 1;
  elements.meter.value = 0;
  elements.stability.textContent = "STB —";
  elements.motion.textContent = "MOV —";
  applySettingsToDom();
}

async function runOcrCapture() {
  if (!scanning || !camera.isOn || scanInFlight) return;
  scanInFlight = true;
  frameMovedDuringCapture = false;
  const runId = stageRunId;
  const captureMode = settings.scanMode;
  try {
    setStatus(tr("loadingOcr"));
    const frame = captureFrame(elements.video);
    let input = { canvas: frame, offsetX: 0, offsetY: 0 };
    if (captureMode === "pen") {
      input = cropTarget(frame, settings.penWidthPct, settings.penHeightPct);
    } else if (captureMode === "scanner") {
      input = cropTarget(frame, settings.scannerWidthPct, settings.scannerHeightPct);
    }
    const { data, reading } = await ocr.recognize(input.canvas, settings.ocrLanguages, {
      profile: settings.documentProfile,
      onProgress: message => {
        if (message?.status === "recognizing text") setStatus(`${tr("processing")} ${Math.round((message.progress || 0) * 100)}%`);
      }
    });
    if (!scanning || runId !== stageRunId) return;
    if (input.offsetX || input.offsetY) translateBoundingBoxes(data, input.offsetX, input.offsetY);
    currentData = data;
    currentReading = captureMode === "auto" ? reading : appendReading(scannerBuffer, reading, captureMode);
    if (captureMode !== "auto") scannerBuffer = currentReading;
    renderCurrent();
    if (captureMode === "auto" || !frameMovedDuringCapture) {
      overlay.setData(currentData, captureMode === "auto" ? 0 : STAGES.length - 1);
    } else {
      // Never display bounding boxes from an old frame over a camera position that moved during OCR.
      overlay.clear();
    }
    elements.saveReading.disabled = !currentReading.text.trim();

    if (captureMode === "auto") {
      await revealStages(data, runId);
      if (scanning && runId === stageRunId) {
        pauseScanning();
        setStatus(tr("scanDone"));
        elements.stage.dataset.mode = captureMode;
      }
    } else {
      // Scanner/Pen are multi-pass sessions. OCR is triggered once per stable stop,
      // then the detector waits for movement before accepting the next position.
      setStatus(tr("scanAwaitMovement"));
    }
  } catch (error) {
    setStatus(`${tr("scanFailed")}: ${error.message || tr("unknown")}`);
    pauseScanning();
  } finally {
    scanInFlight = false;
  }
}

async function revealStages(data, runId) {
  const holdMs = 520;
  for (let index = 0; index < STAGES.length; index += 1) {
    if (!scanning || runId !== stageRunId) return;
    overlay.setStage(index);
    setStatus(tr(STAGES[index].labelKey));
    await sleep(holdMs);
  }
}

function clearCurrentResults() {
  pauseScanning();
  currentData = null; currentReading = null; scannerBuffer = null;
  overlay.clear();
  renderCurrent();
  elements.saveReading.disabled = true;
  setStatus(tr("cleared"));
}

async function copyCurrentReading() {
  const lines = filterLinesByScope(currentReading?.lines || [], settings.scope, settings.documentProfile);
  const text = lines.map(line => line.text).join("\n");
  if (!text) { setStatus(tr("nothingToSave")); return; }
  try { await navigator.clipboard.writeText(text); setStatus(tr("copyDone")); }
  catch { setStatus(tr("copyFailed")); }
}

function saveCurrentObservation() {
  const lines = filterLinesByScope(currentReading?.lines || [], settings.scope, settings.documentProfile);
  const text = lines.map(line => line.text).join("\n").trim();
  if (!text) { setStatus(tr("nothingToSave")); return; }
  const key = lines.map(line => normalizeForComparison(line.text)).filter(Boolean).join("\n");
  if (savedObservations.some(item => item.key === key)) {
    setStatus(settings.uiLanguage === "pl" ? "Ten sam tekst jest już zapisany." : "This exact text is already saved."); return;
  }
  const allPreviousLineKeys = new Set(savedObservations.flatMap(item => item.lineKeys || []));
  const lineKeys = [...new Set(lines.map(line => normalizeForComparison(line.text)).filter(Boolean))];
  const overlap = lineKeys.filter(line => allPreviousLineKeys.has(line));
  const observation = {
    id: `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
    savedAt: new Date().toISOString(),
    profile: settings.documentProfile,
    scope: settings.scope,
    mode: settings.scanMode,
    text,
    lines: lines.map(line => ({ text: line.text, confidence: line.confidence })),
    lineKeys,
    key,
    overlappingLines: overlap
  };
  savedObservations.push(observation);
  persistObservations(savedObservations);
  renderSaved();
  setStatus(tr("stored"));
}

function deleteObservation(id) {
  savedObservations = savedObservations.filter(item => item.id !== id);
  persistObservations(savedObservations); renderSaved();
}

function clearSavedConfirmation() {
  elements.popoverDescription.textContent = settings.uiLanguage === "pl" ? "Usunąć wszystkie zapisane lokalnie obserwacje? Bieżący wynik OCR pozostanie." : "Delete all locally saved observations? The current OCR result will remain.";
  elements.popoverBody.replaceChildren();
  elements.popoverFooter.replaceChildren();
  addButton(elements.popoverFooter, tr("cancel"), "cancel");
  addButton(elements.popoverFooter, tr("clearSaved"), "confirm-clear-saved", "danger");
}

// Handle confirmation buttons that mutate the local observation store.
elements.popoverFooter.addEventListener("click", event => {
  const button = event.target.closest('[data-action="confirm-clear-saved"]');
  if (!button) return;
  savedObservations = [];
  clearPersistedObservations();
  renderSaved();
  closePopover();
});

function clampNumber(value, min, max, fallback) { const number = Number(value); return Math.max(min, Math.min(max, Number.isFinite(number) ? number : fallback)); }
function sleep(ms) { return new Promise(resolve => setTimeout(resolve, ms)); }
