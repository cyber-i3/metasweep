from pathlib import Path
import zipfile
import re

def docx_deep_scan(path: Path):
    raw = {}
    try:
        with zipfile.ZipFile(str(path), "r") as z:
            namelist = z.namelist()
            raw["zip_members"] = namelist
            # read core.xml if present
            if "docProps/core.xml" in namelist:
                core_xml = z.read("docProps/core.xml")
                def find_tag(xml, tag):
                    m = re.search(rb"<(?:[^:>]+:)?"+re.escape(tag.encode())+rb"[^>]*>(.*?)</(?:[^:>]+:)?"+re.escape(tag.encode())+rb">", xml, flags=re.DOTALL)
                    return m.group(1).decode("utf-8", errors="ignore").strip() if m else "Unknown"
                raw["core_author"] = find_tag(core_xml, "creator")
                raw["core_lastModifiedBy"] = find_tag(core_xml, "lastModifiedBy")
                raw["core_created"] = find_tag(core_xml, "created")
                raw["core_modified"] = find_tag(core_xml, "modified")
                raw["core_revision"] = find_tag(core_xml, "revision")
            else:
                raw["core_props"] = "Unknown"
            # app.xml
            if "docProps/app.xml" in namelist:
                app_xml = z.read("docProps/app.xml")
                def find_tag(xml, tag):
                    m = re.search(rb"<(?:[^:>]+:)?"+re.escape(tag.encode())+rb"[^>]*>(.*?)</(?:[^:>]+:)?"+re.escape(tag.encode())+rb">", xml, flags=re.DOTALL)
                    return m.group(1).decode("utf-8", errors="ignore").strip() if m else "Unknown"
                raw["app_application"] = find_tag(app_xml, "Application")
                raw["app_totalTime"] = find_tag(app_xml, "TotalTime")
            else:
                raw["app_props"] = "Unknown"
            raw["has_macros"] = any("vbaProject.bin" in n for n in namelist)
    except zipfile.BadZipFile:
        raw["error"] = "Not a valid DOCX/ZIP"
    except Exception as e:
        raw["error"] = f"docx parse error: {e}"
    return raw
