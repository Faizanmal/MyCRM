"""
Transcription Engine
Core transcription services using multiple providers
"""

import openai
from django.conf import settings
from django.utils import timezone
from typing import Optional, Dict, Any, List
import logging
import requests
import tempfile
import os

logger = logging.getLogger(__name__)


class TranscriptionEngine:
    """Engine for transcribing audio using various providers"""
    
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    
    def transcribe(
        self,
        audio_file_path: str,
        provider: str = 'whisper',
        language: Optional[str] = None,
        enable_diarization: bool = True,
        custom_vocabulary: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Main transcription method that routes to appropriate provider
        """
        try:
            if provider == 'whisper':
                return self._transcribe_whisper(
                    audio_file_path, language, custom_vocabulary
                )
            elif provider == 'deepgram':
                return self._transcribe_deepgram(
                    audio_file_path, language, enable_diarization
                )
            elif provider == 'assembly':
                return self._transcribe_assembly(
                    audio_file_path, language, enable_diarization
                )
            else:
                return self._transcribe_whisper(
                    audio_file_path, language, custom_vocabulary
                )
        except Exception as e:
            logger.error(f"Transcription error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'provider': provider
            }
    
    def _transcribe_whisper(
        self,
        audio_file_path: str,
        language: Optional[str] = None,
        custom_vocabulary: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Transcribe using OpenAI Whisper"""
        try:
            with open(audio_file_path, 'rb') as audio_file:
                # Build prompt with custom vocabulary if provided
                prompt = ""
                if custom_vocabulary:
                    prompt = f"Vocabulary hints: {', '.join(custom_vocabulary)}"
                
                # Get word-level timestamps
                response = self.openai_client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language=language,
                    prompt=prompt if prompt else None,
                    response_format="verbose_json",
                    timestamp_granularities=["word", "segment"]
                )
            
            return {
                'success': True,
                'provider': 'whisper',
                'full_text': response.text,
                'language': response.language,
                'duration_seconds': response.duration,
                'segments': self._format_whisper_segments(response.segments) if hasattr(response, 'segments') else [],
                'words': self._format_whisper_words(response.words) if hasattr(response, 'words') else [],
                'confidence': 0.95  # Whisper doesn't provide confidence scores
            }
        except Exception as e:
            logger.error(f"Whisper transcription error: {str(e)}")
            raise
    
    def _format_whisper_segments(self, segments) -> List[Dict]:
        """Format Whisper segments for storage"""
        formatted = []
        for segment in segments:
            formatted.append({
                'id': segment.id if hasattr(segment, 'id') else len(formatted),
                'start': segment.start,
                'end': segment.end,
                'text': segment.text.strip(),
                'tokens': segment.tokens if hasattr(segment, 'tokens') else [],
                'temperature': segment.temperature if hasattr(segment, 'temperature') else 0,
                'avg_logprob': segment.avg_logprob if hasattr(segment, 'avg_logprob') else 0,
                'compression_ratio': segment.compression_ratio if hasattr(segment, 'compression_ratio') else 0,
                'no_speech_prob': segment.no_speech_prob if hasattr(segment, 'no_speech_prob') else 0
            })
        return formatted
    
    def _format_whisper_words(self, words) -> List[Dict]:
        """Format Whisper words for storage"""
        formatted = []
        for word in words:
            formatted.append({
                'word': word.word,
                'start': word.start,
                'end': word.end
            })
        return formatted
    
    def _transcribe_deepgram(
        self,
        audio_file_path: str,
        language: Optional[str] = None,
        enable_diarization: bool = True
    ) -> Dict[str, Any]:
        """Transcribe using Deepgram (placeholder for integration)"""
        # This would integrate with Deepgram API
        # For now, fall back to Whisper
        logger.info("Deepgram integration - falling back to Whisper")
        return self._transcribe_whisper(audio_file_path, language)
    
    def _transcribe_assembly(
        self,
        audio_file_path: str,
        language: Optional[str] = None,
        enable_diarization: bool = True
    ) -> Dict[str, Any]:
        """Transcribe using AssemblyAI (placeholder for integration)"""
        # This would integrate with AssemblyAI API
        # For now, fall back to Whisper
        logger.info("AssemblyAI integration - falling back to Whisper")
        return self._transcribe_whisper(audio_file_path, language)


class SpeakerDiarization:
    """Speaker diarization to identify different speakers"""
    
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    
    def identify_speakers(
        self,
        transcript_segments: List[Dict],
        participant_hints: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Use AI to identify and label different speakers in the transcript
        """
        try:
            # Combine segments for analysis
            transcript_text = "\n".join([
                f"[{s['start']:.1f}s]: {s['text']}"
                for s in transcript_segments
            ])
            
            prompt = f"""Analyze this transcript and identify different speakers.
            
Transcript:
{transcript_text[:8000]}

{f"Participant hints: {', '.join(participant_hints)}" if participant_hints else ""}

For each segment, identify the most likely speaker based on:
1. Content and context
2. Speaking style
3. Topic transitions
4. Question/answer patterns

Return a JSON object with:
1. speaker_count: estimated number of speakers
2. speakers: list of speaker descriptions
3. segments: list of segment assignments with speaker IDs

Format:
{{
    "speaker_count": 2,
    "speakers": [
        {{"id": "speaker_1", "description": "Sales rep - asks questions, explains product"}},
        {{"id": "speaker_2", "description": "Customer - asks about pricing, expresses concerns"}}
    ],
    "segments": [
        {{"start": 0.0, "speaker_id": "speaker_1"}},
        ...
    ]
}}"""
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            
            import json
            result = json.loads(response.choices[0].message.content)
            
            return {
                'success': True,
                'speaker_count': result.get('speaker_count', 2),
                'speakers': result.get('speakers', []),
                'segment_assignments': result.get('segments', [])
            }
            
        except Exception as e:
            logger.error(f"Speaker diarization error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'speaker_count': 2,
                'speakers': [],
                'segment_assignments': []
            }
    
    def merge_speaker_labels(
        self,
        transcript_segments: List[Dict],
        speaker_assignments: List[Dict]
    ) -> List[Dict]:
        """Merge speaker labels into transcript segments"""
        # Create time-based lookup
        speaker_at_time = {}
        sorted_assignments = sorted(speaker_assignments, key=lambda x: x['start'])
        
        for i, assignment in enumerate(sorted_assignments):
            start = assignment['start']
            end = sorted_assignments[i + 1]['start'] if i + 1 < len(sorted_assignments) else float('inf')
            speaker_at_time[(start, end)] = assignment.get('speaker_id', 'unknown')
        
        # Assign speakers to segments
        labeled_segments = []
        for segment in transcript_segments:
            segment_start = segment['start']
            speaker = 'unknown'
            
            for (start, end), speaker_id in speaker_at_time.items():
                if start <= segment_start < end:
                    speaker = speaker_id
                    break
            
            labeled_segments.append({
                **segment,
                'speaker': speaker
            })
        
        return labeled_segments


class RealTimeTranscription:
    """Real-time transcription for live audio streams"""
    
    def __init__(self, recording_id: str):
        self.recording_id = recording_id
        self.buffer = []
        self.accumulated_text = ""
        self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    
    async def process_chunk(
        self,
        audio_chunk: bytes,
        chunk_duration_ms: int = 1000
    ) -> Optional[Dict[str, Any]]:
        """
        Process an audio chunk and return partial transcription
        Note: Real-time transcription with Whisper requires buffering
        """
        self.buffer.append(audio_chunk)
        
        # Process when we have enough audio (e.g., 5 seconds)
        if len(self.buffer) >= 5:
            return await self._process_buffer()
        
        return None
    
    async def _process_buffer(self) -> Dict[str, Any]:
        """Process accumulated audio buffer"""
        try:
            # Combine buffer chunks
            combined_audio = b''.join(self.buffer)
            
            # Save to temp file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
                tmp.write(combined_audio)
                tmp_path = tmp.name
            
            try:
                # Transcribe
                with open(tmp_path, 'rb') as audio_file:
                    response = self.openai_client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        prompt=f"Previous context: {self.accumulated_text[-500:]}" if self.accumulated_text else None
                    )
                
                new_text = response.text
                self.accumulated_text += " " + new_text
                
                # Clear buffer
                self.buffer = []
                
                return {
                    'partial_text': new_text,
                    'accumulated_text': self.accumulated_text.strip(),
                    'is_final': False
                }
                
            finally:
                os.unlink(tmp_path)
                
        except Exception as e:
            logger.error(f"Real-time transcription error: {str(e)}")
            return {
                'error': str(e),
                'partial_text': '',
                'accumulated_text': self.accumulated_text
            }
    
    async def finalize(self) -> Dict[str, Any]:
        """Finalize transcription with any remaining buffer"""
        if self.buffer:
            await self._process_buffer()
        
        return {
            'final_text': self.accumulated_text.strip(),
            'is_final': True
        }


class AudioPreprocessor:
    """Preprocess audio files for optimal transcription"""
    
    @staticmethod
    def get_audio_info(file_path: str) -> Dict[str, Any]:
        """Get audio file information"""
        try:
            import subprocess
            
            result = subprocess.run([
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_format', '-show_streams', file_path
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                import json
                info = json.loads(result.stdout)
                
                stream = info.get('streams', [{}])[0]
                format_info = info.get('format', {})
                
                return {
                    'duration': float(format_info.get('duration', 0)),
                    'sample_rate': int(stream.get('sample_rate', 0)),
                    'channels': int(stream.get('channels', 1)),
                    'codec': stream.get('codec_name', ''),
                    'bitrate': int(format_info.get('bit_rate', 0)),
                    'file_size': int(format_info.get('size', 0))
                }
            
        except Exception as e:
            logger.error(f"Error getting audio info: {str(e)}")
        
        return {}
    
    @staticmethod
    def convert_to_optimal_format(
        input_path: str,
        output_path: Optional[str] = None
    ) -> str:
        """Convert audio to optimal format for transcription"""
        try:
            import subprocess
            
            if output_path is None:
                output_path = input_path.rsplit('.', 1)[0] + '_converted.mp3'
            
            # Convert to mono, 16kHz, mp3 - optimal for Whisper
            subprocess.run([
                'ffmpeg', '-y', '-i', input_path,
                '-ac', '1',  # Mono
                '-ar', '16000',  # 16kHz
                '-b:a', '64k',  # 64kbps
                output_path
            ], capture_output=True, check=True)
            
            return output_path
            
        except Exception as e:
            logger.error(f"Audio conversion error: {str(e)}")
            return input_path  # Return original if conversion fails
    
    @staticmethod
    def split_large_file(
        file_path: str,
        max_duration_seconds: int = 600,  # 10 minutes
        output_dir: Optional[str] = None
    ) -> List[str]:
        """Split large audio files for batch processing"""
        try:
            import subprocess
            
            if output_dir is None:
                output_dir = os.path.dirname(file_path)
            
            base_name = os.path.basename(file_path).rsplit('.', 1)[0]
            output_pattern = os.path.join(output_dir, f"{base_name}_part_%03d.mp3")
            
            subprocess.run([
                'ffmpeg', '-y', '-i', file_path,
                '-f', 'segment',
                '-segment_time', str(max_duration_seconds),
                '-c', 'copy',
                output_pattern
            ], capture_output=True, check=True)
            
            # Find generated files
            import glob
            parts = sorted(glob.glob(os.path.join(output_dir, f"{base_name}_part_*.mp3")))
            
            return parts
            
        except Exception as e:
            logger.error(f"Audio split error: {str(e)}")
            return [file_path]  # Return original if split fails
