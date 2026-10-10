import assert from "node:assert/strict";
import { cropTarget } from "../js/core/frame-capture.js";

let lastDrawArgs = null;
globalThis.document = {
  createElement(name) {
    assert.equal(name, "canvas");
    return {
      width: 0,
      height: 0,
      getContext() {
        return { drawImage(...args) { lastDrawArgs = args; } };
      }
    };
  }
};

const frame = { width: 1280, height: 720 };
const pen = cropTarget(frame, 5.5, 22);
assert.equal(pen.canvas.width, 70);
assert.equal(pen.canvas.height, 158);
assert.equal(pen.offsetX, 605);
assert.equal(pen.offsetY, 281);
assert.deepEqual(lastDrawArgs, [frame, 605, 281, 70, 158, 0, 0, 70, 158]);

const scanner = cropTarget(frame, 100, 11);
assert.equal(scanner.canvas.width, 1280, "Scanner can cover the full frame width");
assert.equal(scanner.canvas.height, 79);
assert.equal(scanner.offsetX, 0, "Full-width Scanner has no horizontal crop offset");
assert.equal(scanner.offsetY, 321);

console.log("Frame-capture tests passed.");
