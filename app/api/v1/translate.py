from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.groq_translate import translate_with_groq
from app.services.tts_gemini import GeminiTTSService
import os
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

router = APIRouter()
tts_service = GeminiTTSService(api_key=os.getenv("GEMINI_API_KEY"))

class TranslateRequest(BaseModel):
    text: str
    target_language: str

class TranslateResponse(BaseModel):
    translated_text: str
    audio_file: str

@router.post("/", response_model=TranslateResponse)
async def translate_and_speak(req: TranslateRequest):
    try:
        logger.info(f"Translating text to {req.target_language}")
        translated = translate_with_groq(req.text, req.target_language)
        
        logger.info("Generating audio with Gemini TTS")
        audio_path = tts_service.synthesize_speech(
            text=translated,
            lang=req.target_language
        )
        
        return TranslateResponse(
            translated_text=translated,
            audio_file=audio_path
        )
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
