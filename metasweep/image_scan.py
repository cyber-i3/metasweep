from pathlib import Path
from PIL import Image
from PIL.ExifTags import TAGS
import exifread
from .xmp_scan import find_xmp_in_file

def extract_exif_exifread(path: Path):
    try:
        with open(path, "rb") as fh:
            tags = exifread.process_file(fh, details=True)
        if not tags:
            return {}
        out = {}
        for k, v in tags.items():
            out[str(k)] = str(v)
        # note: exifread provides GPS tags and rational values as strings
        return out
    except Exception:
        return {}

def extract_exif_pillow(path: Path):
    try:
        img = Image.open(path)
        exif = img._getexif() or {}
        if not exif:
            return {}
        out = {}
        for tag, val in exif.items():
            name = TAGS.get(tag, tag)
            out[str(name)] = str(val)
        return out
    except Exception:
        return {}

def extract_png_text_chunks(path: Path):
    try:
        img = Image.open(path)
        info = img.info or {}
        return {k: str(v) for k, v in info.items() if v}
    except Exception:
        return {}

def image_deep_scan(path: Path):
    result = {}
    # EXIF via exifread (best)
    exif_r = extract_exif_exifread(path)
    exif_p = extract_exif_pillow(path)
    result["exif_exifread"] = exif_r or {}
    result["exif_pillow"] = exif_p or {}
    # XMP
    xmp = find_xmp_in_file(path)
    result["xmp"] = xmp if xmp else "Unknown"
    # PNG text
    if path.suffix.lower() == ".png":
        pngmeta = extract_png_text_chunks(path)
        result["png_text"] = pngmeta or {}
    # quick derived: GPSDecimal if tags present (do NOT fabricate if not)
    if "GPS GPSLatitude" in exif_r and "GPS GPSLongitude" in exif_r:
        result["gps_raw"] = {"lat": exif_r.get("GPS GPSLatitude"), "lon": exif_r.get("GPS GPSLongitude")}
    else:
        result["gps_raw"] = "Unknown"
    return result
