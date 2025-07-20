from gtts import gTTS
import pygame
import os

class UrduTTS:
    def __init__(self):
        try:
            pygame.mixer.init()
        except pygame.error as e:
            print(f"[ERROR] pygame mixer init failed: {e}")

    def generate_audio(self, text, output_path):
        """Convert Urdu text to speech and save as MP3"""
        if not text.strip():
            raise ValueError("No text provided for TTS.")

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        try:
            tts = gTTS(text=text, lang='ur', slow=False)
            tts.save(output_path)
        except Exception as e:
            print(f"[ERROR] Failed to generate audio: {e}")
            raise

    def play_audio(self, audio_path):
        """Play the audio file"""
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        try:
            pygame.mixer.music.load(audio_path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
        except Exception as e:
            print(f"[ERROR] Failed to play audio: {e}")
        return self.segments[0]["text"].strip() if self.segments else ""
        return result["text"].strip()