from __future__ import annotations

from pathlib import Path

import pytest

import src.export_text_pdf as export_text_pdf


def test_escape_paginate_and_build_page_stream() -> None:
    escaped = export_text_pdf.escape_pdf_text(r"Text \(demo)")
    pages = export_text_pdf.paginate_text("Linha 1\n\n" + ("linha longa " * 30))
    stream = export_text_pdf.build_page_stream(["Linha 1", "Linha 2"])

    assert "\\(" in escaped
    assert pages
    assert stream.startswith("BT")
    assert stream.endswith("ET")


def test_write_pdf_and_main(tmp_path: Path, monkeypatch) -> None:
    input_path = tmp_path / "input.txt"
    output_path = tmp_path / "output.pdf"
    input_path.write_text("Conteudo de teste\n" * 5, encoding="utf-8")

    export_text_pdf.write_pdf(input_path, output_path)
    assert output_path.exists()
    assert output_path.read_bytes().startswith(b"%PDF-1.4")

    monkeypatch.setattr(
        export_text_pdf.sys,
        "argv",
        ["export_text_pdf.py", str(input_path), str(output_path)],
    )
    export_text_pdf.main()

    monkeypatch.setattr(export_text_pdf.sys, "argv", ["export_text_pdf.py"])
    with pytest.raises(SystemExit):
        export_text_pdf.main()
