import torch
from parler_tts import ParlerTTSForConditionalGeneration
from transformers import AutoTokenizer


def generate_audio(text: str, description: str, tts_models: str) -> dict:
    """
    Generates audio from the given text.

    Args:
        tts_models:
        description:
        text (str): The text to convert to audio.

    Returns:
        numpy.ndarray: The generated audio as a NumPy array.
    """
    device = "cuda:0" if torch.cuda.is_available() else "cpu"

    model = ParlerTTSForConditionalGeneration.from_pretrained(tts_models).to(device)
    tokenizer = AutoTokenizer.from_pretrained(tts_models)

    input_ids = tokenizer(description, return_tensors="pt").input_ids.to(device)
    prompt_input_ids = tokenizer(text, return_tensors="pt").input_ids.to(device)

    generation = model.generate(input_ids=input_ids, prompt_input_ids=prompt_input_ids)
    audio_arr = generation.cpu().numpy().squeeze()
    return {"audio": audio_arr.tolist(), "sampling_rate": model.config.sampling_rate}
