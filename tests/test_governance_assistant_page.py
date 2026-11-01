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

def test_consent_is_consumed_and_never_reused_for_the_next_query(monkeypatch, corpus):
    monkeypatch.setattr(page, "load_corpus", lambda: corpus)
    calls = []
    def answer(index, question, *, mode, consent):
        calls.append((mode, consent))
        return rag.answer_question(index, question, mode="local")
    monkeypatch.setattr(page, "answer_question", answer)
    app = app_test().run()
    assert app.radio[0].value == "local"
    app.text_area[0].set_value("quality orders")
    app.radio[0].set_value("openai")
    app.checkbox[0].check()
    app.button[0].click().run()
    assert not app.exception
    assert calls[-1] == ("openai", True)
    assert app.checkbox[0].value is False
    app.text_area[0].set_value("quality orders again")
    app.radio[0].set_value("openai")
    app.button[0].click().run()
    assert calls[-1] == ("openai", False)
    assert app.checkbox[0].value is False
    assert "_rag_query_consent" not in app.session_state


@pytest.mark.parametrize("flag", [True, False, "true", "false", "invalid", 1])
def test_real_streamlit_secrets_flags_control_consented_queries(
    monkeypatch, corpus, tmp_path, flag
):
    import json
    import os

    from streamlit.runtime.secrets import Secrets

    monkeypatch.setattr(page, "load_corpus", lambda: corpus)
    # Use the pinned Streamlit parser/export implementation, never real secrets.
    for name in ("OPENAI_ENABLED", "RAG_EXTERNAL_ENABLED", "OPENAI_API_KEY", "RAG_OPENAI_MODEL"):
        monkeypatch.setenv(name, "")
    secret_path = tmp_path / "secrets.toml"
    literal = str(flag).lower() if type(flag) in {bool, int} else json.dumps(flag)
    secret_path.write_text(
        f"OPENAI_ENABLED = {literal}\nRAG_EXTERNAL_ENABLED = {literal}\n"
        'OPENAI_API_KEY = "test-key"\nRAG_OPENAI_MODEL = "test-model"\n',
        encoding="utf-8",
    )
    original_get_option = page.st.config.get_option
    monkeypatch.setattr(
        page.st.config, "get_option",
        lambda name: [str(secret_path)] if name == "secrets.files" else original_get_option(name),
    )
    secrets = Secrets()
    monkeypatch.setattr(Secrets, "_maybe_install_file_watchers", lambda self: None)
    monkeypatch.setattr(page.st, "secrets", secrets)
    calls = []

    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self, limit):
            return json.dumps({"choices": [{"message": {"content": json.dumps({
                "evidence": [{"id": "S1", "quote": "no_duplicate_primary_key"}]
            })}}]}).encode()

    def respond(req, timeout):
        calls.append(1)
        return Response()

    monkeypatch.setattr(rag.request, "urlopen", respond)
    app = app_test().run()
    assert not calls and secrets._secrets is None
    app.text_area[0].set_value("quality orders")
    app.radio[0].set_value("openai")
    app.checkbox[0].check()
    app.button[0].click().run()
    assert not app.exception
    if flag is True or flag == "true":
        assert calls == [1]
        assert os.environ["OPENAI_ENABLED"] == "true"
        assert os.environ["RAG_EXTERNAL_ENABLED"] == "true"
        assert any("realizada" in item.value for item in app.caption)
    else:
        assert not calls and app.error
        if flag is False or flag == "false":
            assert os.environ["OPENAI_ENABLED"] == "false"
            assert os.environ["RAG_EXTERNAL_ENABLED"] == "false"
    assert app.checkbox[0].value is False
    assert "test-key" not in str(app)
