import pytest
from pathlib import Path
import tempfile
from metasweep.forensics import analyze, timestamp_mismatch_check


class TestAnalyze:
    def test_analyze_returns_list(self):
        """Test that analyze returns a list."""
        report = {
            "file": "/test.jpg",
            "fs": {"created_at": "2025-01-01T00:00:00+00:00", "modified_at": "2025-01-01T00:00:00+00:00"},
            "hashes": {"md5": "abc", "sha256": "def"},
            "image_exif": "Unknown"
        }
        findings = analyze(report)
        assert isinstance(findings, list)
        assert len(findings) > 0

    def test_analyze_detects_stripped_metadata(self):
        """Test that analyze detects stripped EXIF metadata."""
        report = {
            "file": "/test.jpg",
            "fs": {"created_at": "2025-01-01T00:00:00+00:00", "modified_at": "2025-01-01T00:00:00+00:00"},
            "image_exif": "Unknown"
        }
        findings = analyze(report)
        assert any("EXIF" in f or "stripped" in f.lower() for f in findings)

    def test_analyze_pdf_with_javascript(self):
        """Test that analyze detects PDF JavaScript."""
        report = {
            "file": "/test.pdf",
            "fs": {"created_at": "2025-01-01T00:00:00+00:00", "modified_at": "2025-01-01T00:00:00+00:00"},
            "pdf": {"contains_javascript": True, "page_count": 5},
            "image_exif": "Unknown"
        }
        findings = analyze(report)
        assert any("JavaScript" in f for f in findings)

    def test_analyze_docx_with_macros(self):
        """Test that analyze detects DOCX macros."""
        report = {
            "file": "/test.docx",
            "fs": {"created_at": "2025-01-01T00:00:00+00:00", "modified_at": "2025-01-01T00:00:00+00:00"},
            "docx": {"has_macros": True},
            "image_exif": "Unknown"
        }
        findings = analyze(report)
        assert any("macro" in f.lower() for f in findings)

    def test_analyze_default_message(self):
        """Test that analyze returns a message when no special findings."""
        report = {
            "file": "/test.txt",
            "fs": {"created_at": "2025-01-01T00:00:00+00:00", "modified_at": "2025-01-01T00:00:00+00:00"},
            "pdf": "Unknown",
            "docx": "Unknown"
        }
        findings = analyze(report)
        assert len(findings) > 0
        assert "No obvious forensic flags" in findings[0]


class TestTimestampMismatchCheck:
    def test_timestamp_mismatch_returns_list(self):
        """Test that timestamp_mismatch_check returns a list."""
        fs = {"created_at": "2025-01-01T00:00:00+00:00", "modified_at": "2025-01-01T00:00:00+00:00"}
        doc_meta = {"core_created": "2025-01-01T00:00:00+00:00"}
        findings = timestamp_mismatch_check(fs, doc_meta)
        assert isinstance(findings, list)

    def test_timestamp_mismatch_detects_difference(self):
        """Test that timestamp_mismatch_check detects large differences."""
        fs = {"created_at": "2025-01-01T00:00:00+00:00", "modified_at": "2025-01-01T00:00:00+00:00"}
        # 2 days difference
        doc_meta = {"core_created": "2025-01-03T00:00:00+00:00"}
        findings = timestamp_mismatch_check(fs, doc_meta)
        assert len(findings) > 0
        assert "Creation timestamp" in findings[0] or "differ" in findings[0].lower()

    def test_timestamp_mismatch_ignores_small_difference(self):
        """Test that small timestamp differences are ignored."""
        fs = {"created_at": "2025-01-01T00:00:00+00:00", "modified_at": "2025-01-01T00:00:00+00:00"}
        doc_meta = {"core_created": "2025-01-01T00:00:01+00:00"}  # 1 second difference
        findings = timestamp_mismatch_check(fs, doc_meta)
        # Should not flag small differences
        assert len(findings) == 0
