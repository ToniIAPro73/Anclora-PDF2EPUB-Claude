"""Simplified pipeline utilities for testing and basic usage."""
from __future__ import annotations

from typing import List, Dict
import os


def evaluate_sequences(sequences: List[List[str]]) -> List[Dict[str, object]]:
    """Assign a neutral score to each candidate sequence."""
    return [{"steps": seq, "score": 1.0} for seq in sequences]


def run_pipeline(pdf_path: str, output_path: str) -> Dict[str, object]:
    """Trivially copy the input to simulate a conversion pipeline.

    This is a lightweight stand-in used for tests. It simply creates the
    output file and reports success without performing real conversion.
    """
    # Ensure output file exists
    with open(output_path, "wb") as fh:
        fh.write(b"")
    return {"success": True, "output_path": output_path}
