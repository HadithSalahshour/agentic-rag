import pathlib
from PyPDF2 import PdfReader

def load(path: str) -> dict:
    p = pathlib.Path(path)
    
    if p.suffix == ".pdf":
        text = ""
        reader = PdfReader(path)
        for page in reader.pages:
            text += page.extract_text() or ""
    else:
        text = p.read_text(encoding="utf-8")

    return {
        "source": str(p),
        "filename": p.name,
        "text": text.strip()
    }
