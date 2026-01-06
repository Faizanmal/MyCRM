import 'package:flutter/foundation.dart';
import '../services/voice/voice_recorder_service.dart';
import '../core/utils/api_client.dart';

class VoiceIntelligenceProvider extends ChangeNotifier {
  final VoiceRecorderService _service;

  bool _isRecording = false;
  bool _isUploading = false;
  String? _currentPath;
  String? _error;

  VoiceIntelligenceProvider(ApiClient apiClient) : _service = VoiceRecorderService(apiClient);

  bool get isRecording => _isRecording;
  bool get isUploading => _isUploading;
  String? get error => _error;

  Future<void> startRecording() async {
    try {
      _currentPath = await _service.getTemporaryPath();
      await _service.startRecording(_currentPath!);
      _isRecording = true;
      _error = null;
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }

  Future<void> stopAndUpload({String? title}) async {
    try {
      _isRecording = false;
      notifyListeners();

      final path = await _service.stopRecording();
      if (path != null) {
        _isUploading = true;
        notifyListeners();

        await _service.uploadRecording(path, title: title);

        _isUploading = false;
        notifyListeners();
      }
    } catch (e) {
      _isRecording = false;
      _isUploading = false;
      _error = e.toString();
      notifyListeners();
    }
  }

  Future<void> cancelRecording() async {
    try {
      await _service.stopRecording();
      _isRecording = false;
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }
}
