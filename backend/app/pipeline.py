"""Adapters and pipeline for running external conversion tools.

This module provides simple wrappers around external binaries such as
``pandoc`` and ``pdf2htmlEX``.  Each adapter measures execution time and
captures errors so the caller can evaluate cost and reliability.

Example:

    pipeline = ConversionPipeline(["pdf2htmlex", "pandoc"])
    result = pipeline.run("input.pdf")

"""

from __future__ import annotations

import logging
import os
import shutil
import subprocess
import tempfile
import time
from dataclasses import dataclass
from typing import Dict, List, Optional

import pypandoc


logger = logging.getLogger(__name__)


def _ensure_pandoc() -> None:
    """Ensure the pandoc binary is available.

    ``pypandoc`` requires the pandoc executable.  If it is not found, we try
    to download a local copy via :func:`pypandoc.download_pandoc`.
    """

    try:
        pypandoc.get_pandoc_version()
    except OSError:
        logger.info("Pandoc not found. Downloading a local copy...")
        pypandoc.download_pandoc()


@dataclass
class StepResult:
    success: bool
    duration: float
    output: Optional[str] = None
    error: Optional[str] = None


class PandocAdapter:
    """Adapter that converts documents using pandoc."""

    def __init__(self) -> None:
        _ensure_pandoc()

    def run(self, input_path: str, output_path: str) -> StepResult:
        start = time.perf_counter()
        try:
            pypandoc.convert_file(
                input_path,
                "epub3",
                outputfile=output_path,
            )
            duration = time.perf_counter() - start
            logger.info("pandoc completed in %.2fs", duration)
            return StepResult(True, duration, output=output_path)
        except Exception as exc:  # pragma: no cover - defensive
            duration = time.perf_counter() - start
            logger.error("pandoc failed: %s", exc)
            return StepResult(False, duration, error=str(exc))


class Pdf2HtmlEXAdapter:
    """Adapter that converts PDF to HTML using pdf2htmlEX."""

    def __init__(self) -> None:
        if shutil.which("pdf2htmlEX") is None:
            raise RuntimeError("pdf2htmlEX executable not found in PATH")

    def run(self, input_path: str) -> StepResult:
        start = time.perf_counter()
        output_fd, output_path = tempfile.mkstemp(suffix=".html")
        os.close(output_fd)

        cmd = ["pdf2htmlEX", input_path, output_path]
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            duration = time.perf_counter() - start
            logger.info("pdf2htmlEX completed in %.2fs", duration)
            return StepResult(True, duration, output=output_path)
        except subprocess.CalledProcessError as exc:
            duration = time.perf_counter() - start
            err = exc.stderr.decode(errors="ignore") if exc.stderr else str(exc)
            logger.error("pdf2htmlEX failed: %s", err)
            return StepResult(False, duration, error=err)


class ConversionPipeline:
    """Run a sequence of conversion steps.

    Steps are specified by name (``"pdf2htmlex"`` or ``"pandoc"``).  Each
    step is executed in order and metrics are recorded.  If a step fails the
    pipeline stops and returns the collected metrics along with the error.
    """

    def __init__(self, steps: List[str]):
        self.steps = steps
        self.adapters = {
            "pdf2htmlex": Pdf2HtmlEXAdapter(),
            "pandoc": PandocAdapter(),
        }

    def run(self, pdf_path: str) -> Dict[str, object]:
        current = pdf_path
        final_output: Optional[str] = None
        metrics: List[Dict[str, object]] = []

        for step in self.steps:
            adapter = self.adapters[step]
            if step == "pandoc":
                output_fd, output_path = tempfile.mkstemp(suffix=".epub")
                os.close(output_fd)
                result = adapter.run(current, output_path)
                final_output = output_path if result.success else None
            else:  # pdf2htmlex
                result = adapter.run(current)
                current = result.output or current

            metrics.append(
                {
                    "step": step,
                    "success": result.success,
                    "duration": result.duration,
                }
            )

            if not result.success:
                return {"success": False, "error": result.error, "metrics": metrics}

        return {"success": True, "output": final_output or current, "metrics": metrics}


def evaluate_sequences(sequences: List[List[str]]) -> List[Dict[str, object]]:
    return [{"steps": seq, "score": 0} for seq in sequences]
