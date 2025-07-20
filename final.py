import customtkinter as ctk
import threading
import os
import whisper
import torch
from gtts import gTTS
import pygame
from deep_translator import GoogleTranslator
import langdetect


class AudioTranscriber:
    def __init__(self, model_size="large-v3"):
        self.model = self._load_model(model_size)

    def _load_model(self, model_size):
        device = "cuda" if torch.cuda.is_available() else "cpu"
        return whisper.load_model(model_size, device=device)

    def transcribe_segments(self, audio_path):
        result = self.model.transcribe(audio_path, fp16=False)
        return [
            {"start_time": self._format_time(seg["start"]), "text": seg["text"]}
            for seg in result["segments"]
        ]

    def _format_time(self, seconds):
        return f"{int(seconds // 60):02d}:{int(seconds % 60):02d}"


class TextTranslator:
    def translate_to_urdu(self, text):
        lines = text.splitlines()
        translated_lines = []

        for line in lines:
            if not line.strip():
                continue

            try:
                detected_lang = langdetect.detect(line)
            except:
                detected_lang = 'en'

            try:
                if detected_lang == 'ur':
                    translated_lines.append(line)
                else:
                    translated = GoogleTranslator(source=detected_lang, target='ur').translate(line)
                    translated_lines.append(translated)
            except Exception as e:
                translated_lines.append(f"[\u062a\u0631\u062c\u0645\u06c1 \u0646\u0627\u06a9\u0627\u0645: {str(e)}]")

        return "\n".join(translated_lines)


class UrduTTS:
    def __init__(self):
        try:
            pygame.mixer.init()
        except pygame.error as e:
            print(f"[ERROR] pygame mixer init failed: {e}")

    def generate_audio(self, text, output_path):
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
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        try:
            pygame.mixer.music.load(audio_path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
        except Exception as e:
            print(f"[ERROR] Failed to play audio: {e}")


class AudioTranslatorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Multilingual Audio Translator")
        self.geometry("1000x700")
        self._setup_ui()

        self.transcriber = AudioTranscriber()
        self.translator = TextTranslator()
        self.tts = UrduTTS()
        self.audio_filepath = ""
        self.urdu_segments = []
        self.output_dir = "output/"

    def _setup_ui(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.header = ctk.CTkLabel(self, text="Audio Translator to Urdu", font=("Arial", 24, "bold"))
        self.header.pack(pady=20)

        self.upload_frame = ctk.CTkFrame(self)
        self.upload_frame.pack(fill="x", padx=50, pady=10)
        self.btn_upload = ctk.CTkButton(self.upload_frame, text="Upload Audio File", command=self._upload_audio)
        self.btn_upload.pack(pady=15)

        self.progress = ctk.CTkProgressBar(self, height=20, width=800)
        self.progress.pack(pady=10)
        self.progress.set(0)

        self.status_label = ctk.CTkLabel(self, text="Ready to process", text_color="lightblue")
        self.status_label.pack()

        self.result_tabs = ctk.CTkTabview(self)
        self.result_tabs.pack(expand=True, fill="both", padx=50, pady=20)

        self.original_tab = self.result_tabs.add("Original Text")
        self.translated_tab = self.result_tabs.add("Urdu Translation")

        self.original_text = ctk.CTkTextbox(self.original_tab, wrap="word")
        self.original_text.pack(expand=True, fill="both")

        self.translated_text = ctk.CTkTextbox(self.translated_tab, wrap="word", font=("Nafees Nastaleeq", 16))
        self.translated_text.pack(expand=True, fill="both")

        self.action_frame = ctk.CTkFrame(self)
        self.action_frame.pack(pady=20)
        self.btn_process = ctk.CTkButton(self.action_frame, text="Process Audio", command=self._start_processing)
        self.btn_play = ctk.CTkButton(self.action_frame, text="Play Urdu Audio", command=self._play_all_segments, state="disabled")
        self.btn_save = ctk.CTkButton(self.action_frame, text="Save Results", command=self._save_results)

        self.btn_process.pack(side="left", padx=20)
        self.btn_play.pack(side="left", padx=20)
        self.btn_save.pack(side="left", padx=20)

    def _upload_audio(self):
        filepath = ctk.filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3 *.wav *.ogg *.m4a")])
        if filepath:
            self.audio_filepath = filepath
            self.status_label.configure(text=f"Selected: {os.path.basename(filepath)}")
            self.btn_process.configure(state="normal")

    def _start_processing(self):
        if not self.audio_filepath:
            return
        self.btn_process.configure(state="disabled")
        threading.Thread(target=self._processing_pipeline, daemon=True).start()

    def _processing_pipeline(self):
        try:
            self._update_status("Transcribing audio...", 0.2)
            segments = self.transcriber.transcribe_segments(self.audio_filepath)
            full_original = []
            full_urdu = []
            self.urdu_segments.clear()
            self._update_status("Translating segments...", 0.5)

            for idx, seg in enumerate(segments):
                full_original.append(f"[{seg['start_time']}] {seg['text']}")
                urdu = self.translator.translate_to_urdu(seg["text"])
                self.urdu_segments.append({"urdu": urdu, "index": idx})
                full_urdu.append(f"[{seg['start_time']}] {urdu}")

            self.original_text.insert("1.0", "\n\n".join(full_original))
            self.translated_text.insert("1.0", "\n\n".join(full_urdu))

            self._update_status("Ready to speak Urdu!", 1.0)
            self.btn_play.configure(state="normal")

        except Exception as e:
            self._update_status(f"Error: {str(e)}", 0)
            self.btn_process.configure(state="normal")

    def _update_status(self, message, progress):
        self.status_label.configure(text=message)
        self.progress.set(progress)
        self.update_idletasks()

    def _play_all_segments(self):
        self._update_status("Speaking Urdu translation...", 0.9)
        os.makedirs(self.output_dir, exist_ok=True)

        for i, item in enumerate(self.urdu_segments):
            text = item["urdu"]
            output_path = os.path.join(self.output_dir, f"segment_{i+1}.mp3")
            try:
                self.tts.generate_audio(text, output_path)
                self.tts.play_audio(output_path)
            except Exception as e:
                print(f"[ERROR] Segment {i+1} failed: {e}")

        self._update_status("Finished playing all Urdu segments.", 1.0)

    def _save_results(self):
        pass


if __name__ == "__main__":
    app = AudioTranslatorApp()
    app.mainloop()
