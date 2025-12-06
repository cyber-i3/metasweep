from pathlib import Path
from PyPDF2 import PdfReader
from .xmp_scan import find_xmp_in_file

def pdf_deep_scan(path: Path):
    raw = {}
    try:
        reader = PdfReader(str(path))
        info = reader.metadata or {}
        meta = {}
        if hasattr(info, "items"):
            for k, v in info.items():
                meta[str(k).lstrip("/")] = str(v) if v is not None else "Unknown"
        raw["pdf_info"] = meta if meta else "Unknown"
        # page count
        try:
            raw["page_count"] = len(reader.pages)
        except Exception:
            raw["page_count"] = "Unknown"
        # XMP
        xmp = find_xmp_in_file(path)
        raw["xmp"] = xmp if xmp else "Unknown"
        # raw bytes checks
        data = path.read_bytes()
        raw["contains_javascript"] = bool(b"/JavaScript" in data or b"/JS" in data)
        raw["contains_embedded_files"] = bool(b"/EmbeddedFiles" in data or b"/Filespec" in data)
    except Exception as e:
        raw["error"] = f"pdf parse error: {e}"
    return raw
