import 'package:record/record.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:path_provider/path_provider.dart';
import 'dart:io';
import '../../core/constants/api_constants.dart';
import '../../core/utils/api_client.dart';

class VoiceRecorderService {
  final ApiClient _apiClient;
  final AudioRecorder _audioRecorder = AudioRecorder();

  VoiceRecorderService(this._apiClient);

  Future<bool> hasPermission() async {
    final status = await Permission.microphone.request();
    return status == PermissionStatus.granted;
  }

  Future<void> startRecording(String path) async {
    if (await hasPermission()) {
      await _audioRecorder.start(const RecordConfig(), path: path);
    } else {
      throw Exception('Microphone permission denied');
    }
  }

  Future<String?> stopRecording() async {
    return await _audioRecorder.stop();
  }

  Future<String> getTemporaryPath() async {
    final directory = await getTemporaryDirectory();
    return '${directory.path}/recording_${DateTime.now().millisecondsSinceEpoch}.m4a';
  }

  Future<Map<String, dynamic>> uploadRecording(String path, {String? title}) async {
    final response = await _apiClient.uploadFile(
      ApiConstants.callRecordings,
      path,
      data: title != null ? {'title': title} : null,
    );

    if (response.statusCode == 201) {
      return response.data;
    }
    throw Exception('Failed to upload recording');
  }
}
