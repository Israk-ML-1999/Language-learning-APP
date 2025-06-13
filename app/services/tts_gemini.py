from google import genai
from google.genai import types
import wave
import os
import uuid

class GeminiTTSService:
    def __init__(self, api_key):
        self.client = genai.Client(api_key=api_key)
        
        # Updated voice mapping with supported Gemini voices
        self.voice_map = {
            "English": "kore",
            "French": "algieba",
            "German": "enceladus",
            "Spanish": "callirrhoe",
            "Italian": "gacrux",
            "Japanese": "charon",
            "Chinese": "fenrir",
            "Hindi": "sadachbia",
            "Bengali": "puck"
        }
    
    def _save_wave_file(self, filename, pcm, channels=1, rate=24000, sample_width=2):
        with wave.open(filename, "wb") as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(sample_width)
            wf.setframerate(rate)
            wf.writeframes(pcm)

    def synthesize_speech(self, text: str, lang: str, out_dir="output") -> str:
        try:
            os.makedirs(out_dir, exist_ok=True)
            output_file = os.path.join(out_dir, f"ttsaudio_{uuid.uuid4().hex}.wav")
            
            voice_name = self.voice_map.get(lang, "kore")  # Default to kore if language not found
            
            # Configure TTS request
            response = self.client.models.generate_content(
                model="gemini-2.5-flash-preview-tts",
                contents=text,
                config=types.GenerateContentConfig(
                    response_modalities=["AUDIO"],
                    speech_config=types.SpeechConfig(
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                voice_name=voice_name.lower()  # Ensure lowercase
                            )
                        )
                    )
                )
            )
            
            # Extract audio data
            audio_data = response.candidates[0].content.parts[0].inline_data.data
            
            # Save to file
            self._save_wave_file(output_file, audio_data)
            
            return output_file
            
        except Exception as e:
            raise Exception(f"Gemini TTS Error: {str(e)}")