from __future__ import annotations

import dataclasses
import os
import subprocess
import sys
from pathlib import Path

import pytest

from src import governance_rag as rag


def test_public_api_imports_and_dataclass_schemas() -> None:
    from src.governance_rag import (  # noqa: PLC0415
        Answer,
        Chunk,
        Corpus,
        Hit,
        LocalIndex,
        RagError,
        answer_question,
        document_digest,
        load_corpus,
        split_document,
    )

    assert callable(split_document)
    assert callable(load_corpus)
    assert callable(document_digest)
    assert callable(answer_question)
    assert LocalIndex
    assert RagError

    assert dataclasses.is_dataclass(Chunk)
    assert [field.name for field in dataclasses.fields(Chunk)] == [
        "source",
        "title",
        "text",
        "start_line",
        "end_line",
        "sha256",
        "modified_at",
        "dataset",
        "owner",
    ]

    assert dataclasses.is_dataclass(Hit)
    assert [field.name for field in dataclasses.fields(Hit)] == [
        "citation",
        "chunk",
        "score",
    ]

    assert dataclasses.is_dataclass(Answer)
    assert [field.name for field in dataclasses.fields(Answer)] == [
        "text",
        "hits",
        "mode",
        "supported",
        "external_called",
    ]

    assert dataclasses.is_dataclass(Corpus)
    assert [field.name for field in dataclasses.fields(Corpus)] == [
        "chunks",
        "notices",
    ]

    chunk = Chunk(
        source="contracts/a.md",
        title="A",
        text="quality orders",
        start_line=1,
        end_line=1,
        sha256="a" * 64,
        modified_at="2026-01-01T00:00:00+00:00",
    )
    with pytest.raises(dataclasses.FrozenInstanceError):
        chunk.source = "contracts/b.md"  # type: ignore[misc]


def test_document_digest_normalizes_crlf_to_lf() -> None:
    lf = b"line1\nline2\n"
    crlf = b"line1\r\nline2\r\n"
    assert rag.document_digest(lf) == rag.document_digest(crlf)


def test_local_retrieve_is_deterministic_and_orders_ties_by_source_then_line() -> None:
    chunk_a_line_10 = rag.Chunk(
        source="contracts/a.md",
        title="A",
        text="quality orders",
        start_line=10,
        end_line=10,
        sha256="a" * 64,
        modified_at="2026-01-01T00:00:00+00:00",
    )
    chunk_a_line_1 = dataclasses.replace(chunk_a_line_10, start_line=1, end_line=1)
    chunk_b_line_1 = dataclasses.replace(chunk_a_line_10, source="contracts/b.md")

    index = rag.LocalIndex((chunk_a_line_10, chunk_b_line_1, chunk_a_line_1))
    hits = index.retrieve("quality orders", top_k=10)

    assert [(hit.chunk.source, hit.chunk.start_line) for hit in hits[:3]] == [
        ("contracts/a.md", 1),
        ("contracts/a.md", 10),
        ("contracts/b.md", 10),
    ]
    assert [hit.citation for hit in hits[:3]] == ["S1", "S2", "S3"]


def test_answer_question_rejects_sensitive_questions_without_network(monkeypatch) -> None:
    chunks = rag.split_document(
        "quality orders",
        source="contracts/a.md",
        sha256="a" * 64,
    )
    index = rag.LocalIndex(chunks)

    monkeypatch.setattr(
        rag.request,
        "urlopen",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            AssertionError("Network forbidden")
        ),
    )

    with pytest.raises(rag.RagError, match="credenciais|pessoais"):
        rag.answer_question(index, "api_key: sk-example123456789")


def test_cli_help_executes_without_external_calls() -> None:
    project_root = Path(__file__).resolve().parents[1]
    env = os.environ.copy()
    env.setdefault("OPENAI_API_KEY", "")
    env.setdefault("OPENAI_ENABLED", "")
    env.setdefault("RAG_EXTERNAL_ENABLED", "")

    proc = subprocess.run(
        [sys.executable, "-m", "src.governance_rag", "--help"],
        cwd=project_root,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert proc.returncode == 0
    assert "RAG" in (proc.stdout + proc.stderr)
