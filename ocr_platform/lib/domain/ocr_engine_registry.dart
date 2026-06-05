import '../engines/mock_ocr_engine.dart';
import '../engines/auto_ocr_engine.dart';
import '../engines/mlkit_native_ocr_engine.dart';
import '../engines/mlkit_flutter_ocr_engine.dart';
import '../engines/onnx_ocr_engine.dart';
import '../engines/paddle_ocr_engine.dart';
import '../engines/tesseract_ocr_engine.dart';
import '../engines/vision_ocr_engine.dart';

import 'ocr_engine.dart';
import 'ocr_engine_type.dart';

class OcrEngineRegistry {
  static final Map<OcrEngineType, OcrEngine Function()> _registry = {
    OcrEngineType.mock: () => MockOcrEngine(),
    OcrEngineType.auto: () => AutoOcrEngine(),

    OcrEngineType.onnx: () => OnnxOcrEngine(),
    OcrEngineType.tesseract: () => TesseractOcrEngine(),
    OcrEngineType.paddle: () => PaddleOcrEngine(),

    OcrEngineType.mlKitNative: () => MLKitNativeOcrEngine(),
    OcrEngineType.mlKitFlutter: () => MLKitFlutterOcrEngine(),
    OcrEngineType.visionFramework: () => VisionOcrEngine(),
  };

  static OcrEngine create(OcrEngineType type) {
    final factory = _registry[type];

    if (factory == null) {
      throw StateError('No OCR engine registered for: $type');
    }

    return factory();
  }
}