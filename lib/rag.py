"""Retrieval-augmented chat assistant over the corpus.

Answers are grounded in the corpus text: `retrieve` finds the articles (and
the sentences within them) most similar to the question via TF-IDF, and
`answer` asks a small local instruct LLM to respond using only those
snippets. This is deliberately not open-domain chat and not a text-to-pandas
aggregator — it is scoped to "what do the articles say about X", the same
scope as free-text search elsewhere in the app.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st

from lib.data import load_corpus
from lib.nlp import _split_sentences, load_spacy

ASSISTANT_MODEL = "Qwen/Qwen2.5-0.5B-Instruct"

SYSTEM_PROMPT = {
    "en": (
        "You are an assistant answering questions about a news corpus on "
        "corporate financing events at Benfica SAD, FC Porto SAD, and "
        "Sporting SAD. Answer ONLY using the numbered excerpts below. If the "
        "excerpts do not contain the answer, say you could not find it in "
        "the corpus — do not make anything up. Answer in English, concisely."
    ),
    "pt": (
        "És um assistente que responde a perguntas sobre um corpus de "
        "notícias sobre eventos de financiamento corporativo no Benfica SAD, "
        "FC Porto SAD e Sporting SAD. Responde APENAS com base nos excertos "
        "numerados abaixo. Se os excertos não contiverem a resposta, diz que "
        "não a encontraste no corpus — não inventes nada. Responde em "
        "português, de forma concisa."
    ),
}

NO_CONTEXT_TOKEN = "__NO_CONTEXT__"


@st.cache_resource(show_spinner="Indexing the corpus for search...")
def build_corpus_index():
    """TF-IDF index over the corpus, for retrieval (not classification)."""
    from sklearn.feature_extraction.text import TfidfVectorizer

    corpus = load_corpus()
    valid = corpus.get("texto_valido", pd.Series(True, index=corpus.index))
    docs = corpus[valid].copy()
    docs["retrieval_text"] = docs["texto_limpo"].where(
        docs["texto_limpo"].str.len() > 0, docs.get("texto_para_pre_anotacao", "")
    )
    docs = docs[docs["retrieval_text"].str.len() > 0].reset_index(drop=True)

    vectorizer = TfidfVectorizer(max_df=0.9, min_df=1, ngram_range=(1, 2))
    doc_matrix = vectorizer.fit_transform(docs["retrieval_text"])

    return vectorizer, doc_matrix, docs


@st.cache_resource(show_spinner="Loading the assistant model (local LLM, first run may take a while)...")
def load_assistant_llm():
    from transformers import pipeline

    return pipeline("text-generation", model=ASSISTANT_MODEL, device="cpu")


def retrieve(question: str, top_k: int = 4) -> list[dict]:
    """Top-k documents most similar to `question`, each reduced to its two
    most relevant sentences so the LLM prompt stays short."""
    from sklearn.metrics.pairwise import cosine_similarity

    vectorizer, doc_matrix, docs = build_corpus_index()
    question_vector = vectorizer.transform([question])
    scores = cosine_similarity(question_vector, doc_matrix).ravel()

    top_indices = np.argsort(scores)[::-1][:top_k]
    top_indices = [i for i in top_indices if scores[i] > 0]

    if not top_indices:
        return []

    nlp = load_spacy()
    results = []
    for i in top_indices:
        row = docs.iloc[i]
        sentences = _split_sentences(nlp(row["retrieval_text"][:5000]))
        snippet = row["retrieval_text"][:400]
        if sentences:
            sentence_vectors = vectorizer.transform(sentences)
            sentence_scores = cosine_similarity(question_vector, sentence_vectors).ravel()
            top_sentence_idx = np.argsort(sentence_scores)[::-1][:2]
            top_sentence_idx = sorted(idx for idx in top_sentence_idx if sentence_scores[idx] > 0)
            if top_sentence_idx:
                snippet = " ".join(sentences[idx] for idx in top_sentence_idx)

        results.append(
            {
                "doc_id": row.get("doc_id", ""),
                "titulo": row.get("titulo", ""),
                "clubes": row.get("club_list", []),
                "data": row.get("data_publicacao"),
                "url": row.get("url_original", ""),
                "snippet": snippet,
                "score": float(scores[i]),
            }
        )
    return results


def _build_prompt(question: str, sources: list[dict], lang: str) -> list[dict]:
    excerpts = "\n".join(
        f"[{i}] {source['titulo']}: {source['snippet']}"
        for i, source in enumerate(sources, start=1)
    )
    user_content = f"{excerpts}\n\nQuestion: {question}" if lang == "en" else f"{excerpts}\n\nPergunta: {question}"
    return [
        {"role": "system", "content": SYSTEM_PROMPT.get(lang, SYSTEM_PROMPT["en"])},
        {"role": "user", "content": user_content},
    ]


def answer(question: str, lang: str = "en", top_k: int = 4) -> dict:
    """Retrieves relevant excerpts and generates a grounded answer.

    Returns {"text": str, "sources": list[dict]}. `sources` is empty when
    nothing relevant was found, in which case `text` says so without calling
    the LLM.
    """
    sources = retrieve(question, top_k=top_k)
    if not sources:
        return {"text": NO_CONTEXT_TOKEN, "sources": []}

    messages = _build_prompt(question, sources, lang)
    generator = load_assistant_llm()
    output = generator(
        messages,
        max_new_tokens=200,
        do_sample=False,
        pad_token_id=generator.tokenizer.eos_token_id,
    )
    generated = output[0]["generated_text"]
    reply = generated[-1]["content"] if isinstance(generated, list) else str(generated)

    return {"text": reply.strip(), "sources": sources}
