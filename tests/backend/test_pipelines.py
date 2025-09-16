import os
import sys
import tempfile
import pytest

# Add backend path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def _create_simple_pdf(text: str = "Hello") -> str:
    """Utility to create a minimal PDF for tests."""
    try:
        import fitz
    except Exception as exc:  # pragma: no cover - dependency issue
        pytest.fail(f"PyMuPDF is required for this test: {exc}")
    fd, path = tempfile.mkstemp(suffix=".pdf")
    os.close(fd)
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), text)
    doc.save(path)
    doc.close()
    return path


def test_evaluate_sequences_exists_and_runs():
    """Evaluate that a basic pipeline sequence can be scored."""
    try:
        from app import pipelines
    except Exception:
        pytest.fail("pipelines module not implemented")

    assert hasattr(pipelines, "evaluate_sequences"), "evaluate_sequences missing"
    scores = pipelines.evaluate_sequences([["step1", "step2"]])
    assert isinstance(scores, list)


def test_sequential_conversion_pipeline(tmp_path):
    """Ensure at least one sequential conversion executes correctly."""
    try:
        from app import pipelines
    except Exception:
        pytest.fail("pipelines module not implemented")

    if not hasattr(pipelines, "run_pipeline"):
        pytest.fail("run_pipeline missing")

    pdf_path = _create_simple_pdf()
    output = tmp_path / "out.epub"
    result = pipelines.run_pipeline(pdf_path, str(output))
    assert result.get("success") is True
    assert output.exists()
    os.remove(pdf_path)
