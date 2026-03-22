from __future__ import annotations

from pathlib import Path
import sys
from textwrap import wrap


PAGE_WIDTH = 595
PAGE_HEIGHT = 842
LEFT_MARGIN = 48
TOP_MARGIN = 48
BOTTOM_MARGIN = 48
LINE_HEIGHT = 14
FONT_SIZE = 10
MAX_CHARS_PER_LINE = 92


def escape_pdf_text(value: str) -> str:
    return value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def paginate_text(text: str) -> list[list[str]]:
    logical_lines: list[str] = []
    for raw_line in text.splitlines():
        if not raw_line.strip():
            logical_lines.append("")
            continue
        wrapped = wrap(raw_line, width=MAX_CHARS_PER_LINE, replace_whitespace=False, drop_whitespace=False)
        logical_lines.extend(wrapped if wrapped else [""])

    lines_per_page = max((PAGE_HEIGHT - TOP_MARGIN - BOTTOM_MARGIN) // LINE_HEIGHT, 1)
    return [logical_lines[i:i + lines_per_page] for i in range(0, len(logical_lines), lines_per_page)]


def build_page_stream(lines: list[str]) -> str:
    commands = ["BT", f"/F1 {FONT_SIZE} Tf", f"{LEFT_MARGIN} {PAGE_HEIGHT - TOP_MARGIN} Td"]
    first_line = True
    for line in lines:
        escaped = escape_pdf_text(line.rstrip())
        if first_line:
            commands.append(f"({escaped}) Tj")
            first_line = False
        else:
            commands.append(f"0 -{LINE_HEIGHT} Td")
            commands.append(f"({escaped}) Tj")
    commands.append("ET")
    return "\n".join(commands)


def write_pdf(input_path: Path, output_path: Path) -> None:
    text = input_path.read_text(encoding="utf-8")
    pages = paginate_text(text)

    objects: list[bytes] = []

    def add_object(content: str) -> int:
        objects.append(content.encode("latin-1", errors="replace"))
        return len(objects)

    font_id = add_object("<< /Type /Font /Subtype /Type1 /BaseFont /Courier >>")

    page_ids: list[int] = []
    content_ids: list[int] = []
    pages_placeholder_index = len(objects)
    objects.append(b"")

    for lines in pages:
        stream = build_page_stream(lines)
        content_id = add_object(f"<< /Length {len(stream.encode('latin-1', errors='replace'))} >>\nstream\n{stream}\nendstream")
        content_ids.append(content_id)
        page_id = add_object(
            f"<< /Type /Page /Parent {{PAGES_ID}} 0 R /MediaBox [0 0 {PAGE_WIDTH} {PAGE_HEIGHT}] /Resources << /Font << /F1 {font_id} 0 R >> >> /Contents {content_id} 0 R >>"
        )
        page_ids.append(page_id)

    kids = " ".join(f"{page_id} 0 R" for page_id in page_ids)
    pages_object = f"<< /Type /Pages /Kids [{kids}] /Count {len(page_ids)} >>"
    pages_id = pages_placeholder_index + 1
    objects[pages_placeholder_index] = pages_object.encode("latin-1")

    for idx, page_id in enumerate(page_ids, start=1):
        objects[page_id - 1] = objects[page_id - 1].replace(b"{PAGES_ID}", str(pages_id).encode("latin-1"))

    catalog_id = add_object(f"<< /Type /Catalog /Pages {pages_id} 0 R >>")

    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for index, obj in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf.extend(f"{index} 0 obj\n".encode("latin-1"))
        pdf.extend(obj)
        pdf.extend(b"\nendobj\n")

    xref_offset = len(pdf)
    pdf.extend(f"xref\n0 {len(objects) + 1}\n".encode("latin-1"))
    pdf.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode("latin-1"))
    pdf.extend(
        f"trailer\n<< /Size {len(objects) + 1} /Root {catalog_id} 0 R >>\nstartxref\n{xref_offset}\n%%EOF".encode(
            "latin-1"
        )
    )

    output_path.write_bytes(pdf)


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("Uso: python src/export_text_pdf.py <input_md_or_txt> <output_pdf>")

    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])
    write_pdf(input_path, output_path)


if __name__ == "__main__":
    main()
