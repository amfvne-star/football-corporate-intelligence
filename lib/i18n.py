"""Minimal EN/PT translation layer.

`t(key)` looks up UI text by key in the current language (`st.session_state["lang"]`,
set by the selector in `app.py`). Data-dependent labels (event sub-types, NER
entity types, sentiment labels) are translated separately via `event_label`,
`entity_label`, and `sentiment_label`, because their *raw* values come from
cached functions (`st.cache_data`) that must stay language-neutral — baking a
translation into a cached DataFrame would freeze it in whichever language was
active the first time the cache was populated.
"""

from __future__ import annotations

import streamlit as st

DEFAULT_LANG = "en"

LANGUAGES = {"en": "English", "pt": "Português"}

STRINGS: dict[str, dict[str, str]] = {
    # -- app.py --------------------------------------------------------
    "app.language_label": {"en": "Language / Idioma", "pt": "Language / Idioma"},
    "app.sidebar_caption": {
        "en": "Financing and capital markets in Portuguese football — Benfica SAD, FC Porto SAD, Sporting SAD.",
        "pt": "Financiamento e mercados de capitais no futebol português — Benfica SAD, FC Porto SAD, Sporting SAD.",
    },
    "nav.dashboard": {"en": "Dashboard", "pt": "Dashboard"},
    "nav.research_questions": {"en": "Research questions", "pt": "Perguntas de investigação"},
    "nav.events": {"en": "Event explorer", "pt": "Explorador de eventos"},
    "nav.nlp_lab": {"en": "NLP lab", "pt": "Laboratório de NLP"},
    "nav.assistant": {"en": "Assistant", "pt": "Assistente"},
    "nav.data_export": {"en": "Data & export", "pt": "Dados e exportação"},
    "nav.methodology": {"en": "Methodology", "pt": "Metodologia"},

    # -- shared chart vocabulary ------------------------------------------
    "common.other": {"en": "Other", "pt": "Outras"},

    # -- lib/filters.py --------------------------------------------------
    "filters.header": {"en": "Filters", "pt": "Filtros"},
    "filters.relevant_only": {"en": "Show relevant events only", "pt": "Mostrar apenas eventos relevantes"},
    "filters.club": {"en": "Club", "pt": "Clube"},
    "filters.year": {"en": "Year", "pt": "Ano"},
    "filters.year_unknown": {"en": "Unknown date", "pt": "Data desconhecida"},
    "filters.event_type": {"en": "Event type", "pt": "Tipo de evento"},
    "filters.source": {"en": "Source", "pt": "Fonte"},
    "filters.min_probability": {"en": "Minimum relevance probability", "pt": "Probabilidade mínima de relevância"},
    "filters.search": {"en": "Search in title or text", "pt": "Pesquisar no título ou texto"},
    "filters.search_placeholder": {
        "en": "e.g. bond issuance, bank financing, capital increase...",
        "pt": "ex.: emissão de obrigações, financiamento bancário, aumento de capital...",
    },

    # -- app_pages/dashboard.py ------------------------------------------
    "dashboard.title": {"en": "Dashboard", "pt": "Dashboard"},
    "dashboard.caption": {
        "en": "Corporate financing events identified in news and documents about Benfica SAD, FC Porto SAD, and Sporting SAD.",
        "pt": "Eventos de financiamento corporativo identificados em notícias e documentos sobre Benfica SAD, FC Porto SAD e Sporting SAD.",
    },
    "dashboard.empty": {"en": "No records match the selected filters.", "pt": "Não existem registos para os filtros selecionados."},
    "dashboard.metric_total_collected": {"en": "Total collected", "pt": "Total recolhido"},
    "dashboard.metric_total_collected_help": {
        "en": "Fixed: every document collected from Arquivo.pt, regardless of the sidebar filters.",
        "pt": "Fixo: todos os documentos recolhidos do Arquivo.pt, independentemente dos filtros da barra lateral.",
    },
    "dashboard.metric_pct_of_corpus": {"en": "% of corpus", "pt": "% do corpus"},
    "dashboard.metric_pct_of_corpus_help": {
        "en": "Relevant events ÷ total collected. Reacts to the sidebar filters.",
        "pt": "Eventos relevantes a dividir pelo total recolhido. Reage aos filtros da barra lateral.",
    },
    "dashboard.metric_relevant": {"en": "Relevant events", "pt": "Eventos relevantes"},
    "dashboard.metric_relevant_help": {
        "en": "Documents matching the current sidebar filters that were flagged as relevant (by the model or human review).",
        "pt": "Documentos que cumprem os filtros atuais da barra lateral e foram marcados como relevantes (pelo modelo ou por revisão humana).",
    },
    "dashboard.metric_dedup_rate": {"en": "Duplication rate", "pt": "Taxa de duplicação"},
    "dashboard.metric_dedup_rate_help": {
        "en": "Fixed: share of raw archive captures collapsed into a single article during deduplication (1 minus unique articles divided by total captures, from `n_capturas`). Not affected by the sidebar filters.",
        "pt": "Fixo: proporção de capturas brutas do arquivo que foram fundidas num único artigo durante a deduplicação (1 menos artigos únicos a dividir pelo total de capturas, a partir de `n_capturas`). Não é afetado pelos filtros da barra lateral.",
    },
    "dashboard.metric_avg_probability": {"en": "Average relevance probability", "pt": "Probabilidade média de relevância"},
    "dashboard.metric_avg_probability_help": {
        "en": "Average model confidence that a document is relevant, across the currently filtered documents. Reacts to the sidebar filters.",
        "pt": "Confiança média do modelo de que um documento é relevante, entre os documentos atualmente filtrados. Reage aos filtros da barra lateral.",
    },
    "dashboard.section_events_by_type": {"en": "Events by type", "pt": "Eventos por tipo"},
    "dashboard.section_docs_by_source": {"en": "Documents by source", "pt": "Documentos por fonte"},
    "dashboard.section_time_evolution": {"en": "Time evolution", "pt": "Evolução temporal"},
    "dashboard.section_probability_distribution": {"en": "Relevance probability distribution", "pt": "Distribuição da probabilidade de relevância"},
    "dashboard.section_events_by_club": {"en": "Events by club", "pt": "Eventos por clube"},
    "dashboard.col_documents": {"en": "Documents", "pt": "Documentos"},
    "dashboard.col_source": {"en": "Source", "pt": "Fonte"},
    "dashboard.col_club": {"en": "Club", "pt": "Clube"},
    "dashboard.axis_num_documents": {"en": "Number of documents", "pt": "Número de documentos"},
    "dashboard.axis_date": {"en": "Date", "pt": "Data"},
    "dashboard.axis_relevance_probability": {"en": "Relevance probability", "pt": "Probabilidade de relevância"},
    "dashboard.unknown_source": {"en": "Unknown source", "pt": "Fonte desconhecida"},
    "dashboard.not_identified": {"en": "Not identified", "pt": "Não identificado"},
    "dashboard.caption_no_dates": {
        "en": "Not enough valid publication dates for this set of filters.",
        "pt": "Não existem datas de publicação válidas suficientes para este conjunto de filtros.",
    },
    "dashboard.caption_excluded_no_date": {
        "en": "{n} document(s) excluded from this chart — missing publication date.",
        "pt": "{n} documento(s) excluído(s) deste gráfico — sem data de publicação.",
    },
    "dashboard.caption_no_probabilities": {
        "en": "No probabilities available for this set of filters.",
        "pt": "Sem probabilidades disponíveis para este conjunto de filtros.",
    },
    "dashboard.threshold_annotation": {"en": "Current filter: {value}", "pt": "Filtro atual: {value}"},
    "dashboard.caption_probability_distribution_full_corpus": {
        "en": "Shows the full corpus (not affected by the sidebar filters), so you can see where the current \"Minimum relevance probability\" threshold falls relative to the whole distribution.",
        "pt": "Mostra o corpus completo (não é afetado pelos filtros da barra lateral), para veres onde cai o limiar atual de \"Probabilidade mínima de relevância\" em relação à distribuição total.",
    },
    "dashboard.caption_no_clubs": {
        "en": "No clubs identified for this set of filters.",
        "pt": "Sem clubes identificados para este conjunto de filtros.",
    },
    "dashboard.see_research_questions": {
        "en": "Looking for the full breakdown by event category, time, and coverage bias? See the \"Research questions\" page.",
        "pt": "Procuras a distribuição completa por categoria de evento, tempo e viés de cobertura? Ver a página \"Perguntas de investigação\".",
    },
    "dashboard.error_missing_corpus": {
        "en": "corpus_classificado.csv was not found in the project root.",
        "pt": "Não foi encontrado corpus_classificado.csv na raiz do projeto.",
    },

    # -- app_pages/research_questions.py ----------------------------------
    "rq.title": {"en": "Research questions", "pt": "Perguntas de investigação"},
    "rq.caption": {
        "en": "Descriptive results from notebook section 10. These findings do not imply causality — see limitations at the bottom of the page.",
        "pt": "Resultados descritivos da secção 10 do notebook. Estes resultados não implicam causalidade — ver limitações no final da página.",
    },
    "rq.empty": {
        "en": "This page stays empty until you copy the `resultados/` folder (produced by notebook section 10) into the project root.",
        "pt": "Esta página fica vazia até copiares a pasta `resultados/` (produzida pela secção 10 do notebook) para a raiz do projeto.",
    },
    "rq.filters_note": {
        "en": "These are precomputed results (notebook section 10) — the sidebar filters used on other pages do not apply here.",
        "pt": "Estes são resultados pré-calculados (secção 10 do notebook) — os filtros da barra lateral usados noutras páginas não se aplicam aqui.",
    },
    "rq.tab_q1": {"en": "Q1 · By club", "pt": "Q1 · Por clube"},
    "rq.tab_q2": {"en": "Q2 · Over time", "pt": "Q2 · Ao longo do tempo"},
    "rq.tab_q3": {"en": "Q3 · Coverage bias", "pt": "Q3 · Viés de cobertura"},
    "rq.tab_models": {"en": "Model quality", "pt": "Qualidade dos modelos"},
    "rq.tab_context": {"en": "Context & limitations", "pt": "Contexto & limitações"},
    "rq.q1_header": {
        "en": "Q1 · How many financing-related documents were identified per club, and across which categories?",
        "pt": "Q1 · Quantos documentos relacionados com financiamento foram identificados por clube, e como se distribuem pelas categorias?",
    },
    "rq.q1_body": {
        "en": "How many financing-related archived documents were identified for each club, and how are they distributed across the three rule-based categories (**capital-market debt**, **bank & debt financing**, **capital increase**)?",
        "pt": "Quantos documentos arquivados relacionados com financiamento foram identificados para cada clube, e como se distribuem pelas três categorias baseadas em regras (**dívida em mercado de capitais**, **financiamento bancário e dívida**, **aumento de capital**)?",
    },
    "rq.q1_missing": {"en": "`q1_documentos_por_clube_categoria.csv` not found.", "pt": "`q1_documentos_por_clube_categoria.csv` não encontrado."},
    "rq.axis_num_events": {"en": "Number of events", "pt": "Número de eventos"},
    "rq.legend_event_subtype": {"en": "Event sub-type", "pt": "Subtipo de evento"},
    "rq.q2_header": {
        "en": "Q2 · How are financing-related documents distributed over time?",
        "pt": "Q2 · Como se distribuem os documentos relacionados com financiamento ao longo do tempo?",
    },
    "rq.q2_body": {
        "en": "How are the relevant documents distributed between 2019 and 2025, and in which years are greater concentrations observed?",
        "pt": "Como se distribuem os documentos relevantes entre 2019 e 2025, e em que anos se observam maiores concentrações?",
    },
    "rq.q2_missing_club": {"en": "`q2_documentos_por_ano_clube.csv` not found.", "pt": "`q2_documentos_por_ano_clube.csv` não encontrado."},
    "rq.q2_missing_type": {"en": "`q2_documentos_por_ano_categoria.csv` not found.", "pt": "`q2_documentos_por_ano_categoria.csv` não encontrado."},
    "rq.axis_year": {"en": "Year", "pt": "Ano"},
    "rq.legend_club": {"en": "Club", "pt": "Clube"},
    "rq.q2_caption": {
        "en": "The analysis is restricted to 2019–2025 (2026 excluded as incomplete). Years above the mean plus one standard deviation are annotated automatically below — read them against known seasons, transfer windows, or the COVID-19 period rather than as proof of causation.",
        "pt": "A análise está restrita a 2019–2025 (2026 excluído por estar incompleto). Os anos acima da média mais um desvio-padrão são assinalados automaticamente abaixo — interpreta-os à luz de épocas, janelas de transferências, ou do período COVID-19, e não como prova de causalidade.",
    },
    "rq.q3_header": {
        "en": "Q3 · How much does archival coverage vary between clubs, sources, and years?",
        "pt": "Q3 · Quanto varia a cobertura arquivística entre clubes, fontes e anos?",
    },
    "rq.q3_body": {
        "en": "How much does archival coverage vary between clubs, sources, and years, and how may this affect comparisons?",
        "pt": "Quanto varia a cobertura arquivística entre clubes, fontes e anos, e como pode isso afetar as comparações?",
    },
    "rq.q3_missing": {"en": "`q3_indicadores_cobertura.csv` not found.", "pt": "`q3_indicadores_cobertura.csv` não encontrado."},
    "rq.axis_num_news": {"en": "Number of news items", "pt": "Número de notícias"},
    "rq.legend_source": {"en": "Source", "pt": "Fonte"},
    "rq.models_header": {"en": "Classifier quality", "pt": "Qualidade dos classificadores"},
    "rq.models_missing": {
        "en": "`resumo_modelos.csv` not found — run notebook section 10.6.",
        "pt": "`resumo_modelos.csv` não encontrado — corre a secção 10.6 do notebook.",
    },
    "rq.col_accuracy": {"en": "Accuracy", "pt": "Exatidão"},
    "rq.col_precision": {"en": "Precision", "pt": "Precisão"},
    "rq.col_recall": {"en": "Recall", "pt": "Recall"},
    "rq.col_f1": {"en": "F1", "pt": "F1"},
    "rq.confidence_subheader": {"en": "Relevance classifier confidence", "pt": "Confiança do classificador de relevância"},
    "rq.confidence_caption": {
        "en": "Distribution of predicted relevance probability across the corpus — a model clustered near 0.5 is guessing; clustering near 0 or 1 means confident, decisive predictions.",
        "pt": "Distribuição da probabilidade de relevância prevista em todo o corpus — um modelo concentrado perto de 0,5 está a adivinhar; concentração perto de 0 ou 1 significa previsões confiantes e decisivas.",
    },
    "rq.axis_num_documents": {"en": "Number of documents", "pt": "Número de documentos"},
    "rq.q3_ratio_metric": {"en": "Coverage ratio (max ÷ min)", "pt": "Rácio de cobertura (máx ÷ mín)"},
    "rq.q3_ratio_help": {
        "en": "Unique news items for the most-covered club divided by the least-covered one. A ratio far from 1 signals archival coverage bias, not necessarily a real difference in financial activity.",
        "pt": "Notícias únicas do clube mais coberto a dividir pelo menos coberto. Um rácio longe de 1 indica viés de cobertura arquivística, não necessariamente uma diferença real de atividade financeira.",
    },
    "rq.annotation_covid": {"en": "COVID-19", "pt": "COVID-19"},
    "rq.col_unique_news": {"en": "Unique news items", "pt": "Notícias únicas"},
    "rq.col_num_sources": {"en": "Number of sources", "pt": "Número de fontes"},
    "rq.col_first_year": {"en": "First year", "pt": "Primeiro ano"},
    "rq.col_last_year": {"en": "Last year", "pt": "Último ano"},
    "rq.col_years_covered": {"en": "Years covered", "pt": "Anos com cobertura"},
    "rq.col_relevant_news": {"en": "Relevant news items", "pt": "Notícias relevantes"},
    "rq.col_pct_relevant": {"en": "% relevant", "pt": "% relevante"},
    "rq.col_documented_events": {"en": "Documented events", "pt": "Eventos documentados"},
    "rq.col_classified_events": {"en": "Classified events", "pt": "Eventos classificados"},
    "rq.col_documentation_rate": {"en": "Documentation rate (%)", "pt": "Taxa de documentação (%)"},
    "rq.why_nlp_header": {"en": "Is NLP the right approach here?", "pt": "O NLP é a abordagem certa aqui?"},
    "rq.why_nlp_body": {
        "en": """The underlying evidence — years of archived news coverage — exists
only as **unstructured text**, spread across dozens of sources with no
shared schema. Answering Q1–Q3 by hand would mean reading thousands of
archived pages per club just to find the ones that even mention financing.

NLP is an effective fit because each question maps to a specific,
well-established technique:

- **Q1** (how many documents, by category) needs **text classification** to
  turn free text into a structured label (relevant / not relevant, then
  event category) at a volume no manual process could sustain.
- **Q2** (temporal clustering) only becomes visible once every article has
  been classified and dated — it is a downstream view of the same
  classification output, not a separate technique.
- **Q3** (coverage bias) requires comparing *volumes* of text across clubs
  and sources, which again depends on first having a reliable, automatic
  way to decide what counts as a relevant document.

The NLP lab page adds named entity recognition, keyword extraction,
sentiment analysis, and summarization on top of this — they are not
required to answer Q1–Q3, but they demonstrate the same text can be mined
for *who* is involved, *what* the article is about, *how* it is framed,
and a compact readable digest, which is exactly the kind of added value
NLP brings over keyword search on unstructured archives.""",
        "pt": """As evidências de base — anos de cobertura noticiosa arquivada —
existem apenas como **texto não estruturado**, espalhado por dezenas de
fontes sem esquema comum. Responder a Q1–Q3 manualmente implicaria ler
milhares de páginas arquivadas por clube só para encontrar as que sequer
mencionam financiamento.

O NLP é uma escolha eficaz porque cada pergunta corresponde a uma técnica
específica e bem estabelecida:

- **Q1** (quantos documentos, por categoria) precisa de **classificação de
  texto** para transformar texto livre num rótulo estruturado (relevante /
  não relevante, depois categoria de evento) a um volume que nenhum
  processo manual sustentaria.
- **Q2** (agrupamento temporal) só se torna visível depois de cada artigo
  estar classificado e datado — é uma vista derivada do mesmo resultado de
  classificação, não uma técnica separada.
- **Q3** (viés de cobertura) exige comparar *volumes* de texto entre
  clubes e fontes, o que de novo depende de existir primeiro uma forma
  fiável e automática de decidir o que conta como documento relevante.

A página do laboratório de NLP acrescenta reconhecimento de entidades,
extração de palavras-chave, análise de sentimento e sumarização por cima
disto — não são necessários para responder a Q1–Q3, mas demonstram que o
mesmo texto pode ser explorado para saber *quem* está envolvido, *sobre o
que* é o artigo, *como* é enquadrado, e um resumo compacto e legível, que é
exatamente o tipo de valor acrescentado que o NLP traz face à pesquisa por
palavras-chave em arquivos não estruturados.""",
    },
    "rq.synthesis_header": {"en": "Automatic synthesis", "pt": "Síntese automática"},
    "rq.limitations_header": {"en": "Limitations and interpretation caveats", "pt": "Limitações e critérios de interpretação"},
    "rq.limitations_body": {
        "en": """- The observed unit is a **classified news item**, not necessarily
  a single economic event — different articles can refer to the
  same underlying operation.
- Automatic classification is limited by the size and balance of
  the annotated set, especially for minority classes.
- Arquivo.pt coverage varies across sources, clubs, and years — a
  higher count can reflect better archival coverage rather than
  more financial activity.
- The event category is assigned by lexical rules, not a trained
  classifier — it favors precision on well-worded articles and can
  miss paraphrased or ambiguous ones (see the "unclear/multiple"
  bucket).
- Temporal spikes are descriptive and do not establish causal
  links to crises, seasons, or transfer windows.""",
        "pt": """- A unidade observada é uma **notícia classificada**, não necessariamente um
  evento económico único — notícias diferentes podem referir-se à mesma
  operação.
- A classificação automática está limitada pela dimensão e pelo equilíbrio
  do conjunto anotado, sobretudo nas classes minoritárias.
- A cobertura do Arquivo.pt varia entre fontes, clubes e anos — uma
  contagem superior pode refletir melhor cobertura arquivística, e não
  necessariamente mais atividade financeira.
- A categoria do evento é atribuída por regras lexicais, não por um
  classificador treinado — favorece precisão em artigos bem escritos e
  pode falhar em artigos parafraseados ou ambíguos (ver o resíduo
  "pouco claro/múltiplo").
- Os picos temporais são descritivos e não estabelecem relações causais
  com crises, épocas ou janelas de transferências.""",
    },

    # -- app_pages/events.py -----------------------------------------------
    "events.title": {"en": "Event explorer", "pt": "Explorador de eventos"},
    "events.caption": {
        "en": "Browse classified news items, ranked by relevance probability.",
        "pt": "Percorre as notícias classificadas, ordenadas por probabilidade de relevância.",
    },
    "events.empty": {"en": "No events match the selected filters.", "pt": "Não existem eventos para os filtros selecionados."},
    "events.slider_label": {"en": "Maximum number of events shown", "pt": "Número máximo de eventos apresentados"},
    "events.untitled": {"en": "Untitled document", "pt": "Documento sem título"},
    "events.club_unknown": {"en": "Club not identified", "pt": "Clube não identificado"},
    "events.source_unknown": {"en": "Unknown source", "pt": "Fonte desconhecida"},
    "events.date_unknown": {"en": "Unknown date", "pt": "Data desconhecida"},
    "events.label_club": {"en": "Club", "pt": "Clube"},
    "events.label_event": {"en": "Event", "pt": "Evento"},
    "events.label_date": {"en": "Date", "pt": "Data"},
    "events.label_source": {"en": "Source", "pt": "Fonte"},
    "events.no_text": {"en": "This record has no available text.", "pt": "Este registo não contém texto disponível."},
    "events.open_source": {"en": "Open original source", "pt": "Abrir fonte original"},
    "events.open_archive": {"en": "Open archived version", "pt": "Abrir versão arquivada"},
    "events.analyze_button": {"en": "Analyze in the NLP lab", "pt": "Analisar no laboratório de NLP"},

    # -- app_pages/nlp_lab.py -----------------------------------------------
    "nlp.title": {"en": "NLP lab", "pt": "Laboratório de NLP"},
    "nlp.caption1": {
        "en": "Named entity recognition, keyword extraction, sentiment analysis, and summarization applied live to a corpus article or free text — the techniques from the assignment brief that data collection alone does not cover.",
        "pt": "Reconhecimento de entidades, extração de palavras-chave, análise de sentimento e sumarização aplicados ao vivo a um artigo do corpus ou a texto livre — as técnicas do enunciado que a recolha de dados por si só não cobre.",
    },
    "nlp.caption2": {
        "en": "Note: the underlying news corpus and NLP models (spaCy, YAKE) are tuned for Portuguese, since the source articles collected from Arquivo.pt are written in Portuguese — that stays true regardless of the interface language.",
        "pt": "Nota: o corpus de notícias e os modelos de NLP (spaCy, YAKE) estão configurados para português, porque os artigos-fonte recolhidos do Arquivo.pt estão escritos em português — isso mantém-se independentemente da língua da interface.",
    },
    "nlp.models_disabled": {
        "en": "Relevance classification disabled — copy `modelo_relevancia.joblib` into the project root to enable it. The event category preview below always works, since it's rule-based.",
        "pt": "Classificação de relevância desativada — copia `modelo_relevancia.joblib` para a raiz do projeto para a ativar. A pré-visualização da categoria do evento abaixo funciona sempre, por ser baseada em regras.",
    },
    "nlp.source_label": {"en": "Text source", "pt": "Fonte de texto"},
    "nlp.source_corpus": {"en": "Corpus article", "pt": "Artigo do corpus"},
    "nlp.source_free": {"en": "Free text", "pt": "Texto livre"},
    "nlp.article_label": {"en": "Article", "pt": "Artigo"},
    "nlp.analyze_article": {"en": "Analyze article", "pt": "Analisar artigo"},
    "nlp.paste_label": {"en": "Paste a news item or press release", "pt": "Cola aqui uma notícia ou comunicado"},
    "nlp.use_example": {"en": "Use example text", "pt": "Usar texto de exemplo"},
    "nlp.analyze_text": {"en": "Analyze text", "pt": "Analisar texto"},
    "nlp.warn_empty": {"en": "Write or select a text before analyzing.", "pt": "Escreve ou seleciona um texto antes de analisar."},
    "nlp.info_start": {"en": "Pick an article or paste free text, then click analyze.", "pt": "Escolhe um artigo ou cola texto livre e clica em analisar."},
    "nlp.expander_text": {"en": "Text under analysis", "pt": "Texto em análise"},
    "nlp.classification_header": {"en": "Classification (notebook sections 7–8)", "pt": "Classificação (secções 7–8 do notebook)"},
    "nlp.metric_relevance": {"en": "Predicted relevance", "pt": "Relevância prevista"},
    "nlp.relevant": {"en": "Relevant", "pt": "Relevante"},
    "nlp.not_relevant": {"en": "Not relevant", "pt": "Não relevante"},
    "nlp.metric_event_type": {"en": "Event category (rule-based)", "pt": "Categoria do evento (baseada em regras)"},
    "nlp.event_type_help": {
        "en": "Lexical rules over financing terminology, not a trained classifier — the same logic the notebook applies to every document predicted as relevant.",
        "pt": "Regras lexicais sobre terminologia de financiamento, não um classificador treinado — a mesma lógica que o notebook aplica a cada documento previsto como relevante.",
    },
    "nlp.tab_entities": {"en": "Entities", "pt": "Entidades"},
    "nlp.tab_keywords": {"en": "Keywords", "pt": "Palavras-chave"},
    "nlp.tab_sentiment": {"en": "Sentiment", "pt": "Sentimento"},
    "nlp.tab_summary": {"en": "Summary", "pt": "Resumo"},
    "nlp.ner_subheader": {"en": "Named entities (NER)", "pt": "Entidades mencionadas (NER)"},
    "nlp.ner_empty": {"en": "No entities identified in this text.", "pt": "Nenhuma entidade identificada neste texto."},
    "nlp.kw_subheader": {"en": "Keywords (YAKE)", "pt": "Palavras-chave (YAKE)"},
    "nlp.kw_caption": {"en": "Lower score = more relevant keyword.", "pt": "Pontuação mais baixa = palavra-chave mais relevante."},
    "nlp.kw_empty": {"en": "Could not extract keywords from this text.", "pt": "Não foi possível extrair palavras-chave deste texto."},
    "nlp.col_keyword": {"en": "Keyword", "pt": "Palavra-chave"},
    "nlp.col_yake_score": {"en": "YAKE score", "pt": "Pontuação YAKE"},
    "nlp.sentiment_subheader": {"en": "Sentiment analysis", "pt": "Análise de sentimento"},
    "nlp.metric_sentiment": {"en": "Predicted sentiment", "pt": "Sentimento previsto"},
    "nlp.sentiment_caption": {
        "en": "Generic multilingual model (not fine-tuned on financial news) — use as an exploratory indicator of the article's tone, not as a financial fact.",
        "pt": "Modelo multilingue genérico (não treinado especificamente em notícias financeiras) — usar como indicador exploratório do tom da notícia, não como facto financeiro.",
    },
    "nlp.extractive_subheader": {"en": "Extractive summary", "pt": "Resumo extrativo"},
    "nlp.extractive_caption": {
        "en": "Original sentences most central to the text, selected by TF-IDF similarity.",
        "pt": "Frases originais mais centrais ao texto, selecionadas por similaridade TF-IDF.",
    },
    "nlp.llm_subheader": {"en": "Local LLM summary (optional)", "pt": "Resumo por LLM local (opcional)"},
    "nlp.llm_caption": {
        "en": "Uses a multilingual mT5 summarization model (`csebuetnlp/mT5_multilingual_XLSum`), loaded locally. The first generation may take a few minutes while the model downloads.",
        "pt": "Usa um modelo mT5 multilingue de sumarização (`csebuetnlp/mT5_multilingual_XLSum`), carregado localmente. A primeira geração pode demorar alguns minutos a descarregar o modelo.",
    },
    "nlp.llm_button": {"en": "Generate summary with LLM", "pt": "Gerar resumo com LLM"},
    "nlp.llm_spinner": {"en": "Generating summary with the local model...", "pt": "A gerar resumo com o modelo local..."},
    "nlp.llm_error": {
        "en": "Could not generate the summary with the local LLM: {error}",
        "pt": "Não foi possível gerar o resumo com o LLM local: {error}",
    },

    # -- app_pages/assistant.py -------------------------------------------
    "assistant.title": {"en": "Assistant", "pt": "Assistente"},
    "assistant.caption": {
        "en": "Ask questions about the corpus in English or Portuguese. Answers are grounded in retrieved articles, shown as sources below each reply.",
        "pt": "Faz perguntas sobre o corpus em português ou inglês. As respostas baseiam-se em artigos recuperados, apresentados como fontes abaixo de cada resposta.",
    },
    "assistant.caveat": {
        "en": "Runs a small local model (`Qwen2.5-0.5B-Instruct`) — answers can be terse or wrong, always check the sources. Not designed for counting/aggregation questions (e.g. \"how many bond issuances in 2023\"); use the Dashboard and Research questions pages for that.",
        "pt": "Usa um modelo local pequeno (`Qwen2.5-0.5B-Instruct`) — as respostas podem ser incompletas ou incorretas, confirma sempre nas fontes. Não serve para perguntas de contagem/agregação (ex.: \"quantas emissões de obrigações em 2023\"); usa o Dashboard e as Perguntas de investigação para isso.",
    },
    "assistant.no_corpus": {
        "en": "No corpus loaded — nothing to answer questions about yet.",
        "pt": "Nenhum corpus carregado — ainda não há dados sobre os quais responder.",
    },
    "assistant.suggestions_label": {"en": "Try asking:", "pt": "Experimenta perguntar:"},
    "assistant.input_placeholder": {
        "en": "Ask about a club, a bond issuance, a financing event...",
        "pt": "Pergunta sobre um clube, uma emissão de obrigações, um evento de financiamento...",
    },
    "assistant.thinking_spinner": {
        "en": "Searching the corpus and generating an answer with the local model...",
        "pt": "A pesquisar no corpus e a gerar resposta com o modelo local...",
    },
    "assistant.sources_label": {"en": "Sources ({n})", "pt": "Fontes ({n})"},
    "assistant.no_context_found": {
        "en": "I could not find anything relevant to that question in the corpus.",
        "pt": "Não encontrei nada relevante para essa pergunta no corpus.",
    },
    "assistant.error": {
        "en": "Could not generate an answer with the local assistant: {error}",
        "pt": "Não foi possível gerar uma resposta com o assistente local: {error}",
    },


    # -- app_pages/data_export.py ---------------------------------------------
    "data.title": {"en": "Data & export", "pt": "Dados e exportação"},
    "data.caption": {"en": "Filtered dataset, ready to inspect or download as CSV.", "pt": "Base filtrada, pronta a inspecionar ou descarregar em CSV."},
    "data.col_date": {"en": "Date", "pt": "Data"},
    "data.col_relevance_prob": {"en": "Relevance probability", "pt": "Probabilidade de relevância"},
    "data.col_event_confidence": {"en": "Event type confidence", "pt": "Confiança do tipo de evento"},
    "data.col_original_source": {"en": "Original source", "pt": "Fonte original"},
    "data.download_button": {"en": "Download filtered results", "pt": "Descarregar resultados filtrados"},

    # -- app_pages/methodology.py ---------------------------------------------
    "meth.title": {"en": "Methodology", "pt": "Metodologia"},
    "meth.body": {
        "en": """This app presents a corporate-intelligence pipeline applied to
Portuguese football, focused on financing and capital-market events at
Benfica SAD, FC Porto SAD, and Sporting SAD.

### Pipeline (notebook)

1. **Collection** of news via the Arquivo.pt API, partitioned by (host,
   year) to work around the 500-results-per-search cap.
2. **Cleaning and normalization** of text (HTML entities, URLs,
   whitespace).
3. **Human annotation** of a sampled subset (positives, hard negatives,
   easy negatives) to build a gold-standard set.
4. **Binary relevance classification** (TF-IDF + logistic regression),
   trained on the human annotations.
5. **Rule-based event category**: lexical regex patterns assign each
   relevant document to capital-market debt, bank/debt financing, capital
   increase, or a residual "unclear/multiple" bucket — not a trained
   classifier.
6. **Named entities and financial-field extraction** (spaCy NER +
   regex) over the relevant documents — amounts, rates, and maturity
   dates.
7. **Analysis** — distribution by club/category, time evolution,
   coverage indicators, and possible bias between sources.

### In this prototype (Streamlit)

The pipeline above covers collection, cleaning, and **text
classification**. The remaining techniques required by the assignment
brief — **named entity recognition (NER)**, **keyword extraction**,
**sentiment analysis**, and **summarization** — are applied live on
the "NLP lab" page, to any corpus article or user-pasted text:

- **NER** — spaCy (`pt_core_news_sm`), entities of type person,
  organization, and location.
- **Keywords** — YAKE, unsupervised extraction tuned for Portuguese.
- **Sentiment** — multilingual Transformer model
  (`lxyuan/distilbert-base-multilingual-cased-sentiments-student`).
- **Extractive summarization** — TF-IDF + sentence centrality (no
  external model).
- **Abstractive summarization (optional LLM)** — multilingual mT5
  (`csebuetnlp/mT5_multilingual_XLSum`), loaded locally, with no calls
  to paid APIs.

Relevance classification in the NLP lab reuses the model trained in the
notebook (`modelo_relevancia.joblib`), when present in the project root.
The event category preview reuses the notebook's rule-based logic
directly, so it always works, with or without that file.

### Why NLP for this problem?

The evidence base — years of archived news coverage — exists only as
unstructured text, spread across dozens of sources with no shared
schema. Manually reading everything to spot financing events does not
scale. NLP turns that free text into structured, comparable signal:
classification answers *how many* documents are relevant and *of what
category*, while NER, keyword extraction, sentiment, and summarization
surface *who* is involved, *what* each article is about, and a compact
digest of *why* it matters — see the "Research questions" page for how
this maps to each question.""",
        "pt": """Esta app apresenta um pipeline de inteligência corporativa aplicado
ao futebol português, focado em eventos de financiamento e mercado de
capitais do Benfica SAD, FC Porto SAD e Sporting SAD.

### Pipeline (notebook)

1. **Recolha** de notícias via a API do Arquivo.pt, particionada por
   (host, ano) para contornar o teto de 500 resultados por pesquisa.
2. **Limpeza e normalização** de texto (entidades HTML, URLs, espaços).
3. **Anotação humana** de uma amostra (positivos, negativos difíceis,
   negativos fáceis) para construir um conjunto gold-standard.
4. **Classificação binária de relevância** (TF-IDF + regressão
   logística), treinada nas anotações humanas.
5. **Categoria de evento baseada em regras**: padrões lexicais (regex)
   atribuem a cada documento relevante uma categoria — dívida em
   mercado de capitais, financiamento bancário/dívida, aumento de
   capital, ou um resíduo "pouco claro/múltiplo" — não é um classificador
   treinado.
6. **Entidades e extração de campos financeiros** (NER com spaCy +
   regex) sobre os documentos relevantes — montantes, taxas e datas de
   maturidade.
7. **Análise** — distribuição por clube/categoria, evolução temporal,
   indicadores de cobertura e possível viés entre fontes.

### Neste protótipo (Streamlit)

O pipeline acima cobre recolha, limpeza e **classificação de texto**.
As restantes técnicas pedidas no enunciado — **reconhecimento de
entidades (NER)**, **extração de palavras-chave**, **análise de
sentimento** e **sumarização** — são aplicadas ao vivo na página
"Laboratório de NLP", sobre qualquer artigo do corpus ou texto colado
pelo utilizador:

- **NER** — spaCy (`pt_core_news_sm`), entidades de tipo pessoa,
  organização e local.
- **Palavras-chave** — YAKE, extração não supervisionada específica
  para português.
- **Sentimento** — modelo Transformer multilingue
  (`lxyuan/distilbert-base-multilingual-cased-sentiments-student`).
- **Sumarização extrativa** — TF-IDF + centralidade de frases (sem
  modelo externo).
- **Sumarização abstrativa (LLM opcional)** — mT5 multilingue
  (`csebuetnlp/mT5_multilingual_XLSum`), carregado localmente, sem
  chamadas a APIs pagas.

A classificação de relevância no laboratório de NLP reutiliza o modelo
treinado no notebook (`modelo_relevancia.joblib`), quando presente na
raiz do projeto. A pré-visualização da categoria do evento reutiliza
diretamente a lógica baseada em regras do notebook, por isso funciona
sempre, com ou sem esse ficheiro.

### Porque é o NLP a abordagem certa?

A base de evidência — anos de cobertura noticiosa arquivada — existe
apenas como texto não estruturado, espalhado por dezenas de fontes sem
esquema comum. Ler tudo manualmente para identificar eventos de
financiamento não é escalável. O NLP transforma esse texto livre em
sinal estruturado e comparável: a classificação responde a *quantos*
documentos são relevantes e *de que categoria*, enquanto NER, extração
de palavras-chave, sentimento e sumarização revelam *quem* está
envolvido, *sobre o que* é cada artigo, e um resumo compacto de
*porque* é relevante — ver a página "Perguntas de investigação" para a
relação com cada pergunta.""",
    },
    "meth.status_header": {"en": "Loaded data status", "pt": "Estado dos dados carregados"},
    "meth.metric_classifiers": {"en": "Relevance classifier (.joblib)", "pt": "Classificador de relevância (.joblib)"},
    "meth.classifiers_loaded": {"en": "Loaded", "pt": "Carregado"},
    "meth.classifiers_not_found": {"en": "Not found", "pt": "Não encontrado"},
    "meth.metric_results": {"en": "Research results", "pt": "Resultados de investigação"},
    "meth.results_available": {"en": "Available", "pt": "Disponíveis"},
    "meth.results_not_loaded": {"en": "Not loaded", "pt": "Não carregados"},
    "meth.caption_copy_files": {
        "en": "Copy the files produced by notebook section 10 (`corpus_classificado.csv`, `modelo_relevancia.joblib`, the `resultados/` folder) into this project's root to unlock the corresponding sections.",
        "pt": "Copia os ficheiros produzidos pela secção 10 do notebook (`corpus_classificado.csv`, `modelo_relevancia.joblib`, a pasta `resultados/`) para a raiz deste projeto para desbloquear as secções correspondentes.",
    },
    "meth.notebook_header": {"en": "Full notebook", "pt": "Notebook completo"},
    "meth.notebook_body": {
        "en": "Download the Jupyter notebook with the full NLP pipeline used to produce the data behind this app — collection, annotation, classifier training, and extraction.",
        "pt": "Descarrega o notebook Jupyter com o pipeline de NLP completo usado para produzir os dados por trás desta app — recolha, anotação, treino do classificador e extração.",
    },
    "meth.notebook_download_label": {"en": "Download notebook (.ipynb)", "pt": "Descarregar notebook (.ipynb)"},
    "meth.limitations_header": {"en": "Limitations", "pt": "Limitações"},
    "meth.logo_credit": {
        "en": "Club crests and the Porto Business School logo are sourced from Wikipedia / Wikimedia Commons and remain the trademarks of their respective owners; used here only to identify the clubs and institution for this non-commercial academic prototype.",
        "pt": "Os emblemas dos clubes e o logótipo da Porto Business School têm origem na Wikipédia / Wikimedia Commons e continuam a ser marcas registadas dos respetivos titulares; usados aqui apenas para identificar os clubes e a instituição neste protótipo académico não comercial.",
    },
    "meth.limitations_body": {
        "en": """- Results support documentary analysis; they do not replace human
  validation.
- Sentiment analysis uses a generic multilingual model, not one
  specialized in financial text.
- Arquivo.pt coverage varies across sources, clubs, and years —
  volume differences can reflect availability, not real financial
  activity.
- Amounts, rates, dates, and terms extracted by regex are
  candidates and require contextual validation.""",
        "pt": """- Os resultados são um apoio à análise documental; não substituem a
  validação humana.
- A análise de sentimento usa um modelo genérico multilingue, não
  especializado em texto financeiro.
- A cobertura do Arquivo.pt varia entre fontes, clubes e anos —
  diferenças de volume podem refletir disponibilidade, não atividade
  financeira real.
- Montantes, taxas, datas e prazos extraídos por regex são candidatos
  e exigem validação contextual.""",
    },
}

EVENT_LABELS: dict[str, dict[str, str]] = {
    "capital_market_debt": {"en": "Capital-market debt", "pt": "Dívida em mercado de capitais"},
    "bank_and_debt_financing": {"en": "Bank & debt financing", "pt": "Financiamento bancário e dívida"},
    "capital_increase": {"en": "Capital increase", "pt": "Aumento de capital"},
    "multiple_or_ambiguous": {"en": "Multiple / ambiguous", "pt": "Múltiplo / ambíguo"},
    "other_or_unclear": {"en": "Other / unclear", "pt": "Outro / pouco claro"},
    "not_applicable": {"en": "Not applicable (not relevant)", "pt": "Não aplicável (não relevante)"},
    "unknown": {"en": "Not identified", "pt": "Não identificado"},
    "": {"en": "Not identified", "pt": "Não identificado"},
}

ENTITY_TYPE_LABELS: dict[str, dict[str, str]] = {
    "PER": {"en": "Person", "pt": "Pessoa"},
    "ORG": {"en": "Organization", "pt": "Organização"},
    "LOC": {"en": "Location", "pt": "Local"},
    "GPE": {"en": "Location", "pt": "Local"},
    "MISC": {"en": "Miscellaneous", "pt": "Diverso"},
}

SENTIMENT_LABELS: dict[str, dict[str, str]] = {
    "positive": {"en": "Positive", "pt": "Positivo"},
    "neutral": {"en": "Neutral", "pt": "Neutro"},
    "negative": {"en": "Negative", "pt": "Negativo"},
}

# Curated starter questions for the assistant page, phrased with the same
# vocabulary as EVENT_CATEGORY_PATTERNS (lib/nlp.py) so TF-IDF retrieval
# reliably finds a good match — one per club per event category.
ASSISTANT_SUGGESTED_QUESTIONS: dict[str, list[str]] = {
    "en": [
        "What bonds did Sporting SAD issue?",
        "What was the amount of Benfica SAD's bond issuance?",
        "How did FC Porto SAD finance its bank debt?",
        "Was there a capital increase at Benfica SAD?",
        "Did Sporting SAD refinance any debt?",
        "What credit line did FC Porto SAD contract?",
    ],
    "pt": [
        "Que obrigações emitiu o Sporting SAD?",
        "Qual foi o valor da emissão obrigacionista do Benfica SAD?",
        "Como é que o FC Porto SAD financiou a dívida junto da banca?",
        "Houve algum aumento de capital no Benfica SAD?",
        "O Sporting SAD fez algum refinanciamento de dívida?",
        "Que linha de crédito contratou o FC Porto SAD?",
    ],
}


def get_lang() -> str:
    return st.session_state.get("lang", DEFAULT_LANG)


def t(key: str, **kwargs) -> str:
    entry = STRINGS.get(key)
    if entry is None:
        return key
    text = entry.get(get_lang(), entry.get(DEFAULT_LANG, key))
    return text.format(**kwargs) if kwargs else text


def event_label(raw_value: str) -> str:
    key = (raw_value or "").strip().lower()
    entry = EVENT_LABELS.get(key)
    if entry is None:
        return key.replace("_", " ").title() or EVENT_LABELS[""][get_lang()]
    return entry.get(get_lang(), entry[DEFAULT_LANG])


def entity_label(raw_type: str) -> str:
    entry = ENTITY_TYPE_LABELS.get(raw_type)
    return entry.get(get_lang(), raw_type) if entry else raw_type


def sentiment_label(raw_label: str) -> str:
    entry = SENTIMENT_LABELS.get((raw_label or "").strip().lower())
    return entry.get(get_lang(), raw_label) if entry else raw_label
