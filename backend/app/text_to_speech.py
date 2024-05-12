import os
import uuid

from backend.app.melo.api import TTS


def generate_audio(text: str, language: str, speaker: str):
    """
    Generates audio from the given text.

    Args:
        language:
        speaker:
        text (str): The text to convert to audio.

    Returns:
        numpy.ndarray: The generated audio as a NumPy array.
    """

    # Speed is adjustable
    speed = 1.0

    # CPU is sufficient for real-time inference.
    # You can also change to cuda:0
    device = "cpu"

    model = TTS(language=language, device=device)
    speaker_ids = model.hps.data.spk2id
    # Generate a unique file name
    file_name = f"{uuid.uuid4()}.wav"
    output_file_path = os.path.join("data/audio", file_name)

    model.tts_to_file(text, speaker_ids[speaker], output_file_path, speed=speed)
    return output_file_path
