from pathlib import Path
from .utils import compute_hashes, fs_timestamps
from .image_scan import image_deep_scan
from .pdf_scan import pdf_deep_scan
from .docx_scan import docx_deep_scan
from .xmp_scan import find_xmp_in_file
from .forensics import analyze
import mimetypes

def scan_path(path: Path, use_hachoir=False):
    path = path.resolve()
    report = {
        "file": str(path),
        "fs": fs_timestamps(path),
        "hashes": compute_hashes(path),
        "mime": None,
        "pdf": "Unknown",
        "docx": "Unknown",
        "image_exif": "Unknown",
        "png_text": "Unknown",
        "zip_container": "Unknown",
        "xmp": "Unknown",
        "hachoir": "Unknown"
    }
    # detect mime
    try:
        mtype, _ = mimetypes.guess_type(str(path))
        report["mime"] = mtype or None
    except Exception:
        report["mime"] = None

    ext = path.suffix.lower()
    # attempt XMP always
    xmp = find_xmp_in_file(path)
    report["xmp"] = xmp if xmp else "Unknown"

    # container listing
    try:
        from .docx_scan import extract_zip_container
    except Exception:
        extract_zip_container = None

    # docx:
    if ext == ".docx":
        report["docx"] = docx_deep_scan(path)
    elif ext == ".pdf":
        report["pdf"] = pdf_deep_scan(path)
    elif ext in (".jpg", ".jpeg", ".tiff", ".tif", ".png"):
        report["image_exif"] = image_deep_scan(path)
        if ext == ".png":
            report["png_text"] = report["image_exif"].get("png_text", "Unknown")
    else:
        # try to detect by mime
        if report["mime"] == "application/pdf":
            report["pdf"] = pdf_deep_scan(path)
        elif report["mime"] == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            report["docx"] = docx_deep_scan(path)
        elif report["mime"] and report["mime"].startswith("image/"):
            report["image_exif"] = image_deep_scan(path)

    # fallback hachoir extraction if installed
    if use_hachoir:
        try:
            from .utils import compute_hashes as _u
            from .image_scan import extract_hachoir as _dummy
        except Exception:
            pass

    # forensic analysis
    report["forensic_findings"] = analyze(report)
    return report
