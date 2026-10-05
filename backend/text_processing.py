"""Conservative text handling: never guess missing mathematical operators."""
import re
import unicodedata

# Legacy Symbol font codes observed in course PDFs. Only apply to that font.
SYMBOL_OPERATORS = str.maketrans({"È": "∪", "Ç": "∩", "Î": "∈", "Ï": "∉", "Æ": "∅"})


def repair_symbol_text(text: str, font: dict | None) -> str:
    if font and "symbol" in str(font.get("/BaseFont", "")).lower():
        return text.translate(SYMBOL_OPERATORS)
    return text


def extract_page_text(page) -> str:
    fragments = []

    def collect(text, cm, tm, font, size):
        fragments.append(repair_symbol_text(text, font))

    page.extract_text(visitor_text=collect)
    return clean_text("".join(fragments))


def clean_text(text: str) -> str:
    # NFC preserves operators, accents and superscripts, unlike compatibility folding.
    text = unicodedata.normalize("NFC", text).replace("\u00a0", " ")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[^\S\n]+", " ", text)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def chunk_text(text: str, source: str, page: int | None = None,
               chunk_size: int = 250, overlap: int = 40) -> list[dict]:
    if not 0 <= overlap < chunk_size:
        raise ValueError("Overlap must be smaller than chunk size")
    text = clean_text(text)
    words = list(re.finditer(r"\S+", text))
    chunks = []
    for start in range(0, len(words), chunk_size - overlap):
        end = min(start + chunk_size, len(words))
        chunks.append({"source": source, "page": page,
                       "text": text[words[start].start():words[end - 1].end()]})
        if end == len(words):
            break
    return chunks
