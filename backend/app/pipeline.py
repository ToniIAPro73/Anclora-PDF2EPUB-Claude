from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class ConversionSequence:
    """Representa una secuencia de conversión concreta"""
    name: str
    steps: List[str]
    base_quality: int
    base_cost: int


class SequenceEvaluator:
    """Evalúa diferentes secuencias de conversión"""
    def __init__(self) -> None:
        # Definición de secuencias soportadas
        self.sequences = [
            ConversionSequence(
                name="pdf_to_epub_direct",
                steps=["pdf_to_epub"],
                base_quality=60,
                base_cost=1,
            ),
            ConversionSequence(
                name="pdf_to_html_to_epub",
                steps=["pdf_to_html", "pandoc_html_to_epub"],
                base_quality=80,
                base_cost=3,
            ),
            ConversionSequence(
                name="pdf_to_images_ocr_to_epub",
                steps=["pdf_to_images", "ocr", "pandoc_html_to_epub"],
                base_quality=70,
                base_cost=5,
            ),
        ]

    def evaluate(self, pdf_path: str, analysis: Any) -> List[Dict[str, Any]]:
        """Devuelve estimaciones de calidad y coste para cada secuencia"""
        results: List[Dict[str, Any]] = []

        for seq in self.sequences:
            quality = seq.base_quality
            cost = seq.base_cost

            # Ajustes heurísticos basados en el análisis del PDF
            if not getattr(analysis, "text_extractable", True):
                if "ocr" in seq.steps:
                    quality += 15
                else:
                    quality -= 30
            if getattr(analysis, "image_count", 0) > 0 and "pdf_to_epub" in seq.steps:
                quality -= 10
            if getattr(analysis, "complexity_score", 0) > 3:
                cost += 1
                quality += 5

            quality = max(0, min(100, quality))

            results.append({
                "sequence": seq.name,
                "steps": seq.steps,
                "estimated_quality": quality,
                "estimated_cost": cost,
            })

        return results


def evaluate_sequences(pdf_path: str, analysis: Any) -> List[Dict[str, Any]]:
    """Evaluación de todas las secuencias disponibles"""
    evaluator = SequenceEvaluator()
    return evaluator.evaluate(pdf_path, analysis)
