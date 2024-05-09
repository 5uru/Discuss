import tempfile

import numpy as np
import soundfile as sf
from lightning_whisper_mlx import LightningWhisperMLX

TRANSCRIPTION_MODEL = "distil-large-v3"


def transcribe(audio_dict, language) -> str:
    """Transcribe the audio data."""
    audio_data = np.array(audio_dict["audio"])
    sampling_rate = audio_dict["sampling_rate"]

    # Save the audio data to a temporary file
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as temp_audio_file:
        sf.write(temp_audio_file.name, audio_data, samplerate=sampling_rate)

        whisper = LightningWhisperMLX(
            model=TRANSCRIPTION_MODEL, batch_size=12, quant=None
        )
        return whisper.transcribe(audio_path=temp_audio_file.name, language=language)[
            "text"
        ]
