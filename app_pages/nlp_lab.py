import pandas as pd
import streamlit as st

from lib.data import load_corpus, load_event_model, load_relevance_model
from lib.format import format_percentage
from lib.i18n import entity_label, event_label, sentiment_label, t
from lib.nlp import (
    analyze_sentiment,
    classify_text,
    extract_entities,
    extract_keywords,
    prepare_text,
    render_entities_html,
    summarize_extractive,
    summarize_llm,
)

EXAMPLE_TEXT = (
    "O Sporting SAD anunciou esta terça-feira uma emissão de obrigações no "
    "valor de 30 milhões de euros, com maturidade de cinco anos e um cupão "
    "de 6,5%, segundo comunicado enviado à Comissão do Mercado de Valores "
    "Mobiliários. O montante servirá para refinanciar dívida bancária "
    "existente junto do Novo Banco e alongar o perfil de maturidades do "
    "clube. Em comunicado, a administração liderada por Frederico Varandas "
    "sublinhou que a operação reforça a estrutura de capital da SAD."
)

st.title(t("nlp.title"))
st.caption(t("nlp.caption1"))
st.caption(t("nlp.caption2"))

corpus = load_corpus()
relevance_model = load_relevance_model()
event_model = load_event_model()

if relevance_model is None:
    st.caption(t("nlp.models_disabled"))

mode = st.segmented_control(
    t("nlp.source_label"),
    options=[t("nlp.source_corpus"), t("nlp.source_free")],
    default=t("nlp.source_corpus"),
)

selected_text = ""

if mode == t("nlp.source_corpus"):
    candidates = corpus[corpus.get("texto_valido", pd.Series(True, index=corpus.index))]
    candidates = candidates[candidates["titulo"].str.len() > 0]

    preselected_doc_id = st.session_state.pop("nlp_lab_doc_id", None)
    doc_id_options = candidates["doc_id"].tolist()
    default_index = (
        doc_id_options.index(preselected_doc_id)
        if preselected_doc_id in doc_id_options
        else 0
    )

    titles_by_id = dict(zip(candidates["doc_id"], candidates["titulo"]))

    selected_doc_id = st.selectbox(
        t("nlp.article_label"),
        options=doc_id_options,
        index=default_index if doc_id_options else None,
        format_func=lambda i: titles_by_id.get(i, i),
    )

    if selected_doc_id:
        row = candidates.loc[candidates["doc_id"] == selected_doc_id].iloc[0]
        selected_text = row.get("texto_limpo") or row.get("texto_para_pre_anotacao", "")

    analyze = st.button(t("nlp.analyze_article"), type="primary", icon=":material/play_arrow:")

else:
    with st.form("free_text_form"):
        free_text = st.text_area(
            t("nlp.paste_label"), value="", height=180, placeholder=EXAMPLE_TEXT
        )
        use_example = st.form_submit_button(t("nlp.use_example"), icon=":material/lightbulb:")
        analyze = st.form_submit_button(t("nlp.analyze_text"), type="primary", icon=":material/play_arrow:")

    if use_example:
        free_text = EXAMPLE_TEXT
        analyze = True

    selected_text = free_text

selected_text = prepare_text(selected_text)

if analyze and selected_text:
    st.session_state["nlp_lab_active_text"] = selected_text
elif analyze and not selected_text:
    st.warning(t("nlp.warn_empty"), icon=":material/warning:")

active_text = st.session_state.get("nlp_lab_active_text", "")

if not active_text:
    st.info(t("nlp.info_start"), icon=":material/arrow_upward:")
    st.stop()


@st.cache_data(show_spinner="Classifying with the trained models...")
def _classify(text: str) -> dict:
    result = {}
    if relevance_model is not None:
        result["relevance"] = classify_text(text, relevance_model)
    if event_model is not None:
        result["event_type"] = classify_text(text, event_model)
    return result


@st.cache_data(show_spinner="Extracting entities, keywords, sentiment, and summary...")
def _analyze(text: str) -> dict:
    entities, doc = extract_entities(text)
    return {
        "entities": entities,
        "entities_html": render_entities_html(doc),
        "keywords": extract_keywords(text),
        "sentiment": analyze_sentiment(text),
        "extractive_summary": summarize_extractive(text),
    }


with st.expander(t("nlp.expander_text"), icon=":material/description:"):
    st.write(active_text)

if relevance_model is not None or event_model is not None:
    st.header(t("nlp.classification_header"))
    classification_result = _classify(active_text)

    with st.container(horizontal=True):
        relevance = classification_result.get("relevance")
        if relevance:
            is_relevant = relevance["class"] == 1
            st.metric(
                t("nlp.metric_relevance"),
                t("nlp.relevant") if is_relevant else t("nlp.not_relevant"),
                format_percentage(relevance.get("confidence")),
                border=True,
            )

        event_type = classification_result.get("event_type")
        if event_type:
            st.metric(
                t("nlp.metric_event_type"),
                event_label(event_type["class"]),
                format_percentage(event_type.get("confidence")),
                border=True,
            )

    if event_type and event_type.get("probabilities"):
        probabilities = pd.Series(
            {event_label(k): v for k, v in event_type["probabilities"].items()}
        ).sort_values(ascending=False)
        st.bar_chart(probabilities)

analysis = _analyze(active_text)

tab_ner, tab_kw, tab_sentiment, tab_summary = st.tabs([
    t("nlp.tab_entities"), t("nlp.tab_keywords"), t("nlp.tab_sentiment"), t("nlp.tab_summary"),
])

with tab_ner:
    st.subheader(t("nlp.ner_subheader"))
    if analysis["entities"]:
        st.html(analysis["entities_html"])
        counts = pd.Series([entity_label(e["raw_type"]) for e in analysis["entities"]]).value_counts()
        st.bar_chart(counts)
    else:
        st.caption(t("nlp.ner_empty"))

with tab_kw:
    st.subheader(t("nlp.kw_subheader"))
    keywords = analysis["keywords"]
    if keywords:
        st.markdown(
            " ".join(f":blue-badge[{term}]" for term, _ in keywords)
        )
        kw_df = pd.DataFrame(keywords, columns=[t("nlp.col_keyword"), t("nlp.col_yake_score")])
        st.caption(t("nlp.kw_caption"))
        st.dataframe(kw_df, hide_index=True, width="stretch")
    else:
        st.caption(t("nlp.kw_empty"))

with tab_sentiment:
    st.subheader(t("nlp.sentiment_subheader"))
    sentiment = analysis["sentiment"]
    st.metric(t("nlp.metric_sentiment"), sentiment_label(sentiment["label"]), format_percentage(sentiment["confidence"]), border=True)
    st.caption(t("nlp.sentiment_caption"))

with tab_summary:
    st.subheader(t("nlp.extractive_subheader"))
    st.write(analysis["extractive_summary"])
    st.caption(t("nlp.extractive_caption"))

    st.subheader(t("nlp.llm_subheader"))
    st.caption(t("nlp.llm_caption"))
    if st.button(t("nlp.llm_button"), icon=":material/auto_awesome:"):
        with st.spinner(t("nlp.llm_spinner")):
            try:
                llm_summary = summarize_llm(active_text)
                st.success(llm_summary, icon=":material/auto_awesome:")
            except Exception as error:
                st.error(t("nlp.llm_error", error=error))
