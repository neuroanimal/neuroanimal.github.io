import 'ocr_engine_registry.dart';
import 'ocr_engine_type.dart';
import 'ocr_engine.dart';

import '../engines/mock_ocr_engine.dart';
import '../engines/auto_ocr_engine.dart';
import '../engines/mlkit_native_ocr_engine.dart';
import '../engines/mlkit_flutter_ocr_engine.dart';
import '../engines/onnx_ocr_engine.dart';
import '../engines/paddle_ocr_engine.dart';
import '../engines/tesseract_ocr_engine.dart';
import '../engines/vision_ocr_engine.dart';

const bool useRegistry = true;

class OcrEngineFactory {
  static OcrEngine create(OcrEngineType type) {
    return useRegistry
      ? _createFromRegistry(type)
      : _createFromSwitch(type);
  }
  static OcrEngine _createFromRegistry(OcrEngineType type) {
    return OcrEngineRegistry.create(type);
  }
  static OcrEngine _createFromSwitch(OcrEngineType type) {
    switch (type) {
      case OcrEngineType.mock:
        return MockOcrEngine();
      case OcrEngineType.auto:
        return AutoOcrEngine();
      case OcrEngineType.mlKitNative:
        return MLKitNativeOcrEngine();
      case OcrEngineType.mlKitFlutter:
        return MLKitFlutterOcrEngine();
      case OcrEngineType.visionFramework:
        return VisionOcrEngine();
      case OcrEngineType.tesseract:
        return TesseractOcrEngine();
      case OcrEngineType.paddle:
        return PaddleOcrEngine();
      case OcrEngineType.onnx:
        return OnnxOcrEngine();
    }
  }
}