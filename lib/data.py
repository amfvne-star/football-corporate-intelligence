"""Loading and caching of every artifact produced by the notebook.

The `resultados/` folder and the relevance model are optional: pages check
`.empty` / `is None` before using them, so the app works with only
`corpus_classificado.csv` present and gets richer as the rest of the
notebook's outputs (section 10's `resultados/` folder, `modelo_relevancia.joblib`)
are copied into the project root.
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
RELEVANCE_MODEL_FILE = ROOT / "modelo_relevancia.joblib"
RESULTS_FOLDER = ROOT / "resultados"


@dataclass(frozen=True)
class DataState:
    """Summarizes which optional artifacts were found, to drive UI warnings."""

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
    """Classified corpus. The event category (`tipo_evento_previsto`) is
    rule-based (regex over the relevant documents, notebook section 8) —
    there is no trained multiclass classifier in this version of the
    project, so there is no associated confidence score."""

    if not CORPUS_BASE_FILE.exists():
        raise FileNotFoundError(
            "corpus_classificado.csv was not found in the project root."
        )
    df = pd.read_csv(CORPUS_BASE_FILE, low_memory=False)
    df["event_type_final"] = df.get("tipo_evento_previsto")

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


def data_state() -> DataState:
    return DataState(
        trained_models=RELEVANCE_MODEL_FILE.exists(),
        research_results=RESULTS_FOLDER.exists() and any(RESULTS_FOLDER.iterdir()),
    )
