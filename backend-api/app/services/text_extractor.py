from io import BytesIO
from pathlib import Path

from docx import Document
from pptx import Presentation
from pypdf import PdfReader


def extract_text_from_pdf(content: bytes) -> str:
    reader = PdfReader(BytesIO(content))
    pages: list[str] = []
    for page in reader.pages:
        pages.append(page.extract_text() or "")
    return "\n".join(pages).strip()


def extract_text_from_docx(content: bytes) -> str:
    document = Document(BytesIO(content))
    parts: list[str] = []
    for paragraph in document.paragraphs:
        if paragraph.text.strip():
            parts.append(paragraph.text)
    for table in document.tables:
        for row in table.rows:
            row_text = " | ".join(cell.text.strip() for cell in row.cells if cell.text.strip())
            if row_text:
                parts.append(row_text)
    return "\n".join(parts).strip()


def extract_text_from_pptx(content: bytes) -> str:
    prs = Presentation(BytesIO(content))
    parts: list[str] = []
    for slide in prs.slides:
        for shape in slide.shapes:
            if shape.has_text_frame:
                for paragraph in shape.text_frame.paragraphs:
                    text = paragraph.text.strip()
                    if text:
                        parts.append(text)
            if shape.has_table:
                for row in shape.table.rows:
                    row_text = " | ".join(cell.text.strip() for cell in row.cells if cell.text.strip())
                    if row_text:
                        parts.append(row_text)
    return "\n".join(parts).strip()


def extract_text_from_txt(content: bytes) -> str:
    for encoding in ["utf-8", "utf-16", "latin-1"]:
        try:
            return content.decode(encoding).strip()
        except (UnicodeDecodeError, ValueError):
            continue
    return content.decode("utf-8", errors="replace").strip()


def extract_text(content: bytes, path: str) -> str:
    ext = Path(path).suffix.lower()
    if ext == ".pdf":
        return extract_text_from_pdf(content)
    if ext == ".docx":
        return extract_text_from_docx(content)
    if ext == ".pptx":
        return extract_text_from_pptx(content)
    if ext in (".txt", ".rtf"):
        return extract_text_from_txt(content)
    if ext == ".doc":
        return extract_text_from_txt(content)
    raise ValueError(f"Unsupported file type: {ext}")
