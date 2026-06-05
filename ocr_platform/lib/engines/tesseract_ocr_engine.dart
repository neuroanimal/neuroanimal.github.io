import 'dart:io';

import 'package:flutter/foundation.dart';

import '../domain/ocr_engine.dart';

class TesseractOcrEngine implements OcrEngine {
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
    // return 'Tesseract OCR result';

    final tempDir = Directory.systemTemp;

    final imageFile = File(
      '${tempDir.path}/ocr_input.png',
    );

    await imageFile.writeAsBytes(imageBytes);

    final outputBase =
        '${tempDir.path}/ocr_output';

    final result = await Process.run(
      'tesseract',
      [
        imageFile.path,
        outputBase,
        '-l',
        'pol+eng',
      ],
    );

    debugPrint('Tesseract exitCode: ${result.exitCode}');
    debugPrint('Tesseract stdout: ${result.stdout}');
    debugPrint('Tesseract stderr: ${result.stderr}');

    if (result.exitCode != 0) {
      return 'Tesseract error: ${result.stderr}';
    }

    final textFile =
        File('$outputBase.txt');

    if (!await textFile.exists()) {
      return 'No OCR output generated';
    }

    //return 'Tesseract OCR placeholder result';
    return await textFile.readAsString();

  }

}