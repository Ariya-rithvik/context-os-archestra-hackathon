import os
import asyncio
import edge_tts
import speech_recognition as sr
from pydub import AudioSegment

# Create temp directory for audio files
TEMP_DIR = "temp_audio"
os.makedirs(TEMP_DIR, exist_ok=True)

class VoiceProcessor:
    """Handles Speech-to-Text (STT) and Text-to-Speech (TTS) using free tools."""
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.check_dependencies()

    def check_dependencies(self):
        """Verify that ffmpeg is installed and accessible."""
        from pydub import AudioSegment
        try:
            # Simple check to see if pydub can find ffmpeg/avconv
            from pydub.utils import which
            if not which("ffmpeg") and not which("avconv"):
                print("⚠️  WARNING: ffmpeg not found! Voice processing will fail.")
                print("   Please install ffmpeg and add it to your PATH.")
        except Exception as e:
             print(f"⚠️  Voice dependency check failed: {e}")
    
    def convert_ogg_to_wav(self, ogg_path: str) -> str:
        """Convert Telegram OGG audio to WAV for processing."""
        try:
            audio = AudioSegment.from_ogg(ogg_path)
            wav_path = ogg_path.replace(".ogg", ".wav")
            audio.export(wav_path, format="wav")
            return wav_path
        except Exception as e:
            print(f"❌ Error converting audio: {e}")
            return None

    def transcribe_audio(self, audio_path: str) -> str:
        """Convert Audio to Text using Google Speech Recognition (Free)."""
        try:
            # If OGG, convert to WAV first
            if audio_path.endswith(".ogg"):
                audio_path = self.convert_ogg_to_wav(audio_path)
                if not audio_path:
                    return "ERROR: conversion failed (ffmpeg missing?)"
            
            with sr.AudioFile(audio_path) as source:
                audio_data = self.recognizer.record(source)
                text = self.recognizer.recognize_google(audio_data)
                print(f"🎤 Voice transcribed: '{text}'")
                return text
        except sr.UnknownValueError:
            return "ERROR: could not understand audio"
        except sr.RequestError as e:
            return f"ERROR: Google Speech API error: {e}"
        except Exception as e:
            print(f"❌ Transcription error: {e}")
            return f"ERROR: {str(e)}"
        finally:
            # Cleanup WAV file if created
            if audio_path and audio_path.endswith(".wav") and os.path.exists(audio_path):
                try:
                    os.remove(audio_path)
                except:
                    pass

    async def text_to_speech(self, text: str, output_filename: str = "response.mp3") -> str:
        """Convert Text to Audio using Edge TTS (Free)."""
        output_path = os.path.join(TEMP_DIR, output_filename)
        try:
            # Voices: en-US-AriaNeural, en-US-GuyNeural, en-GB-SoniaNeural
            communicate = edge_tts.Communicate(text, "en-US-AriaNeural")
            await communicate.save(output_path)
            return output_path
        except Exception as e:
            print(f"❌ TTS Error: {e}")
            return None
