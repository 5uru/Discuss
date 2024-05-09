import torch
from parler_tts import ParlerTTSForConditionalGeneration
from transformers import AutoTokenizer

DEFAULT_DESCRIPTION = "A female speaker with a slightly low-pitched voice delivers her words quite expressively, in a very confined sounding environment with clear audio quality."
TTS_MODEL = "parler-tts/parler_tts_mini_v0.1"


def generate_audio(text: str, description: str = DEFAULT_DESCRIPTION) -> dict:
    """
    Generates audio from the given text.

    Args:
        description:
        text (str): The text to convert to audio.

    Returns:
        numpy.ndarray: The generated audio as a NumPy array.
    """
    device = "cuda:0" if torch.cuda.is_available() else "cpu"

    model = ParlerTTSForConditionalGeneration.from_pretrained(TTS_MODEL).to(device)
    tokenizer = AutoTokenizer.from_pretrained(TTS_MODEL)

    input_ids = tokenizer(description, return_tensors="pt").input_ids.to(device)
    prompt_input_ids = tokenizer(text, return_tensors="pt").input_ids.to(device)

    generation = model.generate(input_ids=input_ids, prompt_input_ids=prompt_input_ids)
    audio_arr = generation.cpu().numpy().squeeze()
    return {"audio": audio_arr.tolist(), "sampling_rate": model.config.sampling_rate}
