import io
import re
from typing import Tuple
import fitz  # PyMuPDF
from docx import Document as DocxDocument
from bs4 import BeautifulSoup
from striprtf.striprtf import rtf_to_text
import markdown as md

def _clean_text(text: str) -> str:
    text = text.replace("\x00", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text

def parse_pdf(file_bytes: bytes) -> str:
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    parts = []
    for page in doc:
        parts.append(page.get_text("text"))
    return _clean_text("\n".join(parts))

def parse_docx(file_bytes: bytes) -> str:
    f = io.BytesIO(file_bytes)
    doc = DocxDocument(f)
    parts = [p.text for p in doc.paragraphs]
    return _clean_text("\n".join(parts))

def parse_txt(file_bytes: bytes) -> str:
    return _clean_text(file_bytes.decode("utf-8", errors="ignore"))

def parse_html(file_bytes: bytes) -> str:
    html = file_bytes.decode("utf-8", errors="ignore")
    soup = BeautifulSoup(html, "lxml")
    return _clean_text(soup.get_text(separator="\n"))

def parse_xml(file_bytes: bytes) -> str:
    xml = file_bytes.decode("utf-8", errors="ignore")
    soup = BeautifulSoup(xml, "lxml-xml")
    return _clean_text(soup.get_text(separator="\n"))

def parse_md(file_bytes: bytes) -> str:
    raw = file_bytes.decode("utf-8", errors="ignore")
    html = md.markdown(raw)
    soup = BeautifulSoup(html, "lxml")
    return _clean_text(soup.get_text(separator="\n"))

def parse_rtf(file_bytes: bytes) -> str:
    raw = file_bytes.decode("utf-8", errors="ignore")
    return _clean_text(rtf_to_text(raw))

def parse_by_extension(filename: str, file_bytes: bytes) -> Tuple[str, str]:
    ext = filename.split(".")[-1].lower()
    if ext == "pdf":
        return "pdf", parse_pdf(file_bytes)
    if ext == "docx":
        return "docx", parse_docx(file_bytes)
    if ext == "txt":
        return "txt", parse_txt(file_bytes)
    if ext in ("html", "htm"):
        return "html", parse_html(file_bytes)
    if ext == "xml":
        return "xml", parse_xml(file_bytes)
    if ext == "md":
        return "md", parse_md(file_bytes)
    if ext == "rtf":
        return "rtf", parse_rtf(file_bytes)
    raise ValueError(f"Unsupported file type: .{ext}")
