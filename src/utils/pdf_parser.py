"""PDF parser: extract text from arXiv papers via PyPDF2, fallback to abstract."""

import io
import requests
from PyPDF2 import PdfReader


MAX_PAGES = 30
ARXIV_PDF_BASE = "https://arxiv.org/pdf/"


def download_pdf(url: str) -> bytes:
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return resp.content


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    reader = PdfReader(io.BytesIO(pdf_bytes))
    pages = reader.pages[:MAX_PAGES]
    text = ""
    for page in pages:
        t = page.extract_text()
        if t:
            text += t + "\n"
    return text.strip()


def extract_sections(text: str) -> dict[str, str]:
    section_keys = {
        "abstract": ["abstract"],
        "introduction": ["introduction"],
        "method": ["method", "methodology", "approach", "proposed method"],
        "results": ["results", "experiments", "evaluation", "findings"],
        "conclusion": ["conclusion", "conclusions", "discussion"],
    }
    lower = text.lower()
    sections = {}
    for key, markers in section_keys.items():
        start = -1
        for marker in markers:
            idx = lower.find(f"{marker}")
            if idx != -1:
                start = idx
                break
        if start == -1:
            continue
        end = len(text)
        for other_key, other_markers in section_keys.items():
            if other_key == key:
                continue
            for om in other_markers:
                idx = lower.find(om, start + 20)
                if idx != -1 and idx < end:
                    end = idx
        sections[key] = text[start:end].strip()[:3000]
    return sections


def fetch_and_parse_pdf(arxiv_id: str, abstract: str = "") -> tuple[str, dict[str, str]]:
    pdf_url = f"{ARXIV_PDF_BASE}{arxiv_id}.pdf"
    try:
        pdf_bytes = download_pdf(pdf_url)
        text = extract_text_from_pdf(pdf_bytes)
        if not text or len(text) < 100:
            return abstract, extract_sections(abstract)
        return text, extract_sections(text)
    except Exception:
        return abstract, extract_sections(abstract)
