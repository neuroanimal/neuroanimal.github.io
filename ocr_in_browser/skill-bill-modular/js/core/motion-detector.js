const WIDTH = 48;
const HEIGHT = 36;
const POLL_MS = 220;
const STABLE_DEFAULT_MS = 1250;

export class MotionDetector {
  constructor(video) {
    this.video = video;
    this.canvas = document.createElement("canvas");
    this.canvas.width = WIDTH;
    this.canvas.height = HEIGHT;
    this.context = this.canvas.getContext("2d", { willReadFrequently: true });
    this.timer = null;
    this.running = false;
    this.previous = null;
    this.ema = null;
    this.stableSince = null;
    this.movingVotes = 0;
    this.fired = false;
    this.callbacks = {};
    this.getThreshold = () => 14;
    this.stableMs = STABLE_DEFAULT_MS;
  }

  start(onStable, options = {}) {
    this.stop();
    this.running = true;
    this.fired = false;
    this.previous = null;
    this.ema = null;
    this.stableSince = null;
    this.movingVotes = 0;
    this.callbacks = options;
    this.onStable = onStable;
    this.getThreshold = options.getThreshold || (() => 14);
    this.stableMs = options.stableMs || STABLE_DEFAULT_MS;
    this.schedule(100);
  }

  stop() {
    this.running = false;
    if (this.timer) clearTimeout(this.timer);
    this.timer = null;
    this.previous = null;
    this.ema = null;
    this.stableSince = null;
    this.movingVotes = 0;
    this.fired = false;
  }

  schedule(delay = POLL_MS) {
    if (!this.running) return;
    this.timer = setTimeout(() => this.tick(), delay);
  }

  tick() {
    if (!this.running || this.fired) return;
    try {
      if (this.video.readyState < HTMLMediaElement.HAVE_CURRENT_DATA || !this.video.videoWidth || !this.video.videoHeight) {
        this.schedule(POLL_MS);
        return;
      }
      this.context.drawImage(this.video, 0, 0, WIDTH, HEIGHT);
      const pixels = this.context.getImageData(0, 0, WIDTH, HEIGHT).data;
      const gray = grayscale(pixels);
      const now = performance.now();
      let score = 0;

      if (this.previous) {
        score = meanDifference(gray, this.previous);
        this.ema = this.ema == null ? score : (this.ema * 0.55 + score * 0.45);
        const threshold = Number(this.getThreshold());
        if (this.ema > threshold) this.movingVotes += 1;
        else this.movingVotes = Math.max(0, this.movingVotes - 1);

        if (this.movingVotes >= 2) {
          if (this.stableSince !== null) this.callbacks.onStatus?.("moving");
          this.stableSince = null;
        } else if (this.stableSince === null) {
          this.stableSince = now;
          this.callbacks.onStatus?.("waitingStill");
        }
      } else {
        this.stableSince = now;
        this.ema = 0;
      }
      this.previous = gray;

      const moving = this.movingVotes >= 2;
      const stableFor = (!moving && this.stableSince != null) ? now - this.stableSince : 0;
      this.callbacks.onMetrics?.({ score: this.ema ?? score, stableFor, stablePercent: Math.min(100, stableFor / this.stableMs * 100), moving });
      if (!moving && this.stableSince != null && stableFor >= this.stableMs && !this.fired) {
        this.fired = true;
        void this.onStable?.();
        return;
      }
    } catch (error) {
      this.callbacks.onError?.(error);
    }
    this.schedule(POLL_MS);
  }
}

function grayscale(rgba) {
  const result = new Uint8Array(rgba.length / 4);
  for (let src = 0, dst = 0; src < rgba.length; src += 4, dst += 1) {
    result[dst] = Math.round(0.299 * rgba[src] + 0.587 * rgba[src + 1] + 0.114 * rgba[src + 2]);
  }
  return result;
}

function meanDifference(a, b) {
  let total = 0;
  // Skip a few pixels to reduce sensitivity to tiny sensor/noise changes.
  for (let i = 0; i < a.length; i += 2) total += Math.abs(a[i] - b[i]);
  return total / Math.ceil(a.length / 2);
}
