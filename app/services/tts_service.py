from gtts import gTTS
import os
import uuid

def synthesize_speech(text: str, lang: str, out_dir="output") -> str:
    """
    Convert text to speech using gTTS
    Supported languages: https://gtts.readthedocs.io/en/latest/#lang-list
    """
    try:
        # Map full language names to language codes
        language_map = {
            "English": "en",
            "French": "fr",
            "German": "de",
            "Spanish": "es",
            "Italian": "it",
            "Japanese": "ja",
            "Chinese": "zh",
            "Hindi": "hi",
            "Bengali": "bn"
        }
        
        lang_code = language_map.get(lang, "en")
        tts = gTTS(text=text, lang=lang_code, slow=False)
        
        os.makedirs(out_dir, exist_ok=True)
        output_file = os.path.join(out_dir, f"ttsaudio_{uuid.uuid4().hex}.mp3")
        
        tts.save(output_file)
        return output_file
    
    except Exception as e:
        raise Exception(f"TTS Error: {str(e)}")