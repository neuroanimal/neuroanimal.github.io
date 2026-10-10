export class OverlayRenderer {
  constructor(video, canvas, stage) {
    this.video = video;
    this.canvas = canvas;
    this.stage = stage;
    this.context = canvas.getContext("2d");
    this.data = null;
    this.stageIndex = -1;
    this.options = { showRegions: true, showLines: true, showWords: true, showSymbols: true };
    window.addEventListener("resize", () => this.draw());
  }

  setOptions(options) { this.options = { ...this.options, ...options }; this.draw(); }
  setData(data, stageIndex = 0) { this.data = data; this.stageIndex = stageIndex; this.draw(); }
  setStage(index) { this.stageIndex = index; this.draw(); }
  clear() { this.data = null; this.stageIndex = -1; this.draw(); }

  draw() {
    const videoRect = this.video.getBoundingClientRect();
    const canvasRect = this.canvas.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    this.canvas.width = Math.max(1, Math.round(canvasRect.width * dpr));
    this.canvas.height = Math.max(1, Math.round(canvasRect.height * dpr));
    this.context.setTransform(1, 0, 0, 1, 0, 0);
    this.context.clearRect(0, 0, this.canvas.width, this.canvas.height);
    if (!this.data || this.stageIndex < 0 || !this.video.videoWidth || !this.video.videoHeight || !videoRect.width || !videoRect.height) return;

    // Overlay canvas covers the stage; account for the video element's position within it.
    const scale = Math.min(videoRect.width / this.video.videoWidth, videoRect.height / this.video.videoHeight);
    const innerX = (videoRect.width - this.video.videoWidth * scale) / 2;
    const innerY = (videoRect.height - this.video.videoHeight * scale) / 2;
    const relativeX = videoRect.left - canvasRect.left;
    const relativeY = videoRect.top - canvasRect.top;
    this.context.setTransform(dpr, 0, 0, dpr, 0, 0);
    this.context.translate(relativeX + innerX, relativeY + innerY);
    this.context.scale(scale, scale);

    const boxes = collectBoxes(this.data);
    const visibleStages = this.stageIndex + 1;
    const draw = (items, color, width, dashed = false) => {
      this.context.strokeStyle = color;
      this.context.lineWidth = width / scale;
      this.context.setLineDash(dashed ? [8 / scale, 5 / scale] : []);
      for (const box of items) {
        const x = Number(box.x0), y = Number(box.y0);
        const w = Number(box.x1) - x, h = Number(box.y1) - y;
        if (Number.isFinite(x) && Number.isFinite(y) && w > 0 && h > 0) this.context.strokeRect(x, y, w, h);
      }
      this.context.setLineDash([]);
    };
    if (visibleStages >= 1 && this.options.showRegions) draw(boxes.regions, "#ffdf00", 2.2, true);
    if (visibleStages >= 2 && this.options.showLines) draw(boxes.lines, "#ffb300", 1.8);
    if (visibleStages >= 3 && this.options.showWords) draw(boxes.words, "#00d5f5", 1.5);
    if (visibleStages >= 4 && this.options.showSymbols) draw(boxes.symbols, "#ff4f9a", 1.1);
  }
}

function collectBoxes(data) {
  const result = { regions: [], lines: [], words: [], symbols: [] };
  for (const block of (data?.blocks || [])) {
    if (block.bbox) result.regions.push(block.bbox);
    for (const paragraph of (block.paragraphs || [])) {
      for (const line of (paragraph.lines || [])) {
        if (line.bbox) result.lines.push(line.bbox);
        for (const word of (line.words || [])) {
          if (word.bbox) result.words.push(word.bbox);
          for (const symbol of (word.symbols || [])) if (symbol.bbox) result.symbols.push(symbol.bbox);
        }
      }
    }
  }
  return result;
}
