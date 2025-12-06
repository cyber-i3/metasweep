import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
import os

def now_ts():
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

def compute_hashes(path: Path):
    h_md5 = hashlib.md5()
    h_sha256 = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(8192), b""):
            h_md5.update(chunk)
            h_sha256.update(chunk)
    return {"md5": h_md5.hexdigest(), "sha256": h_sha256.hexdigest()}

def fs_timestamps(path: Path):
    st = path.stat()
    return {
        "created_at": datetime.fromtimestamp(st.st_ctime, tz=timezone.utc).isoformat(),
        "modified_at": datetime.fromtimestamp(st.st_mtime, tz=timezone.utc).isoformat()
    }

def save_json(report: dict, out_dir: Path, base_name: str):
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = now_ts()
    file_name = f"{base_name}_{ts}.json"
    path = out_dir / file_name
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=2)
    return path

def render_html(template_path: Path, out_path: Path, replacements: dict):
    tpl = template_path.read_text(encoding="utf-8")
    for k, v in replacements.items():
        tpl = tpl.replace(k, v)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(tpl, encoding="utf-8")
    return out_path
