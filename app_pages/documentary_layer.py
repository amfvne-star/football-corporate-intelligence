import pandas as pd
import streamlit as st

from lib.data import (
    load_documentary_base,
    load_documentary_candidates,
    load_financial_extractions,
    load_pdfs_index,
)
from lib.i18n import t

st.title(t("doc.title"))
st.caption(t("doc.caption"))
st.caption(t("doc.filters_note"))

pdfs = load_pdfs_index()
final_base = load_documentary_base()
candidates = load_documentary_candidates()
extractions = load_financial_extractions()

if pdfs.empty and final_base.empty and candidates.empty:
    st.info(t("doc.empty"), icon=":material/folder_off:")
    st.stop()

if not pdfs.empty:
    with st.container(horizontal=True):
        st.metric(t("doc.metric_pdfs"), len(pdfs), border=True)
        if "clube" in pdfs.columns:
            st.metric(t("doc.metric_clubs"), pdfs["clube"].nunique(), border=True)
        if "host" in pdfs.columns:
            st.metric(t("doc.metric_hosts"), pdfs["host"].nunique(), border=True)

    with st.container(border=True):
        st.subheader(t("doc.chart_subheader"))
        if {"fonte", "clube"}.issubset(pdfs.columns):
            st.bar_chart(pdfs.groupby(["clube", "fonte"]).size().unstack(fill_value=0))

st.header(t("doc.matches_header"))

if not final_base.empty:
    st.success(t("doc.validated_success", n=len(final_base)), icon=":material/verified:")
    table = final_base
elif not candidates.empty:
    st.warning(t("doc.candidates_warning", n=len(candidates)), icon=":material/pending:")
    table = candidates

    if "candidato_rank" in table.columns:
        show_all_candidates = st.checkbox(t("doc.show_all_candidates"), value=False)
        if not show_all_candidates:
            table = table[table["candidato_rank"] == 1]
            st.caption(t("doc.best_match_caption", n=len(table)))
else:
    table = pd.DataFrame()

if not table.empty:
    columns_of_interest = [
        c for c in [
            "titulo_noticia", "clube", "tipo_evento_modelo", "data_publicacao",
            "titulo_documento", "data_documento", "fonte_documento",
            "diferenca_dias", "url_documento", "arquivo_documento",
        ]
        if c in table.columns
    ]
    st.dataframe(
        table[columns_of_interest] if columns_of_interest else table,
        hide_index=True,
        width="stretch",
        column_config={
            "url_documento": st.column_config.LinkColumn(t("doc.col_original_url")),
            "arquivo_documento": st.column_config.LinkColumn(t("doc.col_archived")),
            "diferenca_dias": st.column_config.NumberColumn(t("doc.col_delta_days")),
        },
    )

if not extractions.empty:
    st.header(t("doc.financial_header"))
    st.caption(t("doc.financial_caption"))
    extraction_columns = [
        c for c in [
            "titulo", "clube", "data_documento", "montantes_candidatos",
            "taxas_candidatas", "datas_candidatas", "prazos_candidatos",
        ]
        if c in extractions.columns
    ]
    st.dataframe(extractions[extraction_columns], hide_index=True, width="stretch")
