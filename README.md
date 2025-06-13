# Gold Tongue AI Translator

A FastAPI-based translation and text-to-speech service using Groq LLaMA and Gemini TTS.

## Features

- Text translation using Groq LLaMA 70B model
- Text-to-speech using Gemini TTS
- Support for multiple languages
- Native accent preservation
- FastAPI-based REST API

## Setup

1. Clone the repository:
```bash
git clone https://github.com/Israk-ML-1999/Language-learning-APP.git
```

2. Create a virtual environment:
```bash
python -m venv venv
venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file with your API keys:
```env
GROQ_API_KEY=your_groq_api_key
GROQ_ENDPOINT=https://api.groq.com/openai/v1
GEMINI_API_KEY=your_gemini_api_key
```

## Usage

1. Start the server:
```bash
uvicorn app.main:app --reload
```

2. Access the API documentation at: http://localhost:8000/docs

## API Endpoints

- `POST /api/v1/translate/`: Translate text and generate speech
  - Request body:
    ```json
    {
        "text": "Hello world",
        "target_language": "French"
    }
    ```

## Tech Stack

- FastAPI
- Groq LLaMA 70B
- Gemini TTS
- Python 3.8+

## License

MIT