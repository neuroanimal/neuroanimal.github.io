import 'dart:io';

import 'package:flutter/foundation.dart';

import '../domain/ocr_engine.dart';
import 'mlkit_native_ocr_engine.dart';
import 'tesseract_ocr_engine.dart';
import 'vision_ocr_engine.dart';

class AutoOcrEngine implements OcrEngine {
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
    // return 'Auto OCR result';

    final OcrEngine engine;

    if (Platform.isIOS) {
      engine = VisionOcrEngine();
    } else if (Platform.isAndroid) {
      engine = MLKitNativeOcrEngine();
    } else {
      engine = TesseractOcrEngine();
    }

    debugPrint('Platform: ${Platform.operatingSystem}');
    debugPrint('Selected engine: ${engine.runtimeType}');

    await engine.init();
    final result = await engine.recognizeText(imageBytes);
    await engine.dispose();
    return result;

  }

}