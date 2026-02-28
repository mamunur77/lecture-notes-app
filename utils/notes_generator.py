import requests
import os
import json
import re
from dotenv import load_dotenv

load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

FREE_MODELS = [
    "openrouter/auto",
    "meta-llama/llama-3.3-70b-instruct:free",
    "google/gemma-3-27b-it:free",
    "google/gemma-3-12b-it:free",
    "deepseek/deepseek-r1:free",
    "mistralai/mistral-7b-instruct:free",
    "meta-llama/llama-3.2-3b-instruct:free"
]


def _call_openrouter(prompt: str) -> str:
    for model in FREE_MODELS:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}]
            },
            timeout=60
        )
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"].strip()
        elif response.status_code in [429, 400, 404]:
            continue  # Try next model
        else:
            raise RuntimeError(f"OpenRouter error {response.status_code}: {response.text}")

    raise RuntimeError("All free models are unavailable. Please wait a minute and try again.")


def generate_notes(transcript: str, subject_hint: str = "") -> str:
    subject_context = f"The subject is: {subject_hint}." if subject_hint else ""
    prompt = f"""
You are an expert academic note-taker. {subject_context}

Below is a raw lecture transcript that may contain filler words, repetitions, or minor transcription errors.
Your job is to:
1. Fix any obvious transcription errors based on context
2. Remove filler words (umm, uh, like, you know)
3. Create well-structured, clean lecture notes with:
   - A clear Title
   - Key Topics covered (as sections with headings)
   - Important concepts explained clearly
   - Examples mentioned in the lecture
   - Summary at the end

Format using Markdown. Be concise but comprehensive.

TRANSCRIPT:
{transcript}
"""
    return _call_openrouter(prompt)


def generate_flashcards(transcript: str, subject_hint: str = "") -> list[dict]:
    subject_context = f"The subject is: {subject_hint}." if subject_hint else ""
    prompt = f"""
You are creating study flashcards from a lecture transcript. {subject_context}

Generate 8-12 flashcards from the key concepts in this transcript.
Return ONLY a valid JSON array like this (no extra text, no markdown):
[
  {{"question": "What is ...?", "answer": "..."}},
  {{"question": "Define ...", "answer": "..."}}
]

TRANSCRIPT:
{transcript}
"""
    raw = _call_openrouter(prompt)
    raw = re.sub(r"```json|```", "", raw).strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return [{"question": "Could not parse flashcards", "answer": raw[:200]}]


def generate_quiz(transcript: str, subject_hint: str = "") -> list[dict]:
    subject_context = f"The subject is: {subject_hint}." if subject_hint else ""
    prompt = f"""
Create a multiple choice quiz from this lecture transcript. {subject_context}

Generate 5-8 MCQ questions. Return ONLY a valid JSON array (no extra text, no markdown):
[
  {{
    "question": "What is ...?",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "answer": "Option A"
  }}
]

Make sure the answer exactly matches one of the options.

TRANSCRIPT:
{transcript}
"""
    raw = _call_openrouter(prompt)
    raw = re.sub(r"```json|```", "", raw).strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return [{"question": "Could not parse quiz", "options": ["N/A"], "answer": "N/A"}]


def generate_glossary(transcript: str, subject_hint: str = "") -> dict:
    subject_context = f"The subject is: {subject_hint}." if subject_hint else ""
    prompt = f"""
Extract key technical terms and concepts from this lecture transcript and define them simply. {subject_context}

Return ONLY a valid JSON object (no extra text, no markdown):
{{
  "Term 1": "Simple definition...",
  "Term 2": "Simple definition..."
}}

Extract 8-15 important terms.

TRANSCRIPT:
{transcript}
"""
    raw = _call_openrouter(prompt)
    raw = re.sub(r"```json|```", "", raw).strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"Error": "Could not parse glossary"}