import 'dart:typed_data';

abstract interface class OcrEngine {
  Future<void> init();
  Future<void> dispose();

  Future<String> recognizeText(Uint8List imageBytes);
}