from __future__ import annotations

from dataclasses import replace

import pytest
from streamlit.testing.v1 import AppTest

from app.pages import governance_assistant as page
from src import governance_rag as rag


def app_test():
    return AppTest.from_string(
        "from app.pages.governance_assistant import render_governance_assistant\n"
        "render_governance_assistant('pt-BR')"
    )


@pytest.fixture
def corpus():
    return rag.Corpus(rag.split_document(
        "dataset: orders\nquality: no_duplicate_primary_key\npublication: blocked",
        source="contracts/orders.yml", sha256="b" * 64, owner="governance",
    ), ())


def test_empty_state_and_empty_question(monkeypatch):
    monkeypatch.setattr(page, "load_corpus", lambda: rag.Corpus((), ()))
    app = app_test().run()
    assert not app.exception
    assert "Nenhuma fonte" in app.info[0].value
    app.button[0].click().run()
    assert "Informe uma pergunta" in app.warning[0].value
    app.text_area[0].set_value("quality orders").run()
    app.button[0].click().run()
    assert any("evid\u00eancia suficiente" in item.value for item in app.info)
    assert not app.exception


def test_local_answer_sources_excerpts_and_mode(monkeypatch, corpus):
    monkeypatch.setattr(page, "load_corpus", lambda: corpus)
    monkeypatch.setattr(rag.request, "urlopen", lambda *_args, **_kwargs: pytest.fail("Network forbidden"))
    app = app_test().run()
    app.text_area[0].set_value("quality orders").run()
    app.button[0].click().run()
    assert not app.exception
    assert "[S1]" in app.text[0].value
    assert "contracts/orders.yml" in app.expander[0].label
    assert "no_duplicate_primary_key" in app.code[0].value
    assert any("local | TF-IDF" in item.value for item in app.caption)
    assert any("Chamada externa: n\u00e3o realizada" in item.value for item in app.caption)
    assert any("SHA-256" in item.value for item in app.caption)
    assert any("Fontes aprovadas: 1" in item.value for item in app.caption)


def test_retrieved_metadata_is_plain_text_not_markdown(monkeypatch, corpus):
    untrusted = "![remote image](https://example.invalid/image)"
    chunk = replace(corpus.chunks[0], title=untrusted, owner=untrusted)
    monkeypatch.setattr(page, "load_corpus", lambda: rag.Corpus((chunk,), ()))
    app = app_test().run()
    app.text_area[0].set_value("quality orders").run()
    app.button[0].click().run()
    assert not app.exception
    assert any(untrusted in item.value for item in app.text)
    assert all(untrusted not in item.value for item in app.caption)
    assert all(untrusted not in item.value for item in app.markdown)


def test_no_evidence_rendering(monkeypatch, corpus):
    monkeypatch.setattr(page, "load_corpus", lambda: corpus)
    app = app_test().run()
    app.text_area[0].set_value("weather Mars").run()
    app.button[0].click().run()
    assert app.info[0].value == rag.NO_EVIDENCE
    assert not app.expander and not app.exception


@pytest.mark.parametrize("failure", [rag.RagError("Manifesto invalido"), RuntimeError("secret-value")])
def test_loading_error_rendering_is_safe(monkeypatch, failure):
    def fail():
        raise failure

    monkeypatch.setattr(page, "load_corpus", fail)
    app = app_test().run()
    assert app.error and not app.exception
    assert "secret-value" not in app.error[0].value


def test_source_notice_rendering(monkeypatch, corpus):
    monkeypatch.setattr(page, "load_corpus", lambda: rag.Corpus(corpus.chunks, ("Fonte alterada, excluida",)))
    app = app_test().run()
    assert app.warning[0].value == "Fonte alterada, excluida"


def test_external_consent_and_error_rendering(monkeypatch, corpus):
    monkeypatch.setattr(page, "load_corpus", lambda: corpus)
    app = app_test().run()
    app.text_area[0].set_value("quality orders").run()
    app.radio[0].set_value("openai").run()
    app.button[0].click().run()
    assert "autorizacao" in app.error[0].value

    def fail(*_args, **_kwargs):
        raise rag.RagError("Falha na integracao OpenAI. Use o modo local.")

    monkeypatch.setattr(page, "answer_question", fail)
    app.checkbox[0].check().run()
    app.button[0].click().run()
    assert "integracao OpenAI" in app.error[0].value
    assert not app.exception


def test_unexpected_answer_error_does_not_expose_details(monkeypatch, corpus):
    monkeypatch.setattr(page, "load_corpus", lambda: corpus)

    def fail(*_args, **_kwargs):
        raise RuntimeError("secret-value")

    monkeypatch.setattr(page, "answer_question", fail)
    app = app_test().run()
    app.text_area[0].set_value("quality orders").run()
    app.button[0].click().run()
    assert app.error and not app.exception
    assert "secret-value" not in app.error[0].value


def test_english_title(monkeypatch):
    monkeypatch.setattr(page, "load_corpus", lambda: rag.Corpus((), ()))
    app = AppTest.from_string(
        "from app.pages.governance_assistant import render_governance_assistant\n"
        "render_governance_assistant('en-US')"
    ).run()
    assert app.title[0].value == "Governance Assistant"
    assert not app.exception