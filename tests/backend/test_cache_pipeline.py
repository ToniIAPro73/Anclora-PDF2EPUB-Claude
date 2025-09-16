import os
import os
import sys
import tempfile
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.pipeline import ConversionPipeline, StepResult, ConversionCache


class DummyPdfAdapter:
    def __init__(self):
        self.calls = 0

    def run(self, input_path):
        self.calls += 1
        fd, output_path = tempfile.mkstemp(suffix=".html")
        os.close(fd)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("html")
        return StepResult(True, 0.01, output=output_path)


class DummyPandocAdapter:
    def __init__(self):
        self.calls = 0

    def run(self, input_path, output_path, pdf_path=None):
        self.calls += 1
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("epub")
        return StepResult(True, 0.01, output=output_path)


def test_pipeline_uses_cache(monkeypatch, tmp_path):
    pdf_path = tmp_path / "in.pdf"
    pdf_path.write_text("dummy")

    html_adapter = DummyPdfAdapter()
    epub_adapter = DummyPandocAdapter()
    monkeypatch.setattr("app.pipeline.Pdf2HtmlEXAdapter", lambda: html_adapter)
    monkeypatch.setattr("app.pipeline.PandocAdapter", lambda: epub_adapter)

    pipeline = ConversionPipeline(
        ["pdf2htmlex", "pandoc"], cache=ConversionCache(cache_dir=str(tmp_path / "cache"))
    )

    first = pipeline.run(str(pdf_path))
    assert first["success"] is True
    assert html_adapter.calls == 1
    assert epub_adapter.calls == 1

    second = pipeline.run(str(pdf_path))
    assert second["success"] is True
    assert html_adapter.calls == 1
    assert epub_adapter.calls == 1
    assert first["output"] == second["output"]


def test_cache_expiration(tmp_path):
    cache = ConversionCache(expiry_seconds=1)
    inp = tmp_path / "file.txt"
    out = tmp_path / "out.txt"
    inp.write_text("x")
    out.write_text("y")

    cached = cache.set(str(inp), "step", str(out))
    assert cache.get(str(inp), "step") == cached

    # Force the cache file to appear old and trigger cleanup
    old = time.time() - 3600
    os.utime(cached, (old, old))
    cache._last_cleanup = 0
    cache.cleanup()
    assert not os.path.exists(cached)
    assert cache.get(str(inp), "step") is None
