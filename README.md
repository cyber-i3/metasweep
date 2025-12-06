# MetaSweep — Forensic Metadata Analyzer

A Python-based forensic analysis tool that extracts, analyzes, and reports on hidden metadata embedded in digital files. Perfect for OSINT investigations, incident response, and digital forensics.

**Supports:** JPG/JPEG, PNG, TIFF, PDF, DOCX, and XMP metadata

## Features

- 🔍 **Deep Metadata Extraction** — EXIF, XMP, PDF properties, DOCX document info
- 🗂️ **Multi-Format Support** — Images (JPG, PNG, TIFF), PDFs, Word documents
- 📊 **HTML Reports** — Beautiful, forensic-grade HTML reports with summaries
- 🔐 **Hash Verification** — MD5 and SHA256 checksums for file integrity
- ⏰ **Timestamp Analysis** — Filesystem vs. embedded metadata comparison
- 🗺️ **GPS Detection** — Identifies and reports location data in images
- 📝 **JSON Export** — Machine-readable output for automation
- ⚠️ **Forensic Flags** — Automated detection of suspicious patterns

## Installation

### Requirements
- Python 3.8+
- pip

### Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/metasweep.git
cd metasweep

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Quick Start

### Basic Scan
```bash
python -m metasweep.cli path/to/file.jpg
```

Generates:
- **JSON Report**: `reports/file_<timestamp>.json`
- **HTML Report**: `reports/file_<timestamp>.html`

### With Options
```bash
python -m metasweep.cli path/to/file.pdf --template report_template.html --outdir ./my_reports
python -m metasweep.cli path/to/file.docx --hachoir
```

## CLI Options

```
usage: python -m metasweep.cli [-h] [--template TEMPLATE] [--outdir OUTDIR] [--hachoir] target

positional arguments:
  target                File to scan

optional arguments:
  -h, --help            show this help message and exit
  --template TEMPLATE   HTML template path (default: report_template.html)
  --outdir OUTDIR       Output directory for JSON and HTML (default: reports)
  --hachoir             Enable hachoir fallback if installed
```

## Module Overview

| Module | Purpose |
|--------|---------|
| `core.py` | Main orchestrator, routes files to scanners |
| `pdf_scan.py` | PDF metadata extraction |
| `docx_scan.py` | DOCX document analysis |
| `image_scan.py` | Image EXIF and metadata |
| `xmp_scan.py` | XMP metadata extraction |
| `forensics.py` | Forensic analysis and flags |
| `utils.py` | Hashing, timestamps, report generation |

## Forensic Indicators

Detects:
- **Stripped Metadata** — Image with no EXIF data
- **Timestamp Mismatches** — Filesystem vs. embedded metadata (>1 day)
- **Embedded Objects** — PDFs with embedded files/JavaScript
- **Macros** — DOCX files with VBA projects
- **GPS Data** — Location coordinates in images
- **Document History** — Revision counts and modification patterns

## Use Cases

| Use Case | Description |
|----------|-------------|
| **OSINT** | Find location, author, and timestamps in leaked documents |
| **Incident Response** | Detect file modifications, embedded payloads, tampering |
| **Digital Forensics** | Establish file provenance and integrity |
| **Security Research** | Analyze malware samples for embedded files |

## Output

### HTML Report
- Executive summary with forensic flags
- Key findings table
- Raw JSON data
- Professional styling

### JSON Report
Complete machine-readable output with all extracted metadata.

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| PyPDF2 | 3.0.1 | PDF parsing |
| python-docx | 0.8.11 | DOCX analysis |
| Pillow | 9.5.0 | Image processing |
| exifread | 3.5.1 | EXIF extraction |
| python-magic | 0.4.27 | MIME type detection |
| lxml | 4.9.3 | XML parsing |
| tabulate | 0.9.0 | Table formatting |
| geopy | 2.4.0 | GPS reverse geocoding (optional) |
| hachoir | 3.1.1 | Deep metadata (optional) |

## Testing

```bash
python -m pytest tests/
```

## Contributing

Fork → Feature branch → Add tests → Pull request

## License

MIT License — see `LICENSE` file

## Author

Created by **i3** for digital forensics professionals, security researchers, and OSINT investigators.

## Disclaimer

Use responsibly. Respect privacy laws. For authorized forensic analysis, OSINT research, and educational purposes only.
