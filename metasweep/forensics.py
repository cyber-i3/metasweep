from .utils import fs_timestamps
from datetime import datetime, timezone

def timestamp_mismatch_check(fs: dict, doc_meta: dict):
    """
    fs: filesystem timestamps dict
    doc_meta: dict with possible 'created' 'modified' keys (ISO strings or Unknown)
    returns: list of findings
    """
    findings = []
    try:
        fs_created = fs.get("created_at")
        fs_modified = fs.get("modified_at")
        # only compare if doc_meta has valid strings
        doc_created = doc_meta.get("core_created") if doc_meta else None
        doc_modified = doc_meta.get("core_modified") if doc_meta else None
        # compare presence/absence
        if doc_created and doc_created != "Unknown":
            # attempt parsing few formats robustly
            try:
                d_created = datetime.fromisoformat(doc_created.replace("Z", "+00:00"))
                # parse fs_created
                f_created = datetime.fromisoformat(fs_created)
                if abs((d_created - f_created).total_seconds()) > 24*3600:  # >1 day diff
                    findings.append("Creation timestamp differs between file metadata and filesystem (possible copy or modification).")
            except Exception:
                pass
        if doc_modified and doc_modified != "Unknown":
            try:
                d_mod = datetime.fromisoformat(doc_modified.replace("Z", "+00:00"))
                f_mod = datetime.fromisoformat(fs_modified)
                if abs((d_mod - f_mod).total_seconds()) > 24*3600:
                    findings.append("Modification timestamp differs between document metadata and filesystem (possible edits or metadata changed).")
            except Exception:
                pass
    except Exception:
        pass
    return findings

def analyze(report: dict):
    findings = []
    # If no metadata in image & no exif -> indicate stripped or never present
    if report.get("image_exif") and report["image_exif"] == "Unknown":
        findings.append("Image contains no EXIF metadata (common if stripped or exported by some apps).")
    # PDF checks
    if report.get("pdf") and report["pdf"] != "Unknown":
        pdf = report["pdf"]
        if isinstance(pdf, dict):
            if pdf.get("contains_javascript"):
                findings.append("PDF contains JavaScript objects (may be used for forms or malicious scripts).")
            if pdf.get("contains_embedded_files"):
                findings.append("PDF contains embedded files/attachments.")
            # producer check
            producer = pdf.get("pdf_info", {}).get("Producer")
            if producer:
                findings.append(f"PDF Producer: {producer}")
    # DOCX checks
    if report.get("docx") and report["docx"] != "Unknown":
        doc = report["docx"]
        if isinstance(doc, dict):
            if doc.get("has_macros"):
                findings.append("DOCX contains macros (vbaProject.bin) — examine macros carefully.")
            # timestamp mismatch
            fs = report.get("fs", {})
            tfind = timestamp_mismatch_check(fs, doc)
            findings.extend(tfind)
    # GPS checks
    if report.get("image_exif") and isinstance(report["image_exif"], dict):
        gps = report["image_exif"].get("gps_raw")
        if gps and gps != "Unknown":
            findings.append("Image contains GPS coordinates (raw present).")
    # Hachoir fallback
    if report.get("hachoir") and report["hachoir"] != "Unknown":
        findings.append("Additional metadata available via hachoir (see JSON).")
    # If no findings, state low info
    if not findings:
        findings.append("No obvious forensic flags detected based on available metadata.")
    return findings
