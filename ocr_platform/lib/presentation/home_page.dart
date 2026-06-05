import 'dart:typed_data';

import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';

import '../domain/ocr_engine_factory.dart';
import '../domain/ocr_engine_type.dart';
import '../domain/ocr_pipeline.dart';
import '../state/app_state.dart';

class HomePage extends StatefulWidget {
  final AppState state;

  const HomePage({
    super.key,
    required this.state,
  });

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  final _picker = ImagePicker();
  final _pipeline = OcrPipeline();

  @override
  void initState() {
    super.initState();
    debugPrint('INIT STATE');
  }

  Future<void> _pickImage() async {
    final XFile? file = await _picker.pickImage(
      source: ImageSource.gallery,
    );

    if (file == null) {
      return;
    }

    final bytes = await file.readAsBytes();

    await _pipeline.run(
      state: widget.state,
      imageBytes: bytes,
    );

    setState(() {});
  }

  Future<void> _runOcr() async {
    try {
      final engine = OcrEngineFactory.create(
        widget.state.selectedEngine,
      );

      await engine.init();

      final result = await engine.recognizeText(
        widget.state.imageBytes ?? Uint8List(0),
      );

      await engine.dispose();

      debugPrint('OCR RESULT:\n$result');

      setState(() {
        widget.state.recognizedText = result;
      });
    } catch (e, stackTrace) {
      debugPrint('OCR ERROR: $e');
      debugPrint('$stackTrace');

      setState(() {
        widget.state.recognizedText = 'ERROR: $e';
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('OCR Platform'),
      ),
      body: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'Backend OCR',
                style: TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                ),
              ),

              const SizedBox(height: 20),

              DropdownButton<OcrEngineType>(
                value: widget.state.selectedEngine,
                items: OcrEngineType.values.map((engine) {
                  return DropdownMenuItem(
                    value: engine,
                    child: Text(engine.name),
                  );
                }).toList(),
                onChanged: (value) {
                  if (value == null) {
                    return;
                  }

                  setState(() {
                    widget.state.selectedEngine = value;
                  });
                },
              ),

              const SizedBox(height: 20),

              Text(
                'Selected: ${widget.state.selectedEngine.name}',
                style: const TextStyle(fontSize: 18),
              ),

              const SizedBox(height: 30),

              ElevatedButton(
                onPressed: _pickImage,
                child: const Text('Pick image'),
              ),

              const SizedBox(height: 20),

              if (widget.state.imageBytes != null)
                Image.memory(
                  widget.state.imageBytes!,
                  height: 250,
                  fit: BoxFit.contain,
                ),

              const SizedBox(height: 30),

              ElevatedButton(
                onPressed: _runOcr,
                child: const Text('Run OCR'),
              ),

              const SizedBox(height: 20),

              const Text(
                'OCR Result',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),

              const SizedBox(height: 10),

              SelectableText(
                widget.state.recognizedText.isEmpty
                    ? 'No OCR result yet'
                    : widget.state.recognizedText,
                style: const TextStyle(
                  fontSize: 16,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}