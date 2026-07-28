from pathlib import Path

import streamlit as st

from lib.data import data_state
from lib.i18n import t

NOTEBOOK_PATH = Path(__file__).resolve().parent.parent / "assets" / "Football_Corporate_Intelligence_v13_final.ipynb"

st.title(t("meth.title"))

state = data_state()

st.markdown(t("meth.body"))

st.header(t("meth.status_header"))

with st.container(horizontal=True):
    st.metric(
        t("meth.metric_classifiers"),
        t("meth.classifiers_loaded") if state.trained_models else t("meth.classifiers_not_found"),
        border=True,
    )
    st.metric(
        t("meth.metric_results"),
        t("meth.results_available") if state.research_results else t("meth.results_not_loaded"),
        border=True,
    )

st.caption(t("meth.caption_copy_files"))

st.header(t("meth.notebook_header"))
st.markdown(t("meth.notebook_body"))
if NOTEBOOK_PATH.exists():
    st.download_button(
        t("meth.notebook_download_label"),
        data=NOTEBOOK_PATH.read_bytes(),
        file_name=NOTEBOOK_PATH.name,
        mime="application/x-ipynb+json",
        icon=":material/download:",
    )

with st.expander(t("meth.limitations_header"), icon=":material/warning:"):
    st.markdown(t("meth.limitations_body"))

st.caption(t("meth.logo_credit"))
