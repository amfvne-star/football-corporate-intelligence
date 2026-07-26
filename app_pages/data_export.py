import streamlit as st

from lib.data import load_corpus
from lib.filters import sidebar_filters
from lib.i18n import t

st.title(t("data.title"))
st.caption(t("data.caption"))

corpus = load_corpus()
df_filtered = sidebar_filters(corpus)

display_columns = [
    "doc_id", "data_publicacao", "clubes", "titulo", "fonte",
    "event_type_display", "relevante_previsto",
    "probabilidade_relevancia", "url_original",
]
existing_columns = [c for c in display_columns if c in df_filtered.columns]

st.dataframe(
    df_filtered[existing_columns],
    width="stretch",
    hide_index=True,
    column_config={
        "data_publicacao": st.column_config.DateColumn(t("data.col_date"), format="DD/MM/YYYY"),
        "probabilidade_relevancia": st.column_config.ProgressColumn(
            t("data.col_relevance_prob"), min_value=0.0, max_value=1.0, format="%.2f"
        ),
        "url_original": st.column_config.LinkColumn(t("data.col_original_source")),
    },
)

csv_export = df_filtered.to_csv(index=False).encode("utf-8-sig")
st.download_button(
    t("data.download_button"),
    data=csv_export,
    file_name="financing_events_filtered.csv",
    mime="text/csv",
    icon=":material/download:",
)
