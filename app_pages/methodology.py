import streamlit as st

from lib.data import data_state
from lib.i18n import t

st.title(t("meth.title"))

state = data_state()

st.markdown(t("meth.body"))

st.header(t("meth.status_header"))

with st.container(horizontal=True):
    st.metric(
        t("meth.metric_event_type"),
        t("meth.event_type_model") if state.multiclass_corpus else t("meth.event_type_rules"),
        border=True,
    )
    st.metric(
        t("meth.metric_doc_layer"),
        t("meth.doc_layer_available") if state.documentary_layer else t("meth.doc_layer_not_loaded"),
        border=True,
    )
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

with st.expander(t("meth.limitations_header"), icon=":material/warning:"):
    st.markdown(t("meth.limitations_body"))

st.caption(t("meth.logo_credit"))
