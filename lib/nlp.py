"""NLP techniques applied live to an article or free text.

Covers the techniques required by the assignment brief that the collection
pipeline (notebook) does not implement: named entity recognition (NER),
keyword extraction, sentiment analysis, and summarization. Relevance /
event-type classification reuses the models already trained in the
notebook (sections 13 and 14), loaded from `modelo_relevancia.joblib` /
`modelo_tipo_evento.joblib` when those files exist.

The underlying news corpus is written in Portuguese (collected from
Arquivo.pt), so the NER model (spaCy) and keyword extractor (YAKE) are
configured for Portuguese on purpose, even though this module's own
messages and the rest of the app are in English.
"""

from __future__ import annotations

import re

import numpy as np
import streamlit as st

SPACY_PT_MODEL = "pt_core_news_sm"
SENTIMENT_MODEL = "lxyuan/distilbert-base-multilingual-cased-sentiments-student"
LLM_SUMMARY_MODEL = "csebuetnlp/mT5_multilingual_XLSum"

ENTITY_COLORS = {
    "PER": "#f2b8c6",
    "ORG": "#a8d8b9",
    "LOC": "#a9c9f0",
    "GPE": "#a9c9f0",
    "MISC": "#f5d99b",
}


@st.cache_resource(show_spinner="Loading the Portuguese language model (spaCy)...")
def load_spacy():
    import spacy

    try:
        return spacy.load(SPACY_PT_MODEL)
    except OSError:
        from spacy.cli import download

        download(SPACY_PT_MODEL)
        return spacy.load(SPACY_PT_MODEL)


@st.cache_resource(show_spinner="Loading the sentiment analysis model...")
def load_sentiment():
    from transformers import pipeline

    return pipeline(
        "sentiment-analysis",
        model=SENTIMENT_MODEL,
        truncation=True,
        max_length=512,
    )


@st.cache_resource(show_spinner="Loading the summarization model (local LLM, first run may take a while)...")
def load_llm_summarizer():
    from transformers import pipeline

    return pipeline("summarization", model=LLM_SUMMARY_MODEL)


def extract_entities(text: str) -> tuple[list[dict], object]:
    """Returns (list of entities, spaCy doc) for a given text.

    Entity type is kept as spaCy's raw label (e.g. "ORG") — language-neutral
    on purpose, since this feeds a cached function. Translate it for display
    with `lib.i18n.entity_label`.
    """
    nlp = load_spacy()
    doc = nlp(text)

    entities = [
        {"text": ent.text, "raw_type": ent.label_}
        for ent in doc.ents
    ]
    return entities, doc


def render_entities_html(doc) -> str:
    from spacy import displacy

    options = {"colors": ENTITY_COLORS}
    return displacy.render(doc, style="ent", page=False, options=options)


def extract_keywords(text: str, top_n: int = 12) -> list[tuple[str, float]]:
    import yake

    extractor = yake.KeywordExtractor(lan="pt", n=2, dedupLim=0.8, top=top_n)
    pairs = extractor.extract_keywords(text)
    # YAKE: lower score = more relevant keyword.
    return sorted(pairs, key=lambda pair: pair[1])


def analyze_sentiment(text: str) -> dict:
    pipe = load_sentiment()
    result = pipe(text[:2000])[0]
    return {"label": result["label"], "confidence": result["score"]}


def _split_sentences(doc) -> list[str]:
    sentences = [sentence.text.strip() for sentence in doc.sents]
    return [s for s in sentences if len(s) > 15]


def summarize_extractive(text: str, n_sentences: int = 4) -> str:
    """Extractive summarization: TF-IDF + sentence centrality (no LLM)."""
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    nlp = load_spacy()
    doc = nlp(text)
    sentences = _split_sentences(doc)

    if len(sentences) <= n_sentences:
        return " ".join(sentences)

    vectorizer = TfidfVectorizer(max_df=0.9, min_df=1)
    matrix = vectorizer.fit_transform(sentences)
    centroid = np.asarray(matrix.mean(axis=0))
    scores = cosine_similarity(matrix, centroid).ravel()

    top_indices = np.argsort(scores)[::-1][:n_sentences]
    top_indices_ordered = sorted(top_indices)
    return " ".join(sentences[i] for i in top_indices_ordered)


def summarize_llm(text: str) -> str:
    """Abstractive summarization with a local LLM (multilingual mT5)."""
    pipe = load_llm_summarizer()
    limited_text = text[:4000]
    result = pipe(limited_text, max_length=120, min_length=25, do_sample=False)
    return result[0]["summary_text"]


def classify_text(text: str, model) -> dict | None:
    """Applies an already-trained sklearn pipeline (TF-IDF + classifier)."""
    if model is None or not text.strip():
        return None

    prediction = model.predict([text])[0]
    result = {"class": prediction}

    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba([text])[0]
        classes = model.named_steps["classificador"].classes_ if hasattr(model, "named_steps") else model.classes_
        result["probabilities"] = dict(zip(classes, probabilities))
        result["confidence"] = float(max(probabilities))

    return result


def prepare_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text or "").strip()
    return text
