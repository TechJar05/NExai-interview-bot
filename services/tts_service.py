# services/tts_service.py
import base64
import os
import logging
import hashlib
import time
from gtts import gTTS
from gtts.tts import gTTSError

logger = logging.getLogger(__name__)

# Cache directory for audio files
CACHE_DIR = os.path.join(os.getcwd(), 'tts_cache')
os.makedirs(CACHE_DIR, exist_ok=True)

def text_to_speech(text: str) -> str:
    """
    Converts input text to speech using Google Text-to-Speech (gTTS),
    caches the audio, and returns it as a base64-encoded string.
    Includes retry logic, file integrity checks, and logging.
    """
    logger.debug(f"Converting text to speech: {text[:50]}...")

    try:
        # Generate a unique hash for the text
        file_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
        cached_file_path = os.path.join(CACHE_DIR, f"{file_hash}.mp3")

        # Return cached audio if it exists and is valid
        if os.path.exists(cached_file_path):
            with open(cached_file_path, 'rb') as f:
                cached_audio = f.read()
                if cached_audio:
                    logger.debug("Using cached audio file")
                    return base64.b64encode(cached_audio).decode('utf-8')
                else:
                    logger.warning("Cached file was empty. Regenerating...")

        # Retry logic for gTTS
        retries = 3
        delay = 1.5
        for attempt in range(retries):
            try:
                tts = gTTS(text=text, lang='en', slow=False)
                tts.save(cached_file_path)
                logger.info(f"TTS generated and saved (attempt {attempt + 1})")
                break  # Exit loop if successful
            except gTTSError as e:
                logger.warning(f"gTTS error (attempt {attempt + 1}): {str(e)}")
                time.sleep(delay)
            except Exception as e:
                logger.error(f"Unexpected error during TTS (attempt {attempt + 1}): {e}", exc_info=True)
                time.sleep(delay)
        else:
            logger.error("❌ TTS generation failed after all retries")
            return None

        # Read and return base64 audio
        with open(cached_file_path, 'rb') as f:
            audio_data = f.read()
            if not audio_data:
                logger.error("TTS file saved but is empty.")
                return None

        logger.debug("Successfully generated and cached new audio")
        return base64.b64encode(audio_data).decode('utf-8')

    except Exception as e:
        logger.error(f"Unhandled exception in text_to_speech: {str(e)}", exc_info=True)
        return None
