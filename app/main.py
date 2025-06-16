from fastapi import FastAPI
from app.api.v1.translate import router as translate_router

app = FastAPI(
    title="Gold Tongue AI Translator & Pronunciation Analyzer",
    version="1.0",
    description="Translate via Groq LLaMA 70B, TTS via Gemini, and Pronunciation Analysis via Whisper + LLaMA"
)

app.include_router(translate_router, prefix="/api/v1/translate")
