import os
import sys
import tempfile
import zipfile
import fitz
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.converter import (
    PDFAnalyzer,
    ContentType,
    PDFAnalysis,
    ConversionEngine,
    EnhancedPDFToEPUBConverter,
    RapidConverter,
)
from langdetect import LangDetectException


def _create_simple_pdf(text: str = "Hello world") -> str:
    fd, path = tempfile.mkstemp(suffix=".pdf")
    os.close(fd)
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), text)
    doc.save(path)
    doc.close()
    return path


def _create_empty_pdf() -> str:
    fd, path = tempfile.mkstemp(suffix=".pdf")
    os.close(fd)
    doc = fitz.open()
    doc.new_page()
    doc.save(path)
    doc.close()
    return path


def _analysis_for(pdf_path: str) -> PDFAnalysis:
    return PDFAnalysis(
        page_count=1,
        file_size=os.path.getsize(pdf_path),
        text_extractable=True,
        image_count=0,
        content_type=ContentType.TEXT_ONLY,
        issues=[],
        complexity_score=1,
        recommended_engine=ConversionEngine.RAPID,
    )


def test_pdf_analyzer_detects_basic_metrics():
    pdf_path = _create_simple_pdf()
    analyzer = PDFAnalyzer()
    analysis = analyzer.analyze_pdf(pdf_path)
    assert analysis.page_count == 1
    assert analysis.text_extractable is True
    assert analysis.image_count == 0
    assert analysis.content_type == ContentType.TEXT_ONLY
    os.remove(pdf_path)


def test_pdf_analyzer_handles_pdf_without_text():
    pdf_path = _create_empty_pdf()
    analyzer = PDFAnalyzer()
    analysis = analyzer.analyze_pdf(pdf_path)
    assert analysis.text_extractable is False
    assert "No text extractable, OCR required" in analysis.issues
    os.remove(pdf_path)


def test_pdf_analyzer_handles_corrupt_images(monkeypatch):
    pdf_path = _create_simple_pdf()
    analyzer = PDFAnalyzer()

    class DummyPage:
        def get_text(self):
            return ""

        def get_images(self):
            raise ValueError("corrupt image")

    class DummyDoc:
        def __len__(self):
            return 1

        def __iter__(self):
            return iter([DummyPage()])

    monkeypatch.setattr(fitz, "open", lambda _: DummyDoc())
    analysis = analyzer.analyze_pdf(pdf_path)
    assert analysis.issues == ["Error analyzing PDF"]
    assert analysis.content_type == ContentType.SCANNED_DOCUMENT
    os.remove(pdf_path)


def test_pdf_analyzer_handles_language_detection_errors(monkeypatch):
    pdf_path = _create_simple_pdf()
    analyzer = PDFAnalyzer()

    def fake_detect(_text):
        raise LangDetectException("fail")

    monkeypatch.setattr("app.converter.detect", fake_detect)
    analysis = analyzer.analyze_pdf(pdf_path)
    assert analysis.language is None
    os.remove(pdf_path)


def test_enhanced_converter_uses_recommended_engine(monkeypatch):
    pdf_path = _create_simple_pdf()
    converter = EnhancedPDFToEPUBConverter()

    fake_analysis = PDFAnalysis(
        page_count=1,
        file_size=100,
        text_extractable=True,
        image_count=0,
        content_type=ContentType.TEXT_ONLY,
        issues=[],
        complexity_score=1,
        recommended_engine=ConversionEngine.BALANCED,
    )

    monkeypatch.setattr(converter.analyzer, "analyze_pdf", lambda path: fake_analysis)

    called = {}

    def fake_balanced(pdf_path_arg, output_path, analysis, metadata):
        called["engine"] = "balanced"
        return {"success": True, "quality_metrics": {}}

    monkeypatch.setattr(converter.engines[ConversionEngine.BALANCED], "convert", fake_balanced)

    result = converter.convert(pdf_path)
    assert result["engine_used"] == "balanced"
    assert called.get("engine") == "balanced"
    assert result["pipeline_used"] == ["analyze", "balanced"]
    assert "quality" in result["pipeline_metrics"]
    assert "cost" in result["pipeline_metrics"]
    os.remove(pdf_path)


def test_rapid_converter_generates_epub(tmp_path):
    pdf_path = _create_simple_pdf()
    output_path = tmp_path / "output.epub"
    analysis = _analysis_for(pdf_path)
    converter = RapidConverter()
    result = converter.convert(pdf_path, str(output_path), analysis, metadata={"title": "Test"})
    assert result["success"] is True
    assert output_path.exists()
    os.remove(pdf_path)


def test_rapid_converter_preserves_tables(tmp_path):
    pdf_path = _create_simple_pdf("<table><tr><td>Cell</td></tr></table>")
    output_path = tmp_path / "table.epub"
    analysis = _analysis_for(pdf_path)
    converter = RapidConverter()
    converter.convert(pdf_path, str(output_path), analysis, metadata={"title": "Table"})
    import zipfile
    with zipfile.ZipFile(output_path, 'r') as zf:
        content = zf.read('EPUB/page_1.xhtml').decode('utf-8')
    assert '<table>' in content
    os.remove(pdf_path)


def test_rapid_converter_handles_math(tmp_path):
    mathml = "<math><mi>x</mi><msup><mi>x</mi><mn>2</mn></msup></math>"
    pdf_path = _create_simple_pdf(mathml)
    output_path = tmp_path / "math.epub"
    analysis = _analysis_for(pdf_path)
    converter = RapidConverter()
    converter.convert(pdf_path, str(output_path), analysis, metadata={"title": "Math"})
    import zipfile
    with zipfile.ZipFile(output_path, 'r') as zf:
        content = zf.read('EPUB/page_1.xhtml').decode('utf-8')
    assert ('<math' in content) or ('<img' in content and 'alt=' in content)
    os.remove(pdf_path)


def test_suggest_best_pipeline_returns_sequence_and_metrics():
    pdf_path = _create_simple_pdf()
    converter = EnhancedPDFToEPUBConverter()
    pipeline, metrics, analysis = converter.suggest_best_pipeline(pdf_path)
    assert pipeline[0] == "analyze"
    assert pipeline[-1] in [e.value for e in ConversionEngine]
    assert "quality" in metrics and "cost" in metrics
    assert isinstance(analysis, PDFAnalysis)
    os.remove(pdf_path)


def test_convert_injects_tables(monkeypatch):
    pdf_path = _create_simple_pdf()
    converter = EnhancedPDFToEPUBConverter()

    def fake_extract(_):
        return [{"page": 1, "content": "<table><tr><td>1</td></tr></table>"}]

    monkeypatch.setattr("app.converter.extract_tables", fake_extract)
    result = converter.convert(pdf_path)
    assert result["success"] is True
    with zipfile.ZipFile(result["output_path"], "r") as zf:
        html = zf.read("EPUB/page_1.xhtml").decode("utf-8")
        assert "<table>" in html
    os.remove(pdf_path)
    os.remove(result["output_path"])
