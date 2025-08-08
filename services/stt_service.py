# services/stt_service.py
import base64
import os
import logging
import tempfile
import numpy as np
import hashlib
import webrtcvad
from pydub import AudioSegment

# Setup logger
logger = logging.getLogger(__name__)

# Cache directory for audio files (WAV files)
CACHE_DIR = os.path.join(os.getcwd(), 'stt_cache')
os.makedirs(CACHE_DIR, exist_ok=True)

# VAD configuration
VAD_SAMPLING_RATE = 16000  # WebRTC VAD only supports 8kHz, 16kHz, 32kHz, 48kHz
VAD_FRAME_DURATION = 30  # ms, supported values are 10, 20, or 30
VAD_MODE = 3  # Aggressiveness mode (0-3)
vad = webrtcvad.Vad()
vad.set_mode(VAD_MODE)

def convert_audio_to_wav(audio_bytes):
    """
    Convert the given audio bytes (MP3) into WAV format for VAD processing.
    Caches the WAV file.
    """
    try:
        logger.debug("Starting audio conversion to WAV format")
        file_hash = hashlib.md5(audio_bytes).hexdigest()
        cached_wav_path = os.path.join(CACHE_DIR, f"{file_hash}.wav")
        
        # If WAV file is already cached, return it
        if os.path.exists(cached_wav_path):
            logger.debug("Using cached WAV file")
            with open(cached_wav_path, 'rb') as f:
                cached_audio = f.read()
                if cached_audio:
                    return cached_audio
                else:
                    logger.warning("Cached file was empty. Regenerating...")

        # Convert MP3 to WAV
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp_mp3:
            tmp_mp3.write(audio_bytes)
            tmp_mp3_filename = tmp_mp3.name

        try:
            logger.debug("Attempting to read audio file")
            audio = AudioSegment.from_mp3(tmp_mp3_filename)
        except Exception as e:
            logger.warning(f"MP3 read failed: {str(e)}")
            audio = AudioSegment.from_file(tmp_mp3_filename)

        audio = audio.set_frame_rate(VAD_SAMPLING_RATE).set_channels(1)

        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_wav:
            logger.debug("Exporting to WAV format")
            audio.export(tmp_wav.name, format="wav")
            with open(tmp_wav.name, 'rb') as f:
                wav_data = f.read()
            
            # Cache the WAV file for future use
            with open(cached_wav_path, 'wb') as f:
                f.write(wav_data)

        logger.debug("Audio conversion completed successfully")
        os.unlink(tmp_mp3_filename)
        os.unlink(tmp_wav.name)
        return wav_data
    except Exception as e:
        logger.error(f"Error converting audio to WAV: {str(e)}")
        return None

def process_audio_with_vad(audio_bytes):
    """
    Process audio using WebRTC VAD for voice activity detection.
    """
    try:
        logger.debug("Starting VAD processing")
        # Convert bytes to numpy array
        audio = np.frombuffer(audio_bytes, dtype=np.int16)
        
        # Calculate number of frames
        frame_size = int(VAD_SAMPLING_RATE * VAD_FRAME_DURATION / 1000)
        frames = [audio[i:i+frame_size] for i in range(0, len(audio), frame_size)]
        logger.debug(f"Processing {len(frames)} audio frames")
        
        # Process each frame
        speech_frames = 0
        for frame in frames:
            # WebRTC VAD requires 16-bit mono PCM audio
            if len(frame) < frame_size:
                # Pad with zeros if last frame is too short
                frame = np.pad(frame, (0, frame_size - len(frame)), 'constant')
            
            # Convert to bytes
            frame_bytes = frame.tobytes()
            
            # Check if frame contains speech
            if vad.is_speech(frame_bytes, VAD_SAMPLING_RATE):
                speech_frames += 1
        
        # Calculate speech ratio
        speech_ratio = speech_frames / len(frames) if frames else 0
        has_speech = speech_ratio > 0.5
        logger.debug(f"VAD processing complete - Speech detected: {has_speech} (ratio: {speech_ratio:.2f})")
        return has_speech, speech_ratio
    except Exception as e:
        logger.error(f"Error in VAD processing: {e}", exc_info=True)
        return False, 0

def process_audio_from_base64(audio_data_base64):
    """
    Process the audio data (in base64 format) using WebRTC VAD.
    """
    try:
        logger.debug("Processing audio from base64")
        audio_bytes = base64.b64decode(audio_data_base64.split(',')[1])
        logger.debug(f"Decoded audio data length: {len(audio_bytes)} bytes")
        
        wav_data = convert_audio_to_wav(audio_bytes)
        if not wav_data:
            logger.warning("Audio conversion failed")
            return False, 0
        
        # Process with WebRTC VAD
        return process_audio_with_vad(wav_data)
    except Exception as e:
        logger.error(f"Error processing audio from base64: {str(e)}", exc_info=True)
        return False, 0
