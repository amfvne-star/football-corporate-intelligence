import pandas as pd
import plotly.express as px
import streamlit as st

from lib.charts import CLUB_COLORS, CLUB_LOGOS, CLUB_ORDER, SECONDARY_SEQUENCE, SINGLE_SERIES_COLOR, fold_long_tail
from lib.data import data_state, load_corpus
from lib.filters import sidebar_filters
from lib.format import format_percentage, format_thousands
from lib.i18n import t

st.title(t("dashboard.title"))
st.caption(t("dashboard.caption"))

CLUB_MARKDOWN_COLOR = {"Benfica": "red", "FC Porto": "blue", "Sporting": "green"}

with st.container(horizontal=True, gap="medium"):
    for club in CLUB_ORDER:
        with st.container(horizontal=True, vertical_alignment="center", gap="small"):
            st.image(CLUB_LOGOS[club], width=24)
            st.markdown(f":{CLUB_MARKDOWN_COLOR[club]}[**{club}**]")

state = data_state()
try:
    corpus = load_corpus()
except FileNotFoundError:
    st.error(t("dashboard.error_missing_corpus"), icon=":material/error:")
    st.stop()

if not state.multiclass_corpus:
    st.warning(t("dashboard.warning_rules"), icon=":material/info:")

df_filtered = sidebar_filters(corpus)

if df_filtered.empty:
    st.info(t("dashboard.empty"), icon=":material/filter_alt_off:")
    st.stop()

total_documents = len(df_filtered)
total_relevant = int(df_filtered["relevante_previsto"].sum()) if "relevante_previsto" in df_filtered else 0
n_clubs = len({c for row in df_filtered["club_list"] for c in row})
avg_probability = df_filtered["probabilidade_relevancia"].mean() if "probabilidade_relevancia" in df_filtered else None

with st.container(horizontal=True):
    st.metric(t("dashboard.metric_documents"), format_thousands(total_documents), border=True)
    st.metric(t("dashboard.metric_relevant"), format_thousands(total_relevant), border=True)
    st.metric(t("dashboard.metric_clubs"), n_clubs, border=True)
    st.metric(t("dashboard.metric_avg_probability"), format_percentage(avg_probability), border=True)

st.caption(t("dashboard.see_research_questions"))

col_left, col_right = st.columns(2)

with col_left:
    with st.container(border=True):
        st.subheader(t("dashboard.section_events_by_club"))
        club_rows = [
            {t("dashboard.col_club"): club, "doc_id": row["doc_id"]}
            for _, row in df_filtered.iterrows()
            for club in (row["club_list"] or [t("dashboard.not_identified")])
        ]
        if club_rows:
            club_counts = (
                pd.DataFrame(club_rows)[t("dashboard.col_club")].value_counts()
                .rename_axis(t("dashboard.col_club")).reset_index(name=t("dashboard.col_documents"))
            )
            club_column = t("dashboard.col_club")
            fig = px.bar(
                club_counts, x=club_column, y=t("dashboard.col_documents"),
                color=club_column,
                color_discrete_map={
                    club: CLUB_COLORS.get(club, SINGLE_SERIES_COLOR)
                    for club in club_counts[club_column]
                },
                text_auto=True,
            )
            fig.update_layout(xaxis_title="", yaxis_title=t("dashboard.axis_num_documents"), showlegend=False)
            st.plotly_chart(fig, width="stretch")
        else:
            st.caption(t("dashboard.caption_no_clubs"))

with col_right:
    with st.container(border=True):
        st.subheader(t("dashboard.section_events_by_type"))
        type_counts = (
            df_filtered["event_type_display"]
            .value_counts()
            .rename_axis(t("filters.event_type"))
            .reset_index(name=t("dashboard.col_documents"))
        )
        fig = px.bar(
            type_counts, x=t("filters.event_type"), y=t("dashboard.col_documents"),
            text_auto=True, color_discrete_sequence=SECONDARY_SEQUENCE,
        )
        fig.update_layout(xaxis_title="", yaxis_title=t("dashboard.axis_num_documents"))
        st.plotly_chart(fig, width="stretch")

col_left2, col_right2 = st.columns(2)

with col_left2:
    with st.container(border=True):
        st.subheader(t("dashboard.section_docs_by_source"))
        source_counts = (
            df_filtered["fonte"].replace("", t("dashboard.unknown_source"))
            .value_counts()
        )
        source_counts = fold_long_tail(source_counts, other_label=t("common.other"))
        source_counts = (
            source_counts.rename_axis(t("dashboard.col_source")).reset_index(name=t("dashboard.col_documents"))
        )
        fig = px.bar(
            source_counts, x=t("dashboard.col_documents"), y=t("dashboard.col_source"), orientation="h",
            text_auto=True, color_discrete_sequence=[SINGLE_SERIES_COLOR],
        )
        fig.update_layout(xaxis_title=t("dashboard.axis_num_documents"), yaxis_title="", yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, width="stretch")

with col_right2:
    with st.container(border=True):
        st.subheader(t("dashboard.section_time_evolution"))
        time_data = df_filtered.dropna(subset=["data_publicacao"]) if "data_publicacao" in df_filtered else pd.DataFrame()

        if time_data.empty:
            st.caption(t("dashboard.caption_no_dates"))
        else:
            by_month = (
                time_data.set_index("data_publicacao")
                .resample("ME").size()
                .reset_index(name=t("dashboard.col_documents"))
            )
            fig = px.line(
                by_month, x="data_publicacao", y=t("dashboard.col_documents"), markers=True,
                color_discrete_sequence=[SINGLE_SERIES_COLOR],
            )
            fig.update_layout(xaxis_title=t("dashboard.axis_date"), yaxis_title=t("dashboard.axis_num_documents"))
            st.plotly_chart(fig, width="stretch")

with st.expander(t("dashboard.section_probability_distribution"), icon=":material/model_training:"):
    if "probabilidade_relevancia" in df_filtered and df_filtered["probabilidade_relevancia"].notna().any():
        fig = px.histogram(
            df_filtered, x="probabilidade_relevancia", nbins=20,
            color_discrete_sequence=[SINGLE_SERIES_COLOR],
        )
        fig.update_layout(xaxis_title=t("dashboard.axis_relevance_probability"), yaxis_title=t("dashboard.axis_num_documents"))
        st.plotly_chart(fig, width="stretch")
    else:
        st.caption(t("dashboard.caption_no_probabilities"))
