import 'package:flutter/material.dart';

// import 'domain/ocr_engine_type.dart';
import 'presentation/home_page.dart';
import 'state/app_state.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'OCR Platform',
      home: HomePage(
        state: AppState(),
      ),
    );
  }
}