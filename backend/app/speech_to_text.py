import librosa
from lightning_whisper_mlx import LightningWhisperMLX

TRANSCRIPTION_MODEL = "distil-large-v3"


def audio_to_ndarray(audio_file_path):
    # Load the audio file
    audio_data, sampling_rate = librosa.load(audio_file_path, sr=None)
    return audio_data, sampling_rate


def transcribe(speech_file, language) -> str:
    """
    Transcribe the audio file at the given path.
    """
    whisper = LightningWhisperMLX(model=TRANSCRIPTION_MODEL, batch_size=12, quant=None)
    return whisper.transcribe(audio_path=speech_file, language=language)["text"]
