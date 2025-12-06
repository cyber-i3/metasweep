import pytest
from pathlib import Path
import tempfile
import json
import hashlib
from datetime import datetime, timezone
from metasweep.utils import compute_hashes, fs_timestamps, save_json, render_html


class TestComputeHashes:
    def test_compute_hashes_md5(self):
        """Test MD5 hash computation."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"test content")
            f.flush()
            path = Path(f.name)
        
        hashes = compute_hashes(path)
        assert "md5" in hashes
        assert hashes["md5"] == hashlib.md5(b"test content").hexdigest()
        path.unlink()

    def test_compute_hashes_sha256(self):
        """Test SHA256 hash computation."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"test content")
            f.flush()
            path = Path(f.name)
        
        hashes = compute_hashes(path)
        assert "sha256" in hashes
        assert hashes["sha256"] == hashlib.sha256(b"test content").hexdigest()
        path.unlink()

    def test_compute_hashes_empty_file(self):
        """Test hash computation on empty file."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.flush()
            path = Path(f.name)
        
        hashes = compute_hashes(path)
        assert hashes["md5"] == hashlib.md5(b"").hexdigest()
        assert hashes["sha256"] == hashlib.sha256(b"").hexdigest()
        path.unlink()


class TestFsTimestamps:
    def test_fs_timestamps_returns_dict(self):
        """Test that fs_timestamps returns a dict with required keys."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"test")
            f.flush()
            path = Path(f.name)
        
        ts = fs_timestamps(path)
        assert isinstance(ts, dict)
        assert "created_at" in ts
        assert "modified_at" in ts
        assert "+" in ts["created_at"]  # ISO format with timezone
        path.unlink()

    def test_fs_timestamps_iso_format(self):
        """Test that timestamps are in ISO format."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"test")
            f.flush()
            path = Path(f.name)
        
        ts = fs_timestamps(path)
        # Try parsing ISO format
        datetime.fromisoformat(ts["created_at"])
        datetime.fromisoformat(ts["modified_at"])
        path.unlink()


class TestSaveJson:
    def test_save_json_creates_file(self):
        """Test that save_json creates a JSON file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            report = {"test": "data", "key": 123}
            out_dir = Path(tmpdir)
            result_path = save_json(report, out_dir, "test_report")
            
            assert result_path.exists()
            assert result_path.suffix == ".json"

    def test_save_json_content(self):
        """Test that saved JSON content is correct."""
        with tempfile.TemporaryDirectory() as tmpdir:
            report = {"test": "data", "nested": {"key": "value"}}
            out_dir = Path(tmpdir)
            result_path = save_json(report, out_dir, "test_report")
            
            with open(result_path, "r") as f:
                loaded = json.load(f)
            
            assert loaded["test"] == "data"
            assert loaded["nested"]["key"] == "value"

    def test_save_json_creates_directory(self):
        """Test that save_json creates output directory if it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            report = {"test": "data"}
            out_dir = Path(tmpdir) / "subdir" / "deep"
            result_path = save_json(report, out_dir, "test_report")
            
            assert out_dir.exists()
            assert result_path.exists()


class TestRenderHtml:
    def test_render_html_replaces_placeholders(self):
        """Test that render_html replaces template placeholders."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create template
            template_path = Path(tmpdir) / "template.html"
            template_path.write_text("<h1>{{TITLE}}</h1><p>{{CONTENT}}</p>")
            
            # Render
            out_path = Path(tmpdir) / "output.html"
            replacements = {"{{TITLE}}": "Test", "{{CONTENT}}": "Hello World"}
            render_html(template_path, out_path, replacements)
            
            # Check result
            assert out_path.exists()
            content = out_path.read_text()
            assert "<h1>Test</h1>" in content
            assert "<p>Hello World</p>" in content

    def test_render_html_creates_output_dir(self):
        """Test that render_html creates output directory if needed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            template_path = Path(tmpdir) / "template.html"
            template_path.write_text("<h1>{{TITLE}}</h1>")
            
            out_path = Path(tmpdir) / "output" / "subdir" / "file.html"
            replacements = {"{{TITLE}}": "Test"}
            render_html(template_path, out_path, replacements)
            
            assert out_path.exists()
            assert out_path.parent.exists()
