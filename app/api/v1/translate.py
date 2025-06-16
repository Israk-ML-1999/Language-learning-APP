from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from app.services.groq_translate import translate_with_groq
from app.services.tts_gemini import GeminiTTSService
from app.services.pronunciation_service import PronunciationService
import os
from dotenv import load_dotenv
import logging

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

class PronunciationResponse(BaseModel):
    transcribed_text: str
    score: float
    pronunciation_issues: List[str]
    improvement_suggestions: List[str]

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

@router.post("/analyze-speech", response_model=PronunciationResponse)
async def analyze_speech():
    try:
        analyzer = PronunciationService()
        result = analyzer.evaluate_speech()
        
        print(f"\n=== Analysis Complete ===")
        print(f"Score: {result['score']}/100")
        
        return PronunciationResponse(
            transcribed_text=result["transcribed_text"],
            score=result["score"],
            pronunciation_issues=result["pronunciation_issues"],
            improvement_suggestions=result["improvement_suggestions"]
        )
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
