import { buildReading } from "./result-cleanup.js";

export class OcrEngine {
  constructor() {
    this.worker = null;
    this.languageKey = "";
  }

  async ensureWorker(languages, onProgress = () => {}) {
    const key = [...languages].sort().join("+");
    if (this.worker && this.languageKey === key) return this.worker;
    if (this.worker) {
      await this.worker.terminate();
      this.worker = null;
      this.languageKey = "";
    }
    if (!globalThis.Tesseract?.createWorker) {
      throw new Error("Tesseract.js did not load. Check the CDN connection and reload.");
    }
    this.worker = await globalThis.Tesseract.createWorker(key, 1, {
      logger: message => onProgress(message)
    });
    this.languageKey = key;
    return this.worker;
  }

  async recognize(canvas, languages, options = {}) {
    const worker = await this.ensureWorker(languages, options.onProgress);
    const { data } = await worker.recognize(canvas, {}, { blocks: true });
    return { data, reading: buildReading(data, { profile: options.profile || "receipt" }) };
  }

  terminate() {
    if (!this.worker) return Promise.resolve();
    const worker = this.worker;
    this.worker = null;
    this.languageKey = "";
    return worker.terminate();
  }
}
