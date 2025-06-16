from openai import OpenAI
import os
import json
from dotenv import load_dotenv
import pyaudio
import wave
import uuid
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

load_dotenv()

router = APIRouter()

class PronunciationService:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("GROQ_API_KEY"),
            base_url=os.getenv("GROQ_ENDPOINT")
        )
        self.chunk = 1024
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 16000
        self.record_seconds = 5
        
        # Language codes mapping
        self.language_codes = {
            "English": "en",
            "Bengali": "bn",
            "Hindi": "hi",
            "Japanese": "ja",
            "Chinese": "zh",
            "Korean": "ko",
            "Arabic": "ar",
            "French": "fr",
            "German": "de",
            "Spanish": "es"
        }

    def record_speech(self, output_dir="recordings") -> str:
        """Record audio from microphone"""
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, f"recording_{uuid.uuid4().hex}.wav")
        
        p = pyaudio.PyAudio()
        stream = p.open(format=self.format,
                       channels=self.channels,
                       rate=self.rate,
                       input=True,
                       frames_per_buffer=self.chunk)

        print("\n=== Recording Started ===")
        print("Speak now... Recording for 5 seconds")
        
        frames = []
        for i in range(0, int(self.rate / self.chunk * self.record_seconds)):
            data = stream.read(self.chunk)
            frames.append(data)
            if i % 10 == 0:
                print(".", end="", flush=True)

        print("\n=== Recording Complete ===")
        stream.stop_stream()
        stream.close()
        p.terminate()

        with wave.open(output_file, 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(p.get_sample_size(self.format))
            wf.setframerate(self.rate)
            wf.writeframes(b''.join(frames))

        return output_file

    def transcribe_audio(self, audio_file: str, language: str = "en") -> str:
        """Transcribe audio using Whisper via Groq"""
        try:
            with open(audio_file, "rb") as audio:
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-large-v3",
                    file=audio,
                    language=language,
                    response_format="text"
                )
            return transcript
        except Exception as e:
            raise Exception(f"Transcription error: {str(e)}")

    def detect_language(self, audio_file: str) -> tuple:
        """Detect language from audio using Whisper"""
        try:
            with open(audio_file, "rb") as audio:
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-large-v3",
                    file=audio,
                    response_format="verbose_json"
                )
            return transcript.language, transcript.text
        except Exception as e:
            raise Exception(f"Language detection error: {str(e)}")

    def convert_script(self, text: str, detected_language: str) -> str:
        """Convert text to appropriate script if needed"""
        try:
            if detected_language in ["bn", "hi", "ja", "zh", "ko", "ar","en", "fr", "de", "es"]:
                prompt = f"""Convert this text to proper {detected_language} script:
                Text: "{text}"
                Return only the converted text in the appropriate script, nothing else."""
                
                response = self.client.chat.completions.create(
                    model="llama3-70b-8192",
                    messages=[
                        {"role": "system", "content": "You are a language expert. Convert text to the appropriate script."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1
                )
                
                return response.choices[0].message.content.strip()
            return text  # Return original text for languages using Latin script
            
        except Exception as e:
            print(f"Script conversion error: {str(e)}")
            return text

    def analyze_pronunciation(self, text: str, language: str) -> dict:
        """Analyze pronunciation using LLaMA"""
        try:
            prompt = f"""Analyze the pronunciation quality of this transcribed speech in {language}.
            
            Speech Text: "{text}"
            Language: {language}
            
            Return a JSON object with:
            {{
                "score": <number 0-100>,
                "pronunciation_issues": [<specific issues in {language} context>],
                "improvement_suggestions": [<language-specific suggestions>]
            }}
            """

            response = self.client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[
                    {"role": "system", "content": f"You are a {language} pronunciation expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )

            return json.loads(response.choices[0].message.content)

        except Exception as e:
            return {
                "score": 50,
                "pronunciation_issues": [f"Analysis error: {str(e)}"],
                "improvement_suggestions": ["Please try speaking again"]
            }

    def evaluate_speech(self) -> dict:
        """Complete process: Record, Transcribe, Analyze with language detection"""
        try:
            # Record speech
            audio_file = self.record_speech()
            print(f"\nRecording saved as: {audio_file}")
            print("\nDetecting language and transcribing...")
            
            # Detect language and transcribe
            detected_lang_code, transcribed_text = self.detect_language(audio_file)
            
            # Convert language code to full name
            detected_language = next(
                (lang for lang, code in self.language_codes.items() 
                 if code == detected_lang_code), 
                "Unknown"
            )
            
            # Convert to appropriate script if needed
            transcribed_text = self.convert_script(transcribed_text, detected_lang_code)
            
            print(f"\n=== Detected Language: {detected_language} ===")
            print(f"=== Transcribed Text ===")
            print(transcribed_text)
            print(f"\nAnalyzing pronunciation...")
            
            # Analyze using LLaMA
            analysis = self.analyze_pronunciation(transcribed_text, detected_language)
            
            return {
                "audio_file": audio_file,
                "transcribed_text": transcribed_text,
                "language": detected_language,
                "score": analysis["score"],
                "pronunciation_issues": analysis["pronunciation_issues"],
                "improvement_suggestions": analysis["improvement_suggestions"]
            }
            
        except Exception as e:
            raise Exception(f"Evaluation error: {str(e)}")

class PronunciationResponse(BaseModel):
    audio_file: str  # Added audio file path
    transcribed_text: str
    score: float
    pronunciation_issues: List[str]
    improvement_suggestions: List[str]

@router.post("/analyze-speech", response_model=PronunciationResponse)
async def analyze_speech():
    try:
        analyzer = PronunciationService()
        result = analyzer.evaluate_speech()
        
        print(f"\n=== Analysis Complete ===")
        print(f"Recording file: {result['audio_file']}")
        print(f"Transcribed text: {result['transcribed_text']}")
        print(f"Score: {result['score']}/100")
        
        return PronunciationResponse(
            audio_file=result["audio_file"],
            transcribed_text=result["transcribed_text"],
            score=result["score"],
            pronunciation_issues=result["pronunciation_issues"],
            improvement_suggestions=result["improvement_suggestions"]
        )
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))