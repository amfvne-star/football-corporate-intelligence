import pandas as pd
import streamlit as st

from lib.data import load_corpus
from lib.i18n import ASSISTANT_SUGGESTED_QUESTIONS, get_lang, t
from lib.rag import NO_CONTEXT_TOKEN, answer

st.title(t("assistant.title"))
st.caption(t("assistant.caption"))
st.caption(t("assistant.caveat"))

corpus = load_corpus()
if corpus.empty:
    st.info(t("assistant.no_corpus"), icon=":material/info:")
    st.stop()

if "assistant_messages" not in st.session_state:
    st.session_state["assistant_messages"] = []


def _render_sources(sources: list[dict]) -> None:
    with st.expander(t("assistant.sources_label", n=len(sources))):
        for source in sources:
            date = source.get("data")
            formatted_date = (
                date.strftime("%d/%m/%Y") if pd.notna(date) else t("events.date_unknown")
            )
            clubs = ", ".join(source.get("clubes") or [])
            line = f"**{source['titulo']}** — {formatted_date}"
            if clubs:
                line += f" — {clubs}"
            st.markdown(line)
            st.caption(source["snippet"])
            if source.get("url"):
                st.markdown(f"[{source['url']}]({source['url']})")


suggested_question = None
if not st.session_state["assistant_messages"]:
    st.caption(t("assistant.suggestions_label"))
    suggestions = ASSISTANT_SUGGESTED_QUESTIONS.get(get_lang(), ASSISTANT_SUGGESTED_QUESTIONS["en"])
    with st.container(horizontal=True):
        for suggestion in suggestions:
            if st.button(suggestion, key=f"assistant_suggestion_{suggestion}"):
                suggested_question = suggestion

for message in st.session_state["assistant_messages"]:
    with st.chat_message(message["role"]):
        st.write(message["content"])
        if message.get("sources"):
            _render_sources(message["sources"])

question = st.chat_input(t("assistant.input_placeholder")) or suggested_question

if question:
    st.session_state["assistant_messages"].append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.write(question)

    with st.chat_message("assistant"):
        with st.spinner(t("assistant.thinking_spinner")):
            try:
                result = answer(question, lang=get_lang())
            except Exception as error:
                error_text = t("assistant.error", error=error)
                st.error(error_text)
                st.session_state["assistant_messages"].append(
                    {"role": "assistant", "content": error_text, "sources": []}
                )
            else:
                if result["text"] == NO_CONTEXT_TOKEN:
                    reply_text = t("assistant.no_context_found")
                else:
                    reply_text = result["text"]
                st.write(reply_text)
                if result["sources"]:
                    _render_sources(result["sources"])
                st.session_state["assistant_messages"].append(
                    {"role": "assistant", "content": reply_text, "sources": result["sources"]}
                )
