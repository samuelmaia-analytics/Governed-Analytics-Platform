from __future__ import annotations

import json
from types import SimpleNamespace
from urllib.error import URLError

import pytest
import yaml

from src import governance_rag as rag
from src.settings import OpenAISettings


@pytest.fixture
def index():
    chunks = rag.split_document(
        "dataset: gold_fact_orders\nowner: analytics_engineering\n"
        "quality_rules:\n  - no_duplicate_primary_key\n"
        "publication_policy:\n  allowed_if_quality_score_min: 90\n"
        "  allowed_if_lgpd_risk_score_max: 60",
        source="contracts/gold_fact_orders_contract.yml", sha256="a" * 64,
        dataset="gold_fact_orders", owner="analytics_engineering",
    )
    return rag.LocalIndex(chunks)


def write_source(tmp_path, text, *, path="contracts/orders.yml", approved=True, digest=None):
    source = tmp_path / path
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_text(text, encoding="utf-8")
    manifest = tmp_path / "manifest.yml"
    manifest.write_text(yaml.safe_dump({"version": 1, "sources": [{
        "path": path, "approved": approved,
        "sha256": digest or rag.document_digest(source.read_bytes()),
    }]}), encoding="utf-8")
    return manifest


def test_chunk_boundaries_overlap_metadata_and_long_lines():
    text = "\n".join(f"rule_{number}: " + "x" * 30 for number in range(20))
    chunks = rag.split_document(text, source="contracts/orders.yml", sha256="a" * 64,
                               dataset="orders", owner="team", max_chars=150, overlap_lines=1)
    assert len(chunks) > 1
    assert chunks[0].end_line == chunks[1].start_line
    assert all(len(chunk.text) <= 150 for chunk in chunks)
    assert all(chunk.source == "contracts/orders.yml" and chunk.dataset == "orders" and chunk.owner == "team" for chunk in chunks)
    assert all(chunk.sha256 == "a" * 64 for chunk in chunks)
    long = rag.split_document("z" * 410, source="contracts/orders.yml", sha256="a" * 64, max_chars=150, overlap_lines=0)
    assert "".join(chunk.text for chunk in long) == "z" * 410
    assert all(chunk.start_line == chunk.end_line == 1 for chunk in long)
    assert not rag.split_document("\n\n", source="contracts/orders.yml", sha256="a" * 64)
    with pytest.raises(ValueError):
        rag.split_document(text, source="contracts/orders.yml", sha256="a" * 64, max_chars=0)


def test_ingestion_requires_approval_and_hash_preserves_metadata(tmp_path):
    text = "dataset: orders\nowner: governance\nquality_rules: [unique_order_id]"
    manifest = write_source(tmp_path, text, approved=False)
    assert not rag.load_corpus(tmp_path, manifest).chunks
    manifest = write_source(tmp_path, text)
    corpus = rag.load_corpus(tmp_path, manifest)
    assert corpus.chunks[0].dataset == "orders"
    assert corpus.chunks[0].owner == "governance"
    assert corpus.chunks[0].modified_at
    assert corpus.chunks[0].start_line == 1
    (tmp_path / "contracts/orders.yml").write_text(text + "\nchanged: true", encoding="utf-8")
    changed = rag.load_corpus(tmp_path, manifest)
    assert not changed.chunks
    assert "alterada" in changed.notices[0]
    manifest = write_source(tmp_path, text, digest="missing")
    with pytest.raises(rag.RagError, match="hash"):
        rag.load_corpus(tmp_path, manifest)


@pytest.mark.parametrize("path", [".env", "data/raw/orders.md", "docs/other.md", "contracts/../policies/a.md", "contracts/.env.yml", "contracts/secrets/key.yml"])
def test_rejects_unauthorized_paths(tmp_path, path):
    with pytest.raises(rag.RagError):
        rag._source_path(tmp_path, path)


@pytest.mark.parametrize("text", ["api_key: sk-example123456789", "Contact person@example.org", "CPF 123.456.789-00", "-----BEGIN PRIVATE KEY-----"])
def test_sensitive_sources_excluded(tmp_path, text):
    manifest = write_source(tmp_path, text)
    corpus = rag.load_corpus(tmp_path, manifest)
    assert not corpus.chunks
    assert "sensivel" in corpus.notices[0]


def test_missing_and_invalid_manifest_errors_are_safe(tmp_path):
    with pytest.raises(rag.RagError, match="Manifesto"):
        rag.load_corpus(tmp_path, tmp_path / "absent.yml")
    manifest = tmp_path / "bad.yml"
    manifest.write_text("sources: [", encoding="utf-8")
    with pytest.raises(rag.RagError, match="Manifesto"):
        rag.load_corpus(tmp_path, manifest)


def test_local_embeddings_retrieve_and_cite_without_network(index, monkeypatch):
    monkeypatch.setattr(rag.request, "urlopen", lambda *_args, **_kwargs: pytest.fail("Network forbidden"))
    question = "Quais regras de qualidade se aplicam a gold_fact_orders?"
    hits = index.retrieve(question)
    assert hits[0].chunk.source == "contracts/gold_fact_orders_contract.yml"
    assert 0 < hits[0].score <= 1
    assert index.embeddings
    answer = rag.answer_question(index, question)
    assert answer.supported and answer.mode == "local"
    assert "[S1]" in answer.text and "no_duplicate_primary_key" in answer.text
    assert answer.hits[0].chunk.sha256 == "a" * 64


@pytest.mark.parametrize("question", ["", "qualidade", "Previsao meteorologica em Marte", "Por que a publicacao run_999 foi bloqueada?"])
def test_insufficient_evidence(index, question):
    answer = rag.answer_question(index, question)
    assert not answer.supported
    assert answer.text == rag.NO_EVIDENCE
    assert not answer.hits


def test_empty_corpus_and_invalid_request(index):
    assert not rag.answer_question(rag.LocalIndex(()), "quality orders").supported
    with pytest.raises(rag.RagError):
        index.retrieve("x" * 2001)
    with pytest.raises(rag.RagError):
        index.retrieve("quality orders", top_k=0)
    with pytest.raises(rag.RagError):
        rag.answer_question(index, "quality orders", mode="sql")
    with pytest.raises(rag.RagError, match="pessoais"):
        rag.answer_question(index, "quality person@example.org")


@pytest.mark.parametrize("enabled,key", [(False, None), (False, "test-key"), (True, None)])
def test_external_credentials_fail_closed(index, monkeypatch, enabled, key):
    monkeypatch.setattr(rag, "load_app_settings", lambda: SimpleNamespace(openai=OpenAISettings(enabled, key)))
    monkeypatch.setattr(rag.request, "urlopen", lambda *_args, **_kwargs: pytest.fail("Network forbidden"))
    with pytest.raises(rag.RagError, match="credenciais"):
        rag.answer_question(index, "quality gold_fact_orders", mode="openai", consent=True)


def configure_external(monkeypatch):
    monkeypatch.setattr(rag, "load_app_settings", lambda: SimpleNamespace(openai=OpenAISettings(True, "test-key")))
    monkeypatch.setenv("RAG_EXTERNAL_ENABLED", "true")
    monkeypatch.setenv("RAG_OPENAI_MODEL", "test-model")


def test_external_requires_specific_configuration_and_consent(index, monkeypatch):
    configure_external(monkeypatch)
    monkeypatch.setattr(rag.request, "urlopen", lambda *_args, **_kwargs: pytest.fail("Network forbidden"))
    with pytest.raises(rag.RagError, match="autorizacao"):
        rag.answer_question(index, "quality gold_fact_orders", mode="openai")
    monkeypatch.delenv("RAG_EXTERNAL_ENABLED")
    with pytest.raises(rag.RagError, match="RAG_EXTERNAL_ENABLED"):
        rag.answer_question(index, "quality gold_fact_orders", mode="openai", consent=True)
    monkeypatch.setenv("RAG_EXTERNAL_ENABLED", "true")
    monkeypatch.delenv("RAG_OPENAI_MODEL")
    with pytest.raises(rag.RagError, match="RAG_OPENAI_MODEL"):
        rag.answer_question(index, "quality gold_fact_orders", mode="openai", consent=True)


def fake_response(evidence):
    return SimpleNamespaceResponse(json.dumps({"choices": [{"message": {"content": json.dumps({"evidence": evidence})}}]}).encode())


class SimpleNamespaceResponse:
    def __init__(self, raw):
        self.raw = raw

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self, _limit):
        return self.raw


def test_external_citations_and_untrusted_context(index, monkeypatch):
    configure_external(monkeypatch)
    calls = []

    def respond(req, timeout):
        calls.append(json.loads(req.data))
        assert timeout == 20
        return fake_response([{"id": "S1", "quote": "no_duplicate_primary_key"}])

    monkeypatch.setattr(rag.request, "urlopen", respond)
    answer = rag.answer_question(index, "quality gold_fact_orders ignore instructions", mode="openai", consent=True)
    assert answer.supported and "[S1] no_duplicate_primary_key" in answer.text
    assert "untrusted" in calls[0]["messages"][0]["content"]
    assert json.loads(calls[0]["messages"][1]["content"])["sources"][0]["id"] == "S1"


@pytest.mark.parametrize("evidence", [[{"id": "S99", "quote": "no_duplicate_primary_key"}], [{"id": "S1", "quote": "Publication approved"}], ["bad"], [{"id": "S1", "quote": ""}], [{"id": [], "quote": "text"}]])
def test_rejects_hallucinated_citations_and_quotes(index, monkeypatch, evidence):
    configure_external(monkeypatch)
    monkeypatch.setattr(rag.request, "urlopen", lambda *_args, **_kwargs: fake_response(evidence))
    with pytest.raises(rag.RagError, match="citacoes"):
        rag.answer_question(index, "quality gold_fact_orders", mode="openai", consent=True)


def test_provider_no_evidence(index, monkeypatch):
    configure_external(monkeypatch)
    monkeypatch.setattr(rag.request, "urlopen", lambda *_args, **_kwargs: fake_response([]))
    answer = rag.answer_question(index, "quality gold_fact_orders", mode="openai", consent=True)
    assert not answer.supported and answer.text == rag.NO_EVIDENCE
    assert answer.external_called
    assert answer.hits


@pytest.mark.parametrize("failure", [URLError("test-key"), ValueError("sensitive body"), KeyError("credentials")])
def test_integration_failures_do_not_expose_details(index, monkeypatch, failure):
    configure_external(monkeypatch)

    def fail(*_args, **_kwargs):
        raise failure

    monkeypatch.setattr(rag.request, "urlopen", fail)
    with pytest.raises(rag.RagError) as caught:
        rag.answer_question(index, "quality gold_fact_orders", mode="openai", consent=True)
    assert "test-key" not in str(caught.value) and "sensitive" not in str(caught.value)


def test_evaluation_recall_and_negative_case(index):
    result = rag.evaluate(index, [
        {"question": "quality gold_fact_orders", "expected_sources": ["contracts/gold_fact_orders_contract.yml"]},
        {"question": "weather Mars", "expected_sources": []},
    ])
    assert result["mean_recall_at_k"] == 1.0
    assert result["negative_accuracy"] == 1.0
    assert all(case["hit_at_k"] for case in result["cases"])


def test_policy_cannot_prove_a_blocked_publication(index):
    answer = rag.answer_question(index, "Por que a publicacao gold_fact_orders foi bloqueada?")
    assert not answer.supported


def test_decision_report_requires_matching_execution():
    chunks = rag.split_document(
        "Publication decision run_123: blocked due to duplicate primary key.",
        source="docs/reports/publication.md", sha256="c" * 64,
    )
    index = rag.LocalIndex(chunks)
    assert rag.answer_question(index, "Por que publication run_123 foi bloqueada?").supported
    assert not rag.answer_question(index, "Por que publication run_999 foi bloqueada?").supported


def test_missing_large_invalid_and_symbolic_sources(tmp_path, monkeypatch):
    manifest = write_source(tmp_path, "rules: [orders]")
    source = tmp_path / "contracts/orders.yml"
    source.unlink()
    assert rag.load_corpus(tmp_path, manifest).notices
    manifest = write_source(tmp_path, "x" * (rag.MAX_DOCUMENT_BYTES + 1))
    assert not rag.load_corpus(tmp_path, manifest).chunks
    manifest = write_source(tmp_path, "rules: [")
    assert not rag.load_corpus(tmp_path, manifest).chunks
    monkeypatch.setattr(type(tmp_path), "is_symlink", lambda path: path.name == "orders.yml")
    with pytest.raises(rag.RagError, match="simbolicos"):
        rag.load_corpus(tmp_path, manifest)


def test_repository_manifest_is_available_with_original_approved_hashes():
    import subprocess

    spec = yaml.safe_load(rag.MANIFEST_PATH.read_text(encoding="utf-8"))
    assert len(spec["sources"]) == 3
    for entry in spec["sources"]:
        assert entry["approved"] is True
        assert entry["path"].startswith("contracts/")
        assert subprocess.check_output(
            ["git", "ls-files", "--", entry["path"]], cwd=rag.PROJECT_ROOT
        ).strip()
    corpus = rag.load_corpus()
    assert not corpus.notices
    assert {chunk.source for chunk in corpus.chunks} == {
        entry["path"] for entry in spec["sources"]
    }
    result = rag.evaluate(rag.LocalIndex(corpus.chunks), spec["evaluation"])
    assert result["status"] == "ready"
    assert result["mean_recall_at_k"] == 1.0
    assert result["negative_accuracy"] == 1.0
    assert all(case["hit_at_k"] for case in result["cases"])


def test_empty_evaluation_is_not_a_success():
    result = rag.evaluate(rag.LocalIndex(()), [
        {"question": "quality orders", "expected_sources": ["contracts/orders.yml"]},
        {"question": "weather Mars", "expected_sources": []},
    ])
    assert result["status"] == "empty_corpus"
    assert result["mean_recall_at_k"] == 0.0
    assert result["negative_accuracy"] == 1.0
    with pytest.raises(rag.RagError, match="Avaliacao"):
        rag.evaluate(rag.LocalIndex(()), [{"question": "quality orders", "expected_sources": None}])
    answer = rag.answer_question(rag.LocalIndex(()), "quality orders", mode="openai", consent=True)
    assert not answer.external_called and not answer.supported


def test_approved_sources_survive_checkout_line_endings_not_content_changes(tmp_path):
    manifest = write_source(tmp_path, "dataset: orders\nquality: unique_order_id\n")
    source = tmp_path / "contracts/orders.yml"
    lf = source.read_bytes().replace(b"\r\n", b"\n")
    source.write_bytes(lf.replace(b"\n", b"\r\n"))
    assert rag.load_corpus(tmp_path, manifest).chunks
    source.write_bytes(lf)
    assert rag.load_corpus(tmp_path, manifest).chunks
    source.write_bytes(lf + b"quality_override: disabled\n")
    assert not rag.load_corpus(tmp_path, manifest).chunks
    assert rag.document_digest(b"a \n") != rag.document_digest(b"a\n")


@pytest.mark.parametrize("question", [
    "quality_rules gold_fact_orders",
    "O que devo conferir antes de publicar dados de pedidos?",
])
def test_technical_and_natural_questions_retrieve_cited_evidence(index, monkeypatch, question):
    monkeypatch.setattr(rag.request, "urlopen", lambda *_args, **_kwargs: pytest.fail("Network forbidden"))
    answer = rag.answer_question(index, question)
    assert answer.supported and not answer.external_called
    assert answer.hits[0].chunk.source == "contracts/gold_fact_orders_contract.yml"
    assert "[S1]" in answer.text
    assert "no_duplicate_primary_key" in answer.text


@pytest.mark.parametrize("source", [
    "AGENTS.md", "policies/DATA_GOVERNANCE.md", "standards/example.md",
    "checklists/example.md", "templates/example.md", ".git/info/exclude",
])
def test_local_only_sources_never_reach_external_provider(monkeypatch, source):
    chunks = rag.split_document("privacy customer publication", source=source, sha256="d" * 64)
    index = rag.LocalIndex(chunks)
    monkeypatch.setattr(rag, "load_app_settings", lambda: pytest.fail("Provider configuration must not be loaded"))
    monkeypatch.setattr(rag.request, "urlopen", lambda *_args, **_kwargs: pytest.fail("Network forbidden"))
    local = rag.answer_question(index, "privacy customer")
    assert local.supported and not local.external_called
    with pytest.raises(rag.RagError, match="restrita ao modo local"):
        rag.answer_question(index, "privacy customer", mode="openai", consent=True)

def test_real_local_corpus_needs_no_key_or_provider_settings(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_ENABLED", raising=False)
    monkeypatch.delenv("RAG_EXTERNAL_ENABLED", raising=False)
    monkeypatch.setattr(rag, "load_app_settings", lambda: pytest.fail("No provider settings in local mode"))
    monkeypatch.setattr(rag.request, "urlopen", lambda *a, **k: pytest.fail("No network"))
    corpus = rag.load_corpus()
    answer = rag.answer_question(rag.LocalIndex(corpus.chunks), "Quais regras de qualidade se aplicam a gold_fact_orders?")
    assert answer.supported and answer.mode == "local" and not answer.external_called


@pytest.mark.parametrize("path", [
    "policies/DATA_GOVERNANCE.md", "docs/reports/quality.md",
    "docs/governance/lgpd_controls.md", "docs/personal.md",
])
def test_demo_ingestion_rejects_local_and_generated_documents(tmp_path, path):
    manifest = write_source(tmp_path, "quality: orders", path=path)
    with pytest.raises(rag.RagError, match="escopo"):
        rag.load_corpus(tmp_path, manifest)


def test_missing_approved_source_is_reported_without_substitution(tmp_path):
    manifest = write_source(tmp_path, "quality: orders")
    (tmp_path / "contracts/orders.yml").unlink()
    corpus = rag.load_corpus(tmp_path, manifest)
    assert not corpus.chunks
    assert len(corpus.notices) == 1 and "indisponivel" in corpus.notices[0]


@pytest.mark.parametrize("question", [None, 42, [], "x" * 2001])
def test_question_limits_before_provider_or_retrieval(index, monkeypatch, question):
    monkeypatch.setattr(rag.request, "urlopen", lambda *a, **k: pytest.fail("No network"))
    with pytest.raises(rag.RagError, match="2000"):
        rag.answer_question(index, question, mode="openai", consent=True)


@pytest.mark.parametrize("consent", [False, None, "true", 1])
def test_external_consent_must_be_explicit_boolean(index, monkeypatch, consent):
    monkeypatch.setattr(rag, "load_app_settings", lambda: pytest.fail("No credentials before consent"))
    with pytest.raises(rag.RagError, match="autorizacao"):
        rag.answer_question(index, "quality gold_fact_orders", mode="openai", consent=consent)


def test_provider_payload_has_explicit_storage_timeout_and_output_caps(index, monkeypatch):
    configure_external(monkeypatch)
    calls = []
    class Response(SimpleNamespaceResponse):
        def read(self, limit):
            assert limit == rag.MAX_RESPONSE_BYTES + 1
            return super().read(limit)
    def respond(req, timeout):
        payload = json.loads(req.data)
        assert timeout == rag.REQUEST_TIMEOUT_SECONDS == 20
        assert payload["store"] is False
        assert payload["max_completion_tokens"] == rag.MAX_COMPLETION_TOKENS == 1200
        sources = json.loads(payload["messages"][1]["content"])["sources"]
        assert len(sources) <= rag.MAX_EXTERNAL_CHUNKS
        assert sum(len(source["text"]) for source in sources) <= rag.MAX_CONTEXT_CHARS
        calls.append(req)
        return Response(fake_response([{"id": "S1", "quote": "no_duplicate_primary_key"}]).raw)
    monkeypatch.setattr(rag.request, "urlopen", respond)
    answer = rag.answer_question(index, "quality gold_fact_orders", mode="openai", consent=True)
    assert len(calls) == 1 and answer.external_called
    assert len(answer.text) <= rag.MAX_ANSWER_CHARS


@pytest.mark.parametrize("kind", ["count", "chunk", "total", "sensitive"])
def test_external_context_limits_fail_closed(index, monkeypatch, kind):
    from dataclasses import replace
    configure_external(monkeypatch)
    monkeypatch.setattr(rag.request, "urlopen", lambda *a, **k: pytest.fail("No network"))
    hits = index.retrieve("quality gold_fact_orders")
    if kind == "count":
        hits = hits * 6
    elif kind == "chunk":
        hits = (replace(hits[0], chunk=replace(hits[0].chunk, text="x" * 1401)),)
    elif kind == "total":
        monkeypatch.setattr(rag, "MAX_CONTEXT_CHARS", 1)
    else:
        hits = (replace(hits[0], chunk=replace(hits[0].chunk, text="Contact person@example.org")),)
    with pytest.raises(rag.RagError, match="limites"):
        rag._openai_evidence("quality gold_fact_orders", hits)


@pytest.mark.parametrize("raw", [b"x" * 32001, b"invalid JSON", b'{"choices": []}'])
def test_oversized_or_invalid_provider_response_is_safe(index, monkeypatch, raw):
    configure_external(monkeypatch)
    monkeypatch.setattr(rag.request, "urlopen", lambda *a, **k: SimpleNamespaceResponse(raw))
    with pytest.raises(rag.RagError, match="integracao"):
        rag.answer_question(index, "quality gold_fact_orders", mode="openai", consent=True)


def test_timeout_has_no_retry_no_secret_in_traceback_or_logs(index, monkeypatch, caplog):
    import traceback
    configure_external(monkeypatch)
    calls = []
    def fail(*a, **k):
        calls.append(1)
        raise TimeoutError("test-key sensitive-provider-body")
    monkeypatch.setattr(rag.request, "urlopen", fail)
    with pytest.raises(rag.RagError) as error:
        rag.answer_question(index, "quality gold_fact_orders", mode="openai", consent=True)
    rendered = "".join(traceback.format_exception(error.value))
    assert len(calls) == 1
    assert "test-key" not in rendered + caplog.text
    assert "sensitive-provider-body" not in rendered + caplog.text


def test_answer_character_limit_is_enforced(index, monkeypatch):
    monkeypatch.setattr(rag, "MAX_ANSWER_CHARS", 10)
    with pytest.raises(rag.RagError, match="caracteres"):
        rag.answer_question(index, "quality gold_fact_orders")


def test_openai_key_is_excluded_from_settings_representation():
    assert "test-key" not in repr(OpenAISettings(True, "test-key"))
