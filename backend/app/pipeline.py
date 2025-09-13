"""Adapters and pipeline for running external conversion tools.

This module provides simple wrappers around external binaries such as
``pandoc`` and ``pdf2htmlEX``.  Each adapter measures execution time and
captures errors so the caller can evaluate cost and reliability.

Example:

    pipeline = ConversionPipeline(["pdf2htmlex", "pandoc"])
    result = pipeline.run("input.pdf")

"""

from __future__ import annotations

import hashlib
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


class ConversionCache:
    """Simple filesystem based cache for conversion step outputs.

    Entries are stored under a cache directory using a filename derived from
    the SHA256 hash of the input file and the step name.  Cached files expire
    after ``expiry_seconds`` and a lightweight cleanup runs periodically to
    remove stale entries.
    """

    def __init__(self, cache_dir: Optional[str] = None, expiry_seconds: int = 3600) -> None:
        self.cache_dir = cache_dir or tempfile.mkdtemp(prefix="conversion_cache_")
        self.expiry_seconds = expiry_seconds
        os.makedirs(self.cache_dir, exist_ok=True)
        self._last_cleanup = 0.0

    # ------------------------------------------------------------------
    def _hash_file(self, path: str) -> str:
        hasher = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    def _cache_path(self, file_hash: str, step: str, ext: str) -> str:
        name = f"{file_hash}-{step}{ext}"
        return os.path.join(self.cache_dir, name)

    # ------------------------------------------------------------------
    def get(self, input_path: str, step: str) -> Optional[str]:
        """Return cached file for ``step`` and ``input_path`` if valid."""
        self.cleanup()
        file_hash = self._hash_file(input_path)
        prefix = f"{file_hash}-{step}"
        for fname in os.listdir(self.cache_dir):
            if fname.startswith(prefix):
                path = os.path.join(self.cache_dir, fname)
                if time.time() - os.path.getmtime(path) < self.expiry_seconds:
                    return path
                try:
                    os.remove(path)
                except OSError:
                    pass
        return None

    def set(self, input_path: str, step: str, output_path: str) -> str:
        """Store ``output_path`` result for ``step`` keyed by ``input_path``."""
        file_hash = self._hash_file(input_path)
        ext = os.path.splitext(output_path)[1]
        dest = self._cache_path(file_hash, step, ext)
        shutil.copy2(output_path, dest)
        return dest

    # ------------------------------------------------------------------
    def cleanup(self) -> None:
        """Remove expired cache entries periodically."""
        now = time.time()
        if now - self._last_cleanup < self.expiry_seconds:
            return
        for fname in os.listdir(self.cache_dir):
            path = os.path.join(self.cache_dir, fname)
            if now - os.path.getmtime(path) > self.expiry_seconds:
                try:
                    os.remove(path)
                except OSError:
                    pass
        self._last_cleanup = now


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

    def __init__(self, steps: List[str], cache: Optional[ConversionCache] = None):
        self.steps = steps
        self.cache = cache or ConversionCache()
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

            cached_output = self.cache.get(current, step)
            if cached_output:
                result = StepResult(True, 0.0, output=cached_output)
            else:
                if step == "pandoc":
                    output_fd, output_path = tempfile.mkstemp(suffix=".epub")
                    os.close(output_fd)
                    result = adapter.run(current, output_path)
                else:  # pdf2htmlex
                    result = adapter.run(current)

                if result.success and result.output:
                    result.output = self.cache.set(current, step, result.output)

            metrics.append(
                {
                    "step": step,
                    "success": result.success,
                    "duration": result.duration,
                }
            )

            if not result.success:
                return {"success": False, "error": result.error, "metrics": metrics}

            if step == "pandoc":
                final_output = result.output
            else:
                current = result.output or current

        return {"success": True, "output": final_output or current, "metrics": metrics}


def evaluate_sequences(sequences: List[List[str]]) -> List[Dict[str, object]]:
    return [{"steps": seq, "score": 0} for seq in sequences]
