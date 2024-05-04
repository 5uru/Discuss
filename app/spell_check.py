import Levenshtein as lev
from transformers import AutoTokenizer, T5ForConditionalGeneration


def calculate_overall_similarity_score(
    original, grammar_corrected, coherence_corrected, rewritten
):
    grammar_similarity = 1 - lev.distance(original, grammar_corrected) / max(
        len(original), len(grammar_corrected)
    )
    coherence_similarity = 1 - lev.distance(original, coherence_corrected) / max(
        len(original), len(coherence_corrected)
    )
    rewritten_similarity = 1 - lev.distance(original, rewritten) / max(
        len(original), len(rewritten)
    )

    # Calcul de la moyenne des scores de similarité
    average_similarity = (
        grammar_similarity + coherence_similarity + rewritten_similarity
    ) / 3

    return int(average_similarity * 100)


tokenizer = AutoTokenizer.from_pretrained("grammarly/coedit-large")
model = T5ForConditionalGeneration.from_pretrained("grammarly/coedit-large")


def process_text(text, task_type):
    """
    Process the given text based on the task type.

    Args:
        text (str): The text to process.
        task_type (str): The type of task to perform on the text.

    Returns:
        str: The processed text.
    """
    task_prefixes = {
        "grammar_correction": "Fix grammatical errors in this sentence:",
        "coherence_correction": "Make this text coherent:",
        "rewrite_text": "Rewrite to make this easier to understand:",
    }
    input_text = f"{task_prefixes[task_type]} {text}"  # prepend the task prefix
    input_ids = tokenizer(input_text, return_tensors="pt").input_ids
    outputs = model.generate(input_ids, max_length=1000)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)


def grammar_coherence_correction(text):
    """
    Combine grammar correction, coherence correction, and text rewriting.

    Args:
        text (str): The text to process.

    Returns:
        dict: A dictionary containing the score, grammar corrected text, coherence corrected text, and rewritten text.
    """
    grammar_corrected = process_text(text, "grammar_correction")
    coherence_corrected = process_text(grammar_corrected, "coherence_correction")
    rewritten = process_text(coherence_corrected, "rewrite_text")
    # calculate the difference between texts
    score = calculate_overall_similarity_score(
        text, grammar_corrected, coherence_corrected, rewritten
    )
    return {
        "score": score,
        "grammar_corrected": grammar_corrected,
        "coherence_corrected": coherence_corrected,
        "rewritten": rewritten,
        "original": text,
    }
