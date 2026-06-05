import 'dart:typed_data';
import '../domain/ocr_engine_type.dart';

class AppState {
  OcrEngineType selectedEngine;
  String recognizedText;

  Uint8List? imageBytes;
  String? ocrResult;

  AppState({
    this.selectedEngine = OcrEngineType.auto,
    this.recognizedText = '',
    this.imageBytes,
    this.ocrResult,
  });
}