import 'dart:typed_data';

import '../domain/ocr_engine.dart';

class MLKitFlutterOcrEngine implements OcrEngine {
  @override
  Future<void> init() async {
    // nothing
  }

  @override
  Future<void> dispose() async {
    // nothing
  }

  @override
  Future<String> recognizeText(Uint8List imageBytes) async {
    return 'MLKit Flutter OCR result';
  }
}