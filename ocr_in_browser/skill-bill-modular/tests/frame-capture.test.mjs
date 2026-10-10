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
const pen = cropTarget(frame, 62, 5.5);
assert.equal(pen.canvas.width, 794);
assert.equal(pen.canvas.height, 40);
assert.equal(pen.offsetX, 243);
assert.equal(pen.offsetY, 340);
assert.deepEqual(lastDrawArgs, [frame, 243, 340, 794, 40, 0, 0, 794, 40]);

const scanner = cropTarget(frame, 92, 11);
assert.equal(scanner.canvas.width, 1178);
assert.equal(scanner.canvas.height, 79);
assert.equal(scanner.offsetX, 51);
assert.equal(scanner.offsetY, 321);
console.log("Frame-capture tests passed.");
