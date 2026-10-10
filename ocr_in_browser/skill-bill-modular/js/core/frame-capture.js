export function captureFrame(video) {
  if (!video.videoWidth || !video.videoHeight) throw new Error("Camera frame is not ready yet.");
  const canvas = document.createElement("canvas");
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  canvas.getContext("2d", { willReadFrequently: true }).drawImage(video, 0, 0, canvas.width, canvas.height);
  return canvas;
}

export function cropPenTarget(frame) {
  // These normalized coordinates match the Pen reticle in the camera's visible image area.
  const x = Math.round(frame.width * 0.19);
  const y = Math.round(frame.height * 0.39);
  const width = Math.round(frame.width * 0.62);
  const height = Math.round(frame.height * 0.22);
  const canvas = document.createElement("canvas");
  canvas.width = width;
  canvas.height = height;
  canvas.getContext("2d", { willReadFrequently: true }).drawImage(frame, x, y, width, height, 0, 0, width, height);
  return { canvas, offsetX: x, offsetY: y };
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
