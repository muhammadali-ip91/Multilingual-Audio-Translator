from deep_translator import GoogleTranslator
import langdetect

class TextTranslator:
    def translate_to_urdu(self, text):
        """Translate multi-language text to Urdu line-by-line."""
        lines = text.splitlines()
        translated_lines = []

        for line in lines:
            if not line.strip():
                continue  # skip empty lines

            try:
                detected_lang = langdetect.detect(line)
            except:
                detected_lang = 'en'  # default fallback

            try:
                if detected_lang == 'ur':
                    translated_lines.append(line)  # no translation needed
                else:
                    translated = GoogleTranslator(source=detected_lang, target='ur').translate(line)
                    translated_lines.append(translated)
            except Exception as e:
                translated_lines.append(f"[ترجمہ ناکام: {str(e)}]")

        return "\n".join(translated_lines)
