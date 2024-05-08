from mlx_lm import load, generate


LLM_MODEL = "mlx-community/Meta-Llama-3-8B-Instruct-4bit"


def generation(text):
    model_config = {
        "verbose": True,
        "temp": 0.7,
        "max_tokens": 4000,
        "repetition_penalty": 1.1,
    }
    model, tokenizer = load(LLM_MODEL)
    return generate(model, tokenizer, prompt=text, **model_config)
