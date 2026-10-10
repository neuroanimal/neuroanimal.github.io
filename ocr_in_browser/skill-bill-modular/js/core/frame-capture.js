export function captureFrame(video) {
  if (!video.videoWidth || !video.videoHeight) throw new Error("Camera frame is not ready yet.");
  const canvas = document.createElement("canvas");
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  canvas.getContext("2d", { willReadFrequently: true }).drawImage(video, 0, 0, canvas.width, canvas.height);
  return canvas;
}

/** Crop a centered target from the camera frame; percentages are relative to the source image. */
export function cropTarget(frame, widthPct, heightPct) {
  const widthRatio = clamp(Number(widthPct) / 100, 0.01, 1);
  const heightRatio = clamp(Number(heightPct) / 100, 0.02, 1);
  const width = Math.max(1, Math.round(frame.width * widthRatio));
  const height = Math.max(1, Math.round(frame.height * heightRatio));
  const x = Math.round((frame.width - width) / 2);
  const y = Math.round((frame.height - height) / 2);
  const canvas = document.createElement("canvas");
  canvas.width = width;
  canvas.height = height;
  canvas.getContext("2d", { willReadFrequently: true }).drawImage(frame, x, y, width, height, 0, 0, width, height);
  return { canvas, offsetX: x, offsetY: y };
}

// Backwards-compatible helper for earlier prototypes.
export function cropPenTarget(frame) {
  return cropTarget(frame, 62, 5.5);
}

export function translateBoundingBoxes(data, xOffset, yOffset) {
  const visit = object => {
    if (!object || typeof object !== "object") return;
    if (object.bbox && typeof object.bbox === "object") {
      object.bbox.x0 = Number(object.bbox.x0) + xOffset;
      object.bbox.x1 = Number(object.bbox.x1) + xOffset;
      object.bbox.y0 = Number(object.bbox.y0) + yOffset;
      object.bbox.y1 = Number(object.bbox.y1) + yOffset;
    }
    Object.values(object).forEach(value => { if (value && typeof value === "object") visit(value); });
  };
  visit(data);
}

function clamp(value, min, max) { return Math.max(min, Math.min(max, Number.isFinite(value) ? value : min)); }
