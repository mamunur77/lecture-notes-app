import os
from pydub import AudioSegment
import tempfile


def preprocess_audio(file_path: str, target_format: str = "wav") -> str:
    """
    Preprocesses audio for better Whisper accuracy:
    - Converts to WAV mono 16kHz (optimal for Whisper)
    - Handles video files by extracting audio
    - Normalizes volume

    Args:
        file_path: Path to original audio/video file
        target_format: Output format (wav recommended)

    Returns:
        Path to processed audio file
    """
    ext = os.path.splitext(file_path)[1].lower()

    # Load audio (pydub handles mp3, mp4, wav, m4a, ogg, flac, webm)
    try:
        if ext in [".mp4", ".webm", ".mkv"]:
            audio = AudioSegment.from_file(file_path, format=ext.strip("."))
        elif ext == ".mp3":
            audio = AudioSegment.from_mp3(file_path)
        elif ext == ".wav":
            audio = AudioSegment.from_wav(file_path)
        elif ext == ".m4a":
            audio = AudioSegment.from_file(file_path, format="m4a")
        elif ext == ".ogg":
            audio = AudioSegment.from_ogg(file_path)
        elif ext == ".flac":
            audio = AudioSegment.from_file(file_path, format="flac")
        else:
            audio = AudioSegment.from_file(file_path)
    except Exception as e:
        # If conversion fails, return original (Whisper may still handle it)
        print(f"Audio preprocessing warning: {e}. Using original file.")
        return file_path

    # Convert to mono (single channel - Whisper works best with mono)
    audio = audio.set_channels(1)

    # Set sample rate to 16kHz (Whisper's native rate)
    audio = audio.set_frame_rate(16000)

    # Normalize volume (helps with quiet recordings)
    audio = audio.normalize()

    # Export to temp file
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=f".{target_format}")
    audio.export(tmp.name, format=target_format)

    return tmp.name


def chunk_audio(file_path: str, chunk_duration_ms: int = 600000) -> list[str]:
    """
    Splits audio into chunks for long lectures (>10 min).
    Default chunk size = 10 minutes.

    Args:
        file_path: Path to processed audio
        chunk_duration_ms: Chunk size in milliseconds

    Returns:
        List of paths to chunked audio files
    """
    audio = AudioSegment.from_file(file_path)
    chunks = []

    for i, start in enumerate(range(0, len(audio), chunk_duration_ms)):
        chunk = audio[start:start + chunk_duration_ms]
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        chunk.export(tmp.name, format="wav")
        chunks.append(tmp.name)

    return chunks
