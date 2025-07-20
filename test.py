import os
from transcriber import AudioTranscriber
from translator import TextTranslator
from tts_engine import UrduTTS

# Test paths
TEST_AUDIO = "D:/audio/ans.mp3"  # Create a short test file
OUTPUT_DIR = "output/"

def test_transcription():
    print("Testing transcription...")
    transcriber = AudioTranscriber()
    result = transcriber.transcribe(TEST_AUDIO)
    print(f"Result: {result[:50]}...")
    return bool(result.strip())

def test_translation():
    print("Testing translation...")
    translator = TextTranslator()
    result = translator.translate_to_urdu("Hello world")
    print(f"Urdu: {result}")
    return bool(result.strip())

def test_tts():
    print("Testing TTS...")
    tts = UrduTTS()
    output_path = os.path.join(OUTPUT_DIR, "test_output.mp3")
    tts.generate_audio("آزمائش", output_path)
    exists = os.path.exists(output_path)
    print(f"File created: {exists}")
    return exists

if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    tests = {
        "Transcription": test_transcription,
        "Translation": test_translation,
        "TTS": test_tts
    }
    
    for name, test in tests.items():
        print(f"\n{'='*30}\n{name} TEST\n{'='*30}")
        success = test()
        print(f"✅ {name} Passed" if success else f"❌ {name} Failed")