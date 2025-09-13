from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass
from typing import Iterable, List, Optional

import fitz  # type: ignore
import pytesseract
import pypandoc
from ebooklib import epub

# Heuristic set of fonts commonly used for mathematical formulas
FORMULA_FONTS = {
    "Symbol",
    "CambriaMath",
}
# Fonts starting with these prefixes will also be considered formulas
FORMULA_PREFIXES = ("CM",)


@dataclass
class FormulaRegion:
    """Represents a detected formula region."""

    page: int
    rect: fitz.Rect
    latex: str
    image_path: str


def _is_formula_font(font: str) -> bool:
    if font in FORMULA_FONTS:
        return True
    return any(font.startswith(prefix) for prefix in FORMULA_PREFIXES)


def detect_formulas(pdf_path: str, image_dir: Optional[str] = None) -> List[FormulaRegion]:
    """Detect potential formula regions in ``pdf_path``.

    The detection is heuristic: spans using fonts typically employed in
    mathematical typesetting (e.g. Symbol, Computer Modern) are grouped and
    extracted.  Each region is rasterised and passed through Tesseract to obtain
    a LaTeX representation of the formula.
    """

    doc = fitz.open(pdf_path)
    tmp_dir = image_dir or tempfile.mkdtemp(prefix="formulas_")
    formulas: List[FormulaRegion] = []

    for page_index, page in enumerate(doc, start=1):
        text = page.get_text("dict")
        for block in text.get("blocks", []):
            for line in block.get("lines", []):
                spans = line.get("spans", [])
                formula_spans = [s for s in spans if _is_formula_font(s.get("font", ""))]
                if not formula_spans:
                    continue
                rect = fitz.Rect(formula_spans[0]["bbox"])
                for span in formula_spans[1:]:
                    rect |= fitz.Rect(span["bbox"])
                pix = page.get_pixmap(clip=rect)
                img_path = os.path.join(tmp_dir, f"formula_{page_index}_{len(formulas)}.png")
                pix.save(img_path)
                latex = pytesseract.image_to_string(img_path, config="--oem 1 --psm 6")
                formulas.append(FormulaRegion(page_index, rect, latex.strip(), img_path))
    return formulas


def inject_formulas(epub_path: str, formulas: Iterable[FormulaRegion]) -> None:
    """Insert formulas into an EPUB file.

    For each detected formula we attempt to convert the extracted LaTeX to
    MathML.  If that fails the formula image is embedded with the recognised
    LaTeX as alternative text.
    """

    if not formulas:
        return

    book = epub.read_epub(epub_path)
    doc_items = list(book.get_items_of_type(epub.ITEM_DOCUMENT))
    if not doc_items:
        return

    for item in doc_items:
        content = item.get_content().decode("utf-8")
        body_close = content.rfind("</body>")
        if body_close == -1:
            continue

        additions: List[str] = []
        for idx, formula in enumerate(formulas):
            try:
                mathml = pypandoc.convert_text(
                    f"$$ {formula.latex} $$",
                    to="html",
                    format="latex",
                    extra_args=["--mathml"],
                )
                additions.append(mathml)
            except Exception:
                img_name = os.path.basename(formula.image_path)
                img_item = epub.EpubItem(
                    file_name=f"images/{img_name}",
                    media_type="image/png",
                    content=open(formula.image_path, "rb").read(),
                )
                book.add_item(img_item)
                additions.append(
                    f'<img src="images/{img_name}" alt="{formula.latex}">'  # noqa: E501
                )

        new_content = content[:body_close] + "\n" + "\n".join(additions) + content[body_close:]
        item.set_content(new_content.encode("utf-8"))

    epub.write_epub(epub_path, book)
