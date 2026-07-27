"""Sidebar filters shared by every page that explores the corpus."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from lib.i18n import event_label, t


def sidebar_filters(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["event_type_display"] = df["event_type_final"].fillna("").apply(event_label)

    all_clubs = sorted({c for row in df["club_list"] for c in row}) if "club_list" in df.columns else []
    event_types = sorted(df["event_type_display"].dropna().loc[lambda x: x != ""].unique().tolist())
    sources = sorted(df["fonte"].dropna().loc[lambda x: x != ""].unique().tolist())
    all_years = sorted(df["year"].dropna().unique().tolist()) if "year" in df.columns else []

    with st.sidebar:
        st.header(t("filters.header"))

        relevant_only = st.checkbox(
            t("filters.relevant_only"), value=True, key="filter_relevant_only"
        )
        selected_clubs = st.multiselect(t("filters.club"), options=all_clubs, key="filter_clubs")
        selected_years = st.multiselect(t("filters.year"), options=all_years, key="filter_years")
        selected_events = st.multiselect(t("filters.event_type"), options=event_types, key="filter_events")
        selected_sources = st.multiselect(t("filters.source"), options=sources, key="filter_sources")
        min_probability = st.slider(
            t("filters.min_probability"),
            min_value=0.0, max_value=1.0, value=0.5, step=0.05,
            key="filter_min_probability",
        )
        search = st.text_input(
            t("filters.search"),
            placeholder=t("filters.search_placeholder"),
            key="filter_search",
        )

    result = df

    if relevant_only and "relevante_previsto" in result.columns:
        result = result[result["relevante_previsto"]]

    if selected_clubs:
        result = result[
            result["club_list"].apply(lambda row: any(c in row for c in selected_clubs))
        ]

    if selected_years and "year" in result.columns:
        result = result[result["year"].isin(selected_years)]

    if selected_events:
        result = result[result["event_type_display"].isin(selected_events)]

    if selected_sources:
        result = result[result["fonte"].isin(selected_sources)]

    if "probabilidade_relevancia" in result.columns:
        result = result[result["probabilidade_relevancia"].fillna(0).ge(min_probability)]

    if search:
        text_field = result.get("texto_limpo", result.get("texto_para_pre_anotacao", ""))
        mask = result["titulo"].str.contains(search, case=False, na=False, regex=False)
        if isinstance(text_field, pd.Series):
            mask = mask | text_field.str.contains(search, case=False, na=False, regex=False)
        result = result[mask]

    return result
