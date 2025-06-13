from fastapi import FastAPI
from app.api.v1.translate import router as translate_router




app = FastAPI(
    title="Gold Tongue AI Translator",
    version="1.0",
    description="Translate via Groq LLaMA 70B and TTS via Gemini‑2.5‑flash‑preview voice"
)

app.include_router(translate_router, prefix="/api/v1/translate")
