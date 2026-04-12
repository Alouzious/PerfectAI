"""
Speech-to-Text Service
Converts audio recordings to text using Groq Whisper API (free)
"""
import os
import logging

logger = logging.getLogger(__name__)


class SpeechToTextService:
    """
    Converts audio files to text transcripts using Groq's Whisper.

    Supported audio formats: mp3, mp4, mpeg, mpga, m4a, wav, webm
    Max file size: 25MB
    Cost: Free on Groq
    """

    SUPPORTED_FORMATS = ['mp3', 'mp4', 'mpeg', 'mpga', 'm4a', 'wav', 'webm']
    MAX_FILE_SIZE_MB = 25

    def __init__(self):
        try:
            from groq import Groq
            self.client = Groq(api_key=self._get_api_key())
        except ImportError:
            raise ImportError(
                "groq package is required. Install with: pip install groq"
            )

    def _get_api_key(self):
        """Get Groq API key from Django settings or environment"""
        try:
            from django.conf import settings
            api_key = getattr(settings, 'GROQ_API_KEY', None)
        except Exception:
            api_key = None

        if not api_key:
            api_key = os.getenv('GROQ_API_KEY')

        if not api_key:
            raise ValueError(
                "GROQ_API_KEY is not set. Add it to your .env file."
            )
        return api_key

    def transcribe(self, audio_file):
        """
        Transcribe an audio file to text.

        Args:
            audio_file: Django InMemoryUploadedFile or TemporaryUploadedFile
                        (the object from request.FILES['audio'])

        Returns:
            dict: {
                'success': True,
                'transcript': 'The full transcribed text...',
                'language': 'en',
                'duration': 45.2
            }

        Raises:
            ValueError: If file format or size is invalid
            RuntimeError: If transcription fails
        """
        self._validate_audio_file(audio_file)

        try:
            logger.info(
                f"Transcribing audio via Groq Whisper: {audio_file.name} "
                f"({audio_file.size / 1024:.1f} KB)"
            )

            # Reset file pointer in case it was already read
            audio_file.seek(0)

            # Groq Whisper — identical interface to OpenAI Whisper
            response = self.client.audio.transcriptions.create(
                model="whisper-large-v3",
                file=audio_file,
                response_format="verbose_json",
                language="en",
            )

            transcript = response.text.strip()

            if not transcript:
                logger.warning("Groq Whisper returned empty transcript")
                return {
                    'success': False,
                    'transcript': '',
                    'error': 'No speech detected in the audio.'
                }

            logger.info(
                f"Transcription complete: {len(transcript.split())} words"
            )

            return {
                'success': True,
                'transcript': transcript,
                'language': getattr(response, 'language', 'en'),
                'duration': getattr(response, 'duration', 0),
            }

        except Exception as e:
            logger.error(f"Groq Whisper transcription failed: {str(e)}")
            raise RuntimeError(f"Transcription failed: {str(e)}")

    def _validate_audio_file(self, audio_file):
        """Validate audio file before sending to API"""

        size_mb = audio_file.size / (1024 * 1024)
        if size_mb > self.MAX_FILE_SIZE_MB:
            raise ValueError(
                f"Audio file is {size_mb:.1f}MB. "
                f"Maximum allowed size is {self.MAX_FILE_SIZE_MB}MB."
            )

        filename = getattr(audio_file, 'name', '')
        if filename:
            ext = filename.rsplit('.', 1)[-1].lower()
            if ext not in self.SUPPORTED_FORMATS:
                raise ValueError(
                    f"Unsupported audio format: .{ext}. "
                    f"Supported formats: {', '.join(self.SUPPORTED_FORMATS)}"
                )

        logger.debug(f"Audio file validated: {filename}, {size_mb:.2f}MB")