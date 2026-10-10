export class CameraController {
  constructor(video, callbacks = {}) {
    this.video = video;
    this.stream = null;
    this.callbacks = callbacks;
  }

  get isOn() { return Boolean(this.stream); }

  async start() {
    if (this.stream) return this.stream;
    if (!navigator.mediaDevices?.getUserMedia) {
      throw new Error("getUserMedia is unavailable; open the published HTTPS page in a supported browser.");
    }
    const stream = await navigator.mediaDevices.getUserMedia({
      audio: false,
      video: {
        facingMode: { ideal: "environment" },
        width: { ideal: 1280 },
        height: { ideal: 720 }
      }
    });
    try {
      this.video.srcObject = stream;
      await this.video.play();
      // Ask for continuous autofocus when the browser exposes it; unsupported devices ignore this.
      try {
        const track = stream.getVideoTracks?.()[0];
        const capabilities = track?.getCapabilities?.();
        if (capabilities?.focusMode?.includes?.("continuous")) {
          await track.applyConstraints({ advanced: [{ focusMode: "continuous" }] });
        }
      } catch {
        // Camera constraints vary across Safari, Chrome and device vendors; keep the working stream.
      }
      this.stream = stream;
      this.callbacks.onChange?.(true);
      return stream;
    } catch (error) {
      stream.getTracks().forEach(track => track.stop());
      this.video.srcObject = null;
      throw error;
    }
  }

  stop() {
    if (this.stream) this.stream.getTracks().forEach(track => track.stop());
    this.stream = null;
    this.video.pause();
    this.video.srcObject = null;
    this.callbacks.onChange?.(false);
  }
}
