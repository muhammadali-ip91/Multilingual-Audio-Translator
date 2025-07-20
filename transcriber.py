# transcriber.py
import whisper
import torch

# class AudioTranscriber:
#     def __init__(self, model_size="large-v3"):
#         self.model = self._load_model(model_size)


class AudioTranscriber:
    def __init__(self, model_size="large-v3"):
        self.model = self._load_model(model_size)
    
    def _load_model(self, model_size):
        device = "cuda" if torch.cuda.is_available() else "cpu"
        return whisper.load_model(model_size, device=device)

    def transcribe_segments(self, audio_path):
        """Return segments with time info and text"""
        result = self.model.transcribe(audio_path, fp16=False)
        return [
            {"start_time": self._format_time(seg["start"]), "text": seg["text"]}
            for seg in result["segments"]
        ]

    def _format_time(self, seconds):
        return f"{int(seconds // 60):02d}:{int(seconds % 60):02d}"
