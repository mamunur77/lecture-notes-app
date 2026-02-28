import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

LANGUAGE_MAP = {
    "English": "en",
    "Hindi": "hi",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Auto Detect": None
}


def transcribe_audio(file_path: str, model: str = None, language: str = "English") -> str:
    lang = LANGUAGE_MAP.get(language)

    with open(file_path, "rb") as f:
        response = client.audio.transcriptions.create(
            file=f,
            model="whisper-large-v3",
            language=lang,
            response_format="text"
        )

    return response.strip()