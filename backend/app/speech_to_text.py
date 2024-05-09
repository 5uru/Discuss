from lightning_whisper_mlx import LightningWhisperMLX

TRANSCRIPTION_MODEL = "distil-large-v3"


def transcribe(file_path, language) -> str:
    whisper = LightningWhisperMLX(model=TRANSCRIPTION_MODEL, batch_size=12, quant=None)
    return whisper.transcribe(audio_path=file_path, language=language)["text"]
