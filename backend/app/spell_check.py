import translators as ts
from Levenshtein import distance as levenshtein_distance
from language_tool_python import LanguageTool
from nltk.translate.bleu_score import sentence_bleu
from sklearn.feature_extraction.text import TfidfVectorizer


def translate(text, to_language="en"):
    return ts.translate_text(text, to_language=to_language)


def grammar_check(text, language="en-US"):
    tool = LanguageTool(language)
    return tool.correct(text)


def combined_similarity_score(sentence1, sentence2):
    # Tokenize sentences
    tokens1 = sentence1.split()
    tokens2 = sentence2.split()

    # BLEU Score
    bleu_score = sentence_bleu([tokens1], tokens2)

    # Levenshtein Distance
    lev_distance = levenshtein_distance(sentence1, sentence2)
    max_len = max(len(sentence1), len(sentence2))
    normalized_lev = 1 - lev_distance / max_len

    # Cosine Similarity
    vectorized = TfidfVectorizer()
    tfidf = vectorized.fit_transform([sentence1, sentence2])
    cosine_sim = (tfidf * tfidf.T).A[0, 1]

    # Combined Score
    combined_score = (bleu_score + normalized_lev + cosine_sim) / 3
    return int(combined_score * 100)


def grammar_coherence_correction(text, language):
    """
    Combine grammar correction, coherence correction, and text rewriting.

    Args:
        language:
        text (str): The text to process.

    Returns:
        dict: A dictionary containing the score, grammar corrected text, coherence corrected text, and rewritten text.
    """
    grammar_corrected = grammar_check(text, language)
    translation_language = "en" if language != "en" else "fr"
    coherence_corrected = translate(grammar_corrected, translation_language)
    rewritten = translate(coherence_corrected, language)
    # calculate the difference between texts
    score = combined_similarity_score(text, rewritten)
    return {
        "score": score,
        "rewritten": rewritten,
        "original": text,
    }
