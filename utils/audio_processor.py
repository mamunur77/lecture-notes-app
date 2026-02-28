def preprocess_audio(file_path: str) -> str:
    """
    Returns the file as-is for Whisper processing.
    Groq Whisper handles all audio formats natively.
    """
    return file_path


def chunk_audio(file_path: str, chunk_duration_ms: int = 600000) -> list:
    """
    Returns single file as a list.
    """
    return [file_path]
