import pytest
from pathlib import Path
import tempfile
from metasweep.core import scan_path


class TestScanPath:
    def test_scan_path_returns_dict(self):
        """Test that scan_path returns a dictionary with required keys."""
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            f.write(b"test content")
            f.flush()
            path = Path(f.name)
        
        report = scan_path(path)
        assert isinstance(report, dict)
        assert "file" in report
        assert "hashes" in report
        assert "fs" in report
        assert "mime" in report
        assert "forensic_findings" in report
        path.unlink()

    def test_scan_path_includes_hashes(self):
        """Test that report includes file hashes."""
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            f.write(b"test")
            f.flush()
            path = Path(f.name)
        
        report = scan_path(path)
        assert "md5" in report["hashes"]
        assert "sha256" in report["hashes"]
        assert len(report["hashes"]["md5"]) == 32
        assert len(report["hashes"]["sha256"]) == 64
        path.unlink()

    def test_scan_path_includes_timestamps(self):
        """Test that report includes filesystem timestamps."""
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            f.write(b"test")
            f.flush()
            path = Path(f.name)
        
        report = scan_path(path)
        assert "created_at" in report["fs"]
        assert "modified_at" in report["fs"]
        assert "+" in report["fs"]["created_at"]
        path.unlink()

    def test_scan_path_detects_mime_type(self):
        """Test that scan_path detects MIME type."""
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            f.write(b"test")
            f.flush()
            path = Path(f.name)
        
        report = scan_path(path)
        assert report["mime"] is not None
        path.unlink()
