import pandas as pd
import plotly.express as px
import streamlit as st

from lib.charts import CLUB_COLOR_SEQUENCE, CLUB_ORDER, SECONDARY_SEQUENCE, SINGLE_SERIES_COLOR, add_period_annotations, fold_long_tail
from lib.data import data_state, load_corpus, load_result, load_synthesis
from lib.i18n import event_label, t

st.title(t("rq.title"))
st.caption(t("rq.caption"))
st.caption(t("rq.filters_note"))

state = data_state()

if not state.research_results:
    st.info(t("rq.empty"), icon=":material/folder_off:")
    st.stop()

tab_q1, tab_q2, tab_q3, tab_models, tab_context = st.tabs([
    t("rq.tab_q1"), t("rq.tab_q2"), t("rq.tab_q3"), t("rq.tab_models"), t("rq.tab_context"),
])

# ---------------------------------------------------------------------
# Q1 — events by club and sub-type
# ---------------------------------------------------------------------

with tab_q1:
    st.header(t("rq.q1_header"))
    st.markdown(t("rq.q1_body"))

    q1 = load_result("q1_documentos_por_clube_categoria.csv")
    if q1.empty:
        st.caption(t("rq.q1_missing"))
    else:
        q1 = q1.set_index(q1.columns[0])
        q1_chart = q1.drop(index="Total", errors="ignore").drop(columns="Total", errors="ignore")
        q1_chart.columns = [event_label(c) for c in q1_chart.columns]

        col_table, col_chart = st.columns([1, 2])
        with col_table:
            st.dataframe(q1, width="stretch")
        with col_chart:
            fig = px.bar(q1_chart, barmode="group", color_discrete_sequence=SECONDARY_SEQUENCE)
            fig.update_layout(xaxis_title="", yaxis_title=t("rq.axis_num_events"), legend_title=t("rq.legend_event_subtype"))
            st.plotly_chart(fig, width="stretch")

# ---------------------------------------------------------------------
# Q2 — time clustering
# ---------------------------------------------------------------------

with tab_q2:
    st.header(t("rq.q2_header"))
    st.markdown(t("rq.q2_body"))

    q2_club = load_result("q2_documentos_por_ano_clube.csv")
    q2_type = load_result("q2_documentos_por_ano_categoria.csv")

    col_left, col_right = st.columns(2)
    with col_left:
        if q2_club.empty:
            st.caption(t("rq.q2_missing_club"))
        else:
            q2_club = q2_club.set_index(q2_club.columns[0])
            q2_club = q2_club.reindex(columns=[c for c in CLUB_ORDER if c in q2_club.columns])
            fig = px.line(q2_club, markers=True, color_discrete_sequence=CLUB_COLOR_SEQUENCE)
            fig.update_layout(xaxis_title=t("rq.axis_year"), yaxis_title=t("rq.axis_num_events"), legend_title=t("rq.legend_club"))
            add_period_annotations(fig, t("rq.annotation_2008"), t("rq.annotation_covid"))
            st.plotly_chart(fig, width="stretch")

    with col_right:
        if q2_type.empty:
            st.caption(t("rq.q2_missing_type"))
        else:
            q2_type = q2_type.set_index(q2_type.columns[0])
            q2_type.columns = [event_label(c) for c in q2_type.columns]
            fig = px.bar(q2_type, barmode="stack", color_discrete_sequence=SECONDARY_SEQUENCE)
            fig.update_layout(xaxis_title=t("rq.axis_year"), yaxis_title=t("rq.axis_num_events"), legend_title=t("rq.legend_event_subtype"))
            st.plotly_chart(fig, width="stretch")

    st.caption(t("rq.q2_caption"))

# ---------------------------------------------------------------------
# Q3 — coverage bias between clubs
# ---------------------------------------------------------------------

with tab_q3:
    st.header(t("rq.q3_header"))
    st.markdown(t("rq.q3_body"))

    q3_coverage = load_result("q3_indicadores_cobertura.csv")
    q3_sources = load_result("q3_cobertura_por_fonte.csv")

    COVERAGE_COLUMN_LABELS = {
        "noticias_unicas": t("rq.col_unique_news"),
        "fontes_unicas": t("rq.col_num_sources"),
        "primeiro_ano": t("rq.col_first_year"),
        "ultimo_ano": t("rq.col_last_year"),
        "anos_com_cobertura": t("rq.col_years_covered"),
        "noticias_relevantes": t("rq.col_relevant_news"),
        "percentagem_relevante": t("rq.col_pct_relevant"),
        "eventos_documentados": t("rq.col_documented_events"),
        "eventos_classificados": t("rq.col_classified_events"),
        "taxa_documentacao": t("rq.col_documentation_rate"),
    }

    if q3_coverage.empty:
        st.caption(t("rq.q3_missing"))
    else:
        q3_coverage = q3_coverage.set_index(q3_coverage.columns[0])

        if "noticias_unicas" in q3_coverage.columns:
            coverage_values = q3_coverage["noticias_unicas"]
            ratio = coverage_values.max() / max(coverage_values.min(), 1)
            st.metric(t("rq.q3_ratio_metric"), f"{ratio:.1f}×", border=True, help=t("rq.q3_ratio_help"))

        st.dataframe(q3_coverage.rename(columns=COVERAGE_COLUMN_LABELS), width="stretch")

    if not q3_sources.empty:
        q3_sources = q3_sources.set_index(q3_sources.columns[0])
        if q3_sources.shape[1] > 6:
            totals = q3_sources.sum(axis=0).sort_values(ascending=False)
            kept = totals.head(6).index.tolist()
            q3_sources = q3_sources[kept].assign(**{t("common.other"): q3_sources.drop(columns=kept).sum(axis=1)})
        fig = px.bar(q3_sources, barmode="stack", orientation="h", color_discrete_sequence=SECONDARY_SEQUENCE)
        fig.update_layout(xaxis_title=t("rq.axis_num_news"), yaxis_title="", legend_title=t("rq.legend_source"))
        st.plotly_chart(fig, width="stretch")

# ---------------------------------------------------------------------
# Classifier quality
# ---------------------------------------------------------------------

with tab_models:
    st.header(t("rq.models_header"))

    models_summary = load_result("resumo_modelos.csv")
    if models_summary.empty:
        st.caption(t("rq.models_missing"))
    else:
        st.dataframe(
            models_summary,
            hide_index=True,
            width="stretch",
            column_config={
                "accuracy": st.column_config.ProgressColumn(t("rq.col_accuracy"), min_value=0, max_value=1, format="%.3f"),
                "precision": st.column_config.ProgressColumn(t("rq.col_precision"), min_value=0, max_value=1, format="%.3f"),
                "recall": st.column_config.ProgressColumn(t("rq.col_recall"), min_value=0, max_value=1, format="%.3f"),
                "f1": st.column_config.ProgressColumn(t("rq.col_f1"), min_value=0, max_value=1, format="%.3f"),
            },
        )

    try:
        corpus = load_corpus()
    except FileNotFoundError:
        corpus = pd.DataFrame()

    if not corpus.empty and "probabilidade_relevancia" in corpus.columns and corpus["probabilidade_relevancia"].notna().any():
        st.subheader(t("rq.confidence_subheader"))
        st.caption(t("rq.confidence_caption"))
        fig = px.histogram(corpus, x="probabilidade_relevancia", nbins=20, color_discrete_sequence=[SINGLE_SERIES_COLOR])
        fig.update_layout(xaxis_title=t("dashboard.axis_relevance_probability"), yaxis_title=t("rq.axis_num_documents"))
        st.plotly_chart(fig, width="stretch")

# ---------------------------------------------------------------------
# Why NLP, synthesis, and limitations
# ---------------------------------------------------------------------

with tab_context:
    st.header(t("rq.why_nlp_header"))
    st.markdown(t("rq.why_nlp_body"))

    synthesis = load_synthesis()
    if synthesis:
        st.subheader(t("rq.synthesis_header"))
        for line in synthesis.splitlines():
            if line.strip():
                st.markdown(f"- {line.strip()}")

    with st.expander(t("rq.limitations_header"), icon=":material/warning:"):
        st.markdown(t("rq.limitations_body"))
