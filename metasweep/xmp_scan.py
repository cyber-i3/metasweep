from pathlib import Path
import re
from lxml import etree

XMP_START = b"<x:xmpmeta"
XMP_END = b"</x:xmpmeta>"

def extract_xmp_from_bytes(data: bytes):
    idx = data.find(XMP_START)
    if idx == -1:
        return None
    end = data.find(XMP_END, idx)
    if end == -1:
        return None
    end += len(XMP_END)
    xml = data[idx:end]
    try:
        parser = etree.XMLParser(recover=True)
        root = etree.fromstring(xml, parser=parser)
        # return pretty/XML string
        return etree.tostring(root, encoding="utf-8", pretty_print=True).decode("utf-8", errors="ignore")
    except Exception:
        try:
            return xml.decode("utf-8", errors="ignore")
        except Exception:
            return None

def find_xmp_in_file(path: Path):
    try:
        data = path.read_bytes()
        return extract_xmp_from_bytes(data)
    except Exception:
        return None
