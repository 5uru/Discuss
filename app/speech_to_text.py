import mlx_whisper

TRANSCRIPTION_MODEL = "mlx-community/whisper-small-mlx-8bit"


def transcribe(speech_file) -> str:
    """
    Transcribe the audio file at the given path.
    """
    return mlx_whisper.transcribe(
        speech_file,
        path_or_hf_repo=TRANSCRIPTION_MODEL,
    )["text"]
