import io
import wave

import numpy as np
from lightning_whisper_mlx import LightningWhisperMLX

TRANSCRIPTION_MODEL = "distil-large-v3"


def transcribe(audio_dict, language) -> str:
    """Transcribe the audio data."""
    audio_data = np.array(audio_dict["audio"])
    sampling_rate = audio_dict["sampling_rate"]

    # Create a BytesIO object from the audio data
    audio_bytes = io.BytesIO()
    wave_writer = wave.open(audio_bytes, "wb")
    wave_writer.setnchannels(1)
    wave_writer.setsampwidth(2)  # 16-bit audio
    wave_writer.setframerate(sampling_rate)
    wave_writer.writeframes(audio_data.tobytes())
    wave_writer.close()
    audio_bytes.seek(0)

    whisper = LightningWhisperMLX(model=TRANSCRIPTION_MODEL, batch_size=12, quant=None)
    return whisper.transcribe(audio_path=audio_bytes, language=language)[
        "text"
    ]
