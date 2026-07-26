"""Loading and caching of every artifact produced by the notebook.

Each artifact is optional: pages check `.empty` / `is None` before using it,
so the app works with only `corpus_classificado.csv` and automatically gets
richer as more pipeline outputs (notebook sections 14 and 15) are copied
into the project root.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import joblib
import pandas as pd
import streamlit as st

from lib.format import extract_clubs, normalize_boolean

ROOT = Path(__file__).resolve().parent.parent

CORPUS_BASE_FILE = ROOT / "corpus_classificado.csv"
CORPUS_EVENTS_FILE = ROOT / "corpus_classificado_eventos.csv"
DOCUMENTARY_BASE_FILE = ROOT / "base_documental_final.csv"
PDFS_INDEX_FILE = ROOT / "pdfs_indice.csv"
EXTRACTIONS_FILE = ROOT / "extracoes_financeiras_preliminares.csv"
DOC_CANDIDATES_FILE = ROOT / "candidatos_documentais.csv"
DOC_VALIDATION_FILE = ROOT / "validacao_documental.csv"
RELEVANCE_MODEL_FILE = ROOT / "modelo_relevancia.joblib"
EVENT_MODEL_FILE = ROOT / "modelo_tipo_evento.joblib"
RESULTS_FOLDER = ROOT / "resultados"


@dataclass(frozen=True)
class DataState:
    """Summarizes which optional artifacts were found, to drive UI warnings."""

    multiclass_corpus: bool
    documentary_layer: bool
    trained_models: bool
    research_results: bool


def _optional_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(path, low_memory=False)
    except Exception:
        return pd.DataFrame()


@st.cache_data(show_spinner="Loading the corpus...")
def load_corpus() -> pd.DataFrame:
    """Classified corpus. Uses the version with the model-predicted event
    type (notebook section 14) when available; otherwise falls back to the
    binary-classification version (section 13), using the pre-annotation
    rules as an approximation of the event type."""

    if CORPUS_EVENTS_FILE.exists():
        df = pd.read_csv(CORPUS_EVENTS_FILE, low_memory=False)
        df["_event_type_source"] = "model"
    elif CORPUS_BASE_FILE.exists():
        df = pd.read_csv(CORPUS_BASE_FILE, low_memory=False)
        df["_event_type_source"] = "rules"
    else:
        raise FileNotFoundError(
            "Neither corpus_classificado.csv nor corpus_classificado_eventos.csv "
            "was found in the project root."
        )

    if "tipo_evento_modelo" in df.columns:
        df["event_type_final"] = df["tipo_evento_modelo"]
        df["event_type_confidence"] = pd.to_numeric(
            df.get("prob_tipo_evento"), errors="coerce"
        )
    else:
        df["event_type_final"] = df.get("tipo_evento_sugerido")
        df["event_type_confidence"] = pd.to_numeric(
            df.get("confianca_sugestao"), errors="coerce"
        )

    # NOTE: the human-readable event label is intentionally NOT computed
    # here. This DataFrame is cached with @st.cache_data independently of
    # the UI language, so baking a translated string in would freeze it in
    # whichever language was active the first time the cache was filled.
    # Pages/lib.filters translate `event_type_final` at render time via
    # `lib.i18n.event_label`.

    if "data_publicacao" in df.columns:
        df["data_publicacao"] = pd.to_datetime(
            df["data_publicacao"], errors="coerce"
        )
    df["year"] = df["data_publicacao"].dt.year.astype("Int64") if "data_publicacao" in df.columns else pd.Series(dtype="Int64")

    for column in ("probabilidade_relevancia", "n_chars", "n_capturas", "n_chars_limpo"):
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce")

    if "relevante_previsto" in df.columns:
        df["relevante_previsto"] = normalize_boolean(df["relevante_previsto"].astype(str))

    for column in ("doc_id", "clubes", "fonte", "titulo", "url_original", "url_arquivo", "texto_limpo", "texto"):
        if column in df.columns:
            df[column] = df[column].fillna("").astype(str)

    df["club_list"] = df["clubes"].apply(extract_clubs) if "clubes" in df.columns else [[]] * len(df)

    return df


@st.cache_data
def load_documentary_base() -> pd.DataFrame:
    return _optional_csv(DOCUMENTARY_BASE_FILE)


@st.cache_data
def load_pdfs_index() -> pd.DataFrame:
    return _optional_csv(PDFS_INDEX_FILE)


@st.cache_data
def load_financial_extractions() -> pd.DataFrame:
    return _optional_csv(EXTRACTIONS_FILE)


@st.cache_data(show_spinner="Loading candidate news↔document matches...")
def load_documentary_candidates() -> pd.DataFrame:
    """Candidate news-to-PDF matches (section 15.6/15.7). Prefers
    `candidatos_documentais.csv`; falls back to `validacao_documental.csv`
    (the same rows, with empty columns added for manual validation) since
    that's the file annotators actually work from and may be the only one
    copied over."""
    if DOC_CANDIDATES_FILE.exists():
        return _optional_csv(DOC_CANDIDATES_FILE)
    return _optional_csv(DOC_VALIDATION_FILE)


@st.cache_data
def load_result(file_name: str) -> pd.DataFrame:
    return _optional_csv(RESULTS_FOLDER / file_name)


@st.cache_data
def load_synthesis() -> str:
    path = RESULTS_FOLDER / "sintese_resultados.txt"
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


@st.cache_resource(show_spinner="Loading the relevance classifier...")
def load_relevance_model():
    if not RELEVANCE_MODEL_FILE.exists():
        return None
    return joblib.load(RELEVANCE_MODEL_FILE)


@st.cache_resource(show_spinner="Loading the event-type classifier...")
def load_event_model():
    if not EVENT_MODEL_FILE.exists():
        return None
    return joblib.load(EVENT_MODEL_FILE)


def data_state() -> DataState:
    return DataState(
        multiclass_corpus=CORPUS_EVENTS_FILE.exists(),
        documentary_layer=DOCUMENTARY_BASE_FILE.exists() or DOC_CANDIDATES_FILE.exists() or DOC_VALIDATION_FILE.exists(),
        trained_models=RELEVANCE_MODEL_FILE.exists() and EVENT_MODEL_FILE.exists(),
        research_results=RESULTS_FOLDER.exists() and any(RESULTS_FOLDER.iterdir()),
    )
