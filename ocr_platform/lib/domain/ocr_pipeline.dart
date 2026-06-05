import 'dart:typed_data';

import '../state/app_state.dart';
import 'ocr_engine.dart';
import 'ocr_engine_factory.dart';

class OcrPipeline {
  Future<void> run({
    required AppState state,
    required Uint8List imageBytes,
  }) async {
    state.imageBytes = imageBytes;

    // placeholder "OCR processing"
    // await Future.delayed(const Duration(milliseconds: 300));
    final OcrEngine engine =
        OcrEngineFactory.create(state.selectedEngine);

    await engine.init();

    // state.ocrResult =
    //     //  'Mock OCR result (${state.selectedEngine.name}) - ${imageBytes.length} bytes';
    //     await engine.recognizeText(imageBytes);

    try {
      final result = await engine.recognizeText(imageBytes);

      state.ocrResult = result;
    } finally {
      await engine.dispose();
    }

  }
}