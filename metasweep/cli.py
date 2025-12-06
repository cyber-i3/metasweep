#!/usr/bin/env python3
"""
MetaSweep CLI - Forensic Metadata Analyzer
Author: i3
License: MIT
"""
import argparse
from pathlib import Path
from .core import scan_path
from .utils import save_json, render_html
from importlib import resources
import json
import os

PACKAGE_DIR = Path(__file__).resolve().parent.parent
TEMPLATE = PACKAGE_DIR / "report_template.html"  # we will pass the repo-level template path from top-level

def generate_html_from_report(report, template_path: Path, out_html: Path):
    # key fields table: file, mime, md5, sha256, created, modified, summary items
    key_fields = [
        ("File", report.get("file", "Unknown")),
        ("MIME", report.get("mime", "Unknown")),
        ("MD5", report.get("hashes", {}).get("md5", "Unknown")),
        ("SHA256", report.get("hashes", {}).get("sha256", "Unknown")),
        ("Created", report.get("fs", {}).get("created_at", "Unknown")),
        ("Modified", report.get("fs", {}).get("modified_at", "Unknown")),
    ]
    # build table rows html
    rows = []
    for k, v in key_fields:
        rows.append(f"<tr><td>{k}</td><td>{v}</td></tr>")
    table_html = "\n".join(rows)
    exec_summary = " ; ".join(report.get("forensic_findings", [])[:3]) if report.get("forensic_findings") else "No summary available"
    forensic_text = "\n".join(report.get("forensic_findings", []))
    replacements = {
        "{{FILENAME}}": Path(report.get("file", "")).name,
        "{{TIMESTAMP}}": report.get("fs", {}).get("modified_at", ""),
        "{{EXECUTIVE_SUMMARY}}": exec_summary,
        "{{KEY_FIELDS_TABLE}}": table_html,
        "{{FORENSIC_TEXT}}": forensic_text,
        "{{RAW_JSON}}": json.dumps(report, indent=2)
    }
    render_html(template_path, out_html, replacements)

def main():
    parser = argparse.ArgumentParser(description="MetaSweep Pro - forensic metadata extractor")
    parser.add_argument("target", help="File to scan")
    parser.add_argument("--template", default="report_template.html", help="HTML template path (default: report_template.html)")
    parser.add_argument("--outdir", default="reports", help="Output directory for JSON and HTML")
    parser.add_argument("--hachoir", action="store_true", help="Enable hachoir fallback if installed")
    args = parser.parse_args()

    target = Path(args.target)
    if not target.exists() or not target.is_file():
        print("Target not found or not a file:", target)
        return

    report = scan_path(target, use_hachoir=args.hachoir)
    outdir = Path(args.outdir)
    json_path = save_json(report, outdir, target.stem)
    html_path = outdir / (target.stem + "_" + report["fs"]["modified_at"].replace(":", "").replace("+", "").replace("-", "") + ".html")
    # template can be repo-root file (passed by user) or default
    template_path = Path(args.template) if Path(args.template).exists() else Path("report_template.html")
    # generate HTML
    generate_html_from_report(report, template_path, html_path)
    print("Saved JSON ->", json_path)
    print("Saved HTML ->", html_path)

if __name__ == "__main__":
    main()
