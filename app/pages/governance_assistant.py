from __future__ import annotations

import streamlit as st

from app.i18n import LOCALE_EN_US, Locale
from src.governance_rag import LocalIndex, RagError, answer_question, load_corpus


def render_governance_assistant(locale: Locale) -> None:
    is_en = locale == LOCALE_EN_US
    st.title("Governance Assistant" if is_en else "Assistente de Governan\u00e7a")
    st.caption(
        "Check the answer against its sources. Retrieved excerpts are evidence, not authorization to act."
        if is_en else
        "Confira a resposta nas fontes. Trechos recuperados s\u00e3o evid\u00eancias, n\u00e3o autoriza\u00e7\u00e3o para agir."
    )
    try:
        corpus = load_corpus()
    except RagError as exc:
        st.error(str(exc))
        return
    except Exception:
        st.error("Unable to load the local corpus." if is_en else "N\u00e3o foi poss\u00edvel carregar a base local.")
        return
    for notice in corpus.notices:
        st.warning(notice)
    source_count = len({chunk.source for chunk in corpus.chunks})
    st.caption(
        f"Approved sources: {source_count} | Excerpts: {len(corpus.chunks)}"
        if is_en else f"Fontes aprovadas: {source_count} | Trechos: {len(corpus.chunks)}"
    )
    if not corpus.chunks:
        st.info(
            "No approved sources are available. Review the source manifest and content hashes."
            if is_en else
            "Nenhuma fonte aprovada dispon\u00edvel. Revise o manifesto de fontes e os hashes do conte\u00fado."
        )
    with st.form("governance_rag_question"):
        question = st.text_area("Question" if is_en else "Pergunta", max_chars=2000)
        mode = st.radio(
            "Mode" if is_en else "Modo", options=["local", "openai"], horizontal=True,
            format_func=lambda value: "Local (TF-IDF)" if value == "local" else "OpenAI (API)",
        )
        consent = st.checkbox(
            "I authorize sending this question and approved excerpts to OpenAI (possible charges)."
            if is_en else
            "Autorizo enviar esta pergunta e os trechos aprovados \u00e0 OpenAI (pode haver cobran\u00e7a).",
            value=False,
        )
        submitted = st.form_submit_button(
            "Ask" if is_en else "Consultar", icon=":material/search:",
        )
    if not submitted:
        return
    if not question.strip():
        st.warning("Enter a question." if is_en else "Informe uma pergunta.")
        return
    try:
        result = answer_question(LocalIndex(corpus.chunks), question, mode=mode, consent=consent)
    except RagError as exc:
        st.error(str(exc))
        return
    except Exception:
        st.error(
            "Unable to answer. Try the local mode or review the source configuration."
            if is_en else "N\u00e3o foi poss\u00edvel responder. Use o modo local ou confira a configura\u00e7\u00e3o das fontes."
        )
        return
    st.caption(f"{'Mode used' if is_en else 'Modo utilizado'}: {result.mode} | TF-IDF")
    st.caption(
        ("External call: yes" if result.external_called else "External call: no")
        if is_en else
        ("Chamada externa: realizada" if result.external_called else "Chamada externa: n\u00e3o realizada")
    )
    st.subheader("Answer" if is_en else "Resposta")
    if result.supported:
        st.text(result.text)
    else:
        st.info("Insufficient evidence in the approved sources." if is_en else result.text)
    if result.hits:
        st.subheader("Sources and retrieved excerpts" if is_en else "Fontes e trechos recuperados")
    for hit in result.hits:
        chunk = hit.chunk
        with st.expander(f"[{hit.citation}] {chunk.source}:{chunk.start_line}-{chunk.end_line}"):
            st.caption(f"TF-IDF cosine: {hit.score:.3f} | SHA-256 (LF): {chunk.sha256}")
            st.text(f"{chunk.title}\nmtime UTC: {chunk.modified_at}")
            if chunk.dataset or chunk.owner:
                st.text(f"dataset: {chunk.dataset}\nowner: {chunk.owner}")
            st.code(chunk.text, language="text", wrap_lines=True)