import pandas as pd
import streamlit as st

from lib.data import load_corpus
from lib.filters import sidebar_filters
from lib.format import format_percentage
from lib.i18n import t

st.title(t("events.title"))
st.caption(t("events.caption"))

corpus = load_corpus()
df_filtered = sidebar_filters(corpus)

if df_filtered.empty:
    st.info(t("events.empty"), icon=":material/filter_alt_off:")
    st.stop()

sort_column = "probabilidade_relevancia" if "probabilidade_relevancia" in df_filtered else "doc_id"
df_events = df_filtered.sort_values(by=sort_column, ascending=False)

maximum = min(len(df_events), 200)
quantity = st.slider(
    t("events.slider_label"),
    min_value=5, max_value=max(5, maximum), value=min(20, max(5, maximum)), step=5,
)

for _, row in df_events.head(quantity).iterrows():
    title = row.get("titulo") or t("events.untitled")
    club = ", ".join(row.get("club_list") or []) or t("events.club_unknown")
    event = row.get("event_type_display") or t("dashboard.not_identified")
    source = row.get("fonte") or t("events.source_unknown")
    date = row.get("data_publicacao")
    probability = row.get("probabilidade_relevancia")
    formatted_date = date.strftime("%d/%m/%Y") if pd.notna(date) else t("events.date_unknown")

    with st.expander(f"{title} — {format_percentage(probability)}"):
        col_a, col_b, col_c = st.columns(3)
        col_a.markdown(f"**{t('events.label_club')}:** {club}")
        col_b.markdown(f"**{t('events.label_event')}:** {event}")
        col_c.markdown(f"**{t('events.label_date')}:** {formatted_date}")
        st.markdown(f"**{t('events.label_source')}:** {source}")

        text = row.get("texto_limpo") or row.get("texto_para_pre_anotacao", "")
        st.write(text[:2500] if text else t("events.no_text"))

        with st.container(horizontal=True):
            url = row.get("url_original", "")
            if url.startswith(("http://", "https://")):
                st.link_button(t("events.open_source"), url, icon=":material/open_in_new:")

            archived_url = row.get("url_arquivo", "")
            if archived_url.startswith(("http://", "https://")):
                st.link_button(t("events.open_archive"), archived_url, icon=":material/history:")

            if st.button(t("events.analyze_button"), key=f"nlp_{row['doc_id']}", icon=":material/science:"):
                st.session_state["nlp_lab_doc_id"] = row["doc_id"]
                st.switch_page("app_pages/nlp_lab.py")
