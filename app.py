"""App entry point. Multi-page navigation via st.navigation, with an
EN/PT language switcher that every page reads through `lib.i18n.t`."""

import streamlit as st

from lib.charts import PBS_LOGO_URL
from lib.i18n import LANGUAGES, t

st.set_page_config(
    page_title="Football Corporate Intelligence",
    page_icon=":material/sports_soccer:",
    layout="wide",
)

st.logo(PBS_LOGO_URL, size="large")
st.markdown(
    """
    <style>
    [data-testid="stLogo"] {
        height: 4rem;
        max-height: none;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.selectbox(
        t("app.language_label"),
        options=list(LANGUAGES.keys()),
        format_func=lambda code: LANGUAGES[code],
        key="lang",
        label_visibility="collapsed",
    )

pages = [
    st.Page("app_pages/dashboard.py", title=t("nav.dashboard"), icon=":material/dashboard:", default=True),
    st.Page("app_pages/research_questions.py", title=t("nav.research_questions"), icon=":material/query_stats:"),
    st.Page("app_pages/events.py", title=t("nav.events"), icon=":material/article:"),
    st.Page("app_pages/nlp_lab.py", title=t("nav.nlp_lab"), icon=":material/science:"),
    st.Page("app_pages/assistant.py", title=t("nav.assistant"), icon=":material/forum:"),
    st.Page("app_pages/data_export.py", title=t("nav.data_export"), icon=":material/table_chart:"),
    st.Page("app_pages/methodology.py", title=t("nav.methodology"), icon=":material/menu_book:"),
]

page = st.navigation(pages, position="sidebar")

with st.sidebar:
    st.caption(t("app.sidebar_caption"))

page.run()
