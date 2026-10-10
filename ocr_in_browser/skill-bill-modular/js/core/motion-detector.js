const WIDTH = 48;
const HEIGHT = 36;
const POLL_MS = 220;
const STABLE_DEFAULT_MS = 1000;
const CAPTURE_DELAY_DEFAULT_MS = 500;

/**
 * Tracks low-resolution frame changes. For Scanner/Pen, each capture is followed by
 * a movement gate so a stationary row is not appended again and again. Motion is still
 * monitored while OCR is running, so a user can keep moving through a long document.
 */
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
    this.captureInProgress = false;
    this.completedOneShot = false;
    this.repeatAfterMovement = false;
    this.awaitingMovement = false;
    this.movementSeen = false;
    this.movementDuringCapture = false;
    this.isMoving = false;
    this.callbacks = {};
    this.getThreshold = () => 18;
    this.stableMs = STABLE_DEFAULT_MS;
    this.captureDelayMs = CAPTURE_DELAY_DEFAULT_MS;
  }

  start(onStable, options = {}) {
    this.stop();
    this.running = true;
    this.previous = null;
    this.ema = null;
    this.stableSince = null;
    this.movingVotes = 0;
    this.captureInProgress = false;
    this.completedOneShot = false;
    this.repeatAfterMovement = Boolean(options.repeatAfterMovement);
    this.awaitingMovement = false;
    this.movementSeen = false;
    this.movementDuringCapture = false;
    this.isMoving = false;
    this.callbacks = options;
    this.onStable = onStable;
    this.getThreshold = options.getThreshold || (() => 18);
    this.stableMs = Math.max(0, Number(options.stableMs ?? STABLE_DEFAULT_MS));
    this.captureDelayMs = Math.max(0, Number(options.captureDelayMs ?? CAPTURE_DELAY_DEFAULT_MS));
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
    this.captureInProgress = false;
    this.completedOneShot = false;
    this.awaitingMovement = false;
    this.movementSeen = false;
    this.movementDuringCapture = false;
    this.isMoving = false;
  }

  schedule(delay = POLL_MS) {
    if (!this.running) return;
    this.timer = setTimeout(() => this.tick(), delay);
  }

  tick() {
    if (!this.running) return;
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
        if (this.ema > threshold) this.movingVotes = Math.min(4, this.movingVotes + 1);
        else this.movingVotes = Math.max(0, this.movingVotes - 1);

        const nowMoving = this.movingVotes >= 2;
        if (nowMoving) {
          if (!this.isMoving) this.callbacks.onStatus?.("moving");
          this.isMoving = true;
          this.stableSince = null;
          if (this.captureInProgress) this.movementDuringCapture = true;
          if (this.awaitingMovement) this.movementSeen = true;
        } else {
          if (this.isMoving) {
            this.isMoving = false;
            this.stableSince = now;
            this.callbacks.onStatus?.(this.awaitingMovement && !this.movementSeen ? "waitingMovement" : "waitingStill");
          } else if (this.stableSince === null && this.movingVotes === 0 && !(this.awaitingMovement && !this.movementSeen)) {
            this.stableSince = now;
            this.callbacks.onStatus?.("waitingStill");
          }
        }
      } else {
        this.stableSince = now;
        this.ema = 0;
      }
      this.previous = gray;

      const moving = this.isMoving;
      const stableFor = (!moving && this.stableSince != null) ? now - this.stableSince : 0;
      const requiredStableMs = this.stableMs + this.captureDelayMs;
      this.callbacks.onMetrics?.({
        score: this.ema ?? score,
        stableFor,
        stablePercent: requiredStableMs > 0 ? Math.min(100, stableFor / requiredStableMs * 100) : 100,
        moving,
        awaitingMovement: this.awaitingMovement && !this.movementSeen
      });

      const movementGateClosed = this.awaitingMovement && !this.movementSeen;
      if (!this.captureInProgress && !this.completedOneShot && !movementGateClosed && !moving &&
          this.stableSince != null && stableFor >= requiredStableMs) {
        this.triggerCapture();
      }
    } catch (error) {
      this.callbacks.onError?.(error);
    }
    this.schedule(POLL_MS);
  }

  triggerCapture() {
    this.captureInProgress = true;
    this.movementDuringCapture = false;
    this.awaitingMovement = false;
    this.movementSeen = false;
    Promise.resolve().then(() => this.onStable?.()).catch(error => {
      this.callbacks.onError?.(error);
    }).finally(() => {
      if (!this.running) return;
      this.captureInProgress = false;
      if (this.repeatAfterMovement) {
        if (this.movementDuringCapture) {
          // Movement occurred while OCR was processing. Resume waiting for stillness at
          // the latest position instead of requiring an additional nudge from the user.
          this.awaitingMovement = false;
          this.movementSeen = false;
        } else {
          // Do not repeat the same frame; wait until the document/camera moves again.
          this.awaitingMovement = true;
          this.movementSeen = false;
          this.stableSince = null;
        }
      } else {
        this.completedOneShot = true;
      }
    });
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
  // Sample every other pixel to reduce tiny sensor-noise fluctuations.
  for (let i = 0; i < a.length; i += 2) total += Math.abs(a[i] - b[i]);
  return total / Math.ceil(a.length / 2);
}
