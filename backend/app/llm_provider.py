from mlx_lm import load, generate


LLM_MODEL = "mlx-community/Meta-Llama-3-8B-Instruct-4bit"


def generation(text, llm_model=LLM_MODEL):
    model_config = {
        "verbose": True,
        "temp": 0.7,
        "max_tokens": 4000,
        "repetition_penalty": 1.1,
    }
    model, tokenizer = load(llm_model)
    return generate(model, tokenizer, prompt=text, **model_config)
