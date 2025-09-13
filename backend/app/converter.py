import os
import fitz  # PyMuPDF
import ebooklib
from ebooklib import epub
from enum import Enum
import pytesseract
from PIL import Image
import io
from langdetect import detect, LangDetectException
import tempfile
import uuid
import logging
import zipfile

from .table_extractor import extract_tables

from .pipelines import evaluate_sequences as pipeline_evaluate_sequences

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TESSERACT_LANG_MAP = {
    'en': 'eng',
    'es': 'spa',
    'fr': 'fra',
    'de': 'deu',
    'it': 'ita',
    'pt': 'por',
}


def get_ocr_lang(detected_lang):
    base = TESSERACT_LANG_MAP.get(detected_lang, 'eng')
    if base != 'eng':
        return f"{base}+eng"
    return base


def compress_image(image_bytes, image_ext):
    try:
        with Image.open(io.BytesIO(image_bytes)) as img:
            buffer = io.BytesIO()
            if img.format == 'PNG':
                img.save(buffer, format='PNG', optimize=True)
            else:
                img.save(buffer, format='JPEG', quality=70, optimize=True)
            compressed = buffer.getvalue()
            if len(compressed) < len(image_bytes):
                logger.info(
                    f"Image compressed from {len(image_bytes)} to {len(compressed)} bytes"
                )
                return compressed
    except Exception as e:
        logger.warning(f"Image compression failed: {e}")
    return image_bytes

class ContentType(Enum):
    TEXT_ONLY = "text_only"
    TEXT_WITH_IMAGES = "text_with_images"
    IMAGE_HEAVY = "image_heavy"
    SCANNED_DOCUMENT = "scanned_document"
    TECHNICAL_MANUAL = "technical_manual"
    ACADEMIC_PAPER = "academic_paper"

class ConversionEngine(Enum):
    RAPID = "rapid"
    BALANCED = "balanced"
    QUALITY = "quality"

class PDFAnalysis:
    def __init__(self, page_count, file_size, text_extractable,
                 image_count, content_type, issues, complexity_score,
                 recommended_engine, language=None):
        self.page_count = page_count
        self.file_size = file_size
        self.text_extractable = text_extractable
        self.image_count = image_count
        self.content_type = content_type
        self.issues = issues
        self.complexity_score = complexity_score
        self.recommended_engine = recommended_engine
        self.language = language

class PDFAnalyzer:
    IMAGE_HEAVY_RATIO = 1.5
    TABLE_KEYWORDS = ["table", "tabla", "tabella", "tabelle", "tableau"]
    FORMULA_KEYWORDS = ["equation", "formula", "theorem", "proof"]
    MATH_SYMBOLS = ["∑", "∫", "√", "∞", "≈", "≠", "≤", "≥", "÷", "×", "π", "±"]

    def analyze_pdf(self, pdf_path):
        """Analiza un PDF y devuelve métricas y recomendaciones"""

        # 1. Métricas básicas
        file_size = os.path.getsize(pdf_path)

        try:
            doc = fitz.open(pdf_path)
            page_count = len(doc)

            # 2. Análisis de contenido
            text_length = 0
            image_count = 0

            for page in doc:
                text_length += len(page.get_text())
                image_count += len(page.get_images())

            text_extractable = text_length > 0

            # 3. Determinar tipo de contenido
            if not text_extractable and image_count > 0:
                content_type = ContentType.SCANNED_DOCUMENT
            elif image_count > page_count * self.IMAGE_HEAVY_RATIO:
                content_type = ContentType.IMAGE_HEAVY
            elif image_count > 0:
                content_type = ContentType.TEXT_WITH_IMAGES
            else:
                content_type = ContentType.TEXT_ONLY

            detected_language = None
            text_sample = ""

            # Detección específica para documentos académicos o técnicos
            if text_extractable:
                for i in range(min(5, page_count)):
                    text_sample += doc[i].get_text()

                if text_sample.strip():
                    try:
                        detected_language = detect(text_sample)
                    except LangDetectException:
                        detected_language = None

                if any(marker in text_sample.lower() for marker in
                       ["abstract", "keywords", "references", "bibliography", "doi"]):
                    content_type = ContentType.ACADEMIC_PAPER

                if any(marker in text_sample.lower() for marker in
                       ["figure", "table", "diagram", "appendix", "specification"]):
                    content_type = ContentType.TECHNICAL_MANUAL

            # 4. Detectar problemas
            issues = []

            if not text_extractable:
                issues.append("No text extractable, OCR required")

            if image_count == 0 and page_count > 0:
                issues.append("No images detected")

            # Verificar si hay tablas y fórmulas
            table_hits = 0
            formula_pages = 0
            formula_symbols = 0
            for page in doc:
                text = page.get_text("text")
                text_lower = text.lower()

                for kw in self.TABLE_KEYWORDS:
                    if kw in text_lower:
                        table_hits += 1
                        break

                page_symbol_count = sum(text.count(sym) for sym in self.MATH_SYMBOLS)
                if any(kw in text_lower for kw in self.FORMULA_KEYWORDS) or page_symbol_count > 0:
                    formula_pages += 1
                formula_symbols += page_symbol_count

            table_density = table_hits / page_count if page_count else 0
            formula_density = formula_symbols / page_count if page_count else 0

            has_tables = table_hits >= 2
            dense_tables = table_density > 0.1
            dense_formulas = formula_density > 1 or (formula_pages / page_count if page_count else 0) > 0.1

            if dense_tables:
                issues.append("Tables detected, may require special handling")
            if dense_formulas:
                issues.append("Formulas detected, may require special handling")

            # 5. Calcular complejidad
            complexity_score = 1 + \
                                 (0 if text_extractable else 2) + \
                                 (0 if image_count < page_count * 0.8 else 1) + \
                                 (0 if not has_tables else 1) + \
                                 (0 if page_count < 20 else 1)

            if dense_tables or dense_formulas:
                complexity_score += 1
                complexity_score = max(complexity_score, 4)

            complexity_score = min(5, complexity_score)

            # 6. Recomendar motor
            if complexity_score <= 1:
                recommended_engine = ConversionEngine.RAPID
            elif complexity_score <= 3:
                recommended_engine = ConversionEngine.BALANCED
            else:
                recommended_engine = ConversionEngine.QUALITY

            return PDFAnalysis(
                page_count=page_count,
                file_size=file_size,
                text_extractable=text_extractable,
                image_count=image_count,
                content_type=content_type,
                issues=issues,
                complexity_score=complexity_score,
                recommended_engine=recommended_engine,
                language=detected_language
            )

        except Exception as e:
            logger.error(f"Error analyzing PDF: {str(e)}")
            # Retornar análisis por defecto con recomendación de motor de calidad
            return PDFAnalysis(
                page_count=0,
                file_size=file_size,
                text_extractable=False,
                image_count=0,
                content_type=ContentType.SCANNED_DOCUMENT,
                issues=["Error analyzing PDF"],
                complexity_score=5,
                recommended_engine=ConversionEngine.QUALITY,
                language=None
            )


class SequenceEvaluator:
    """Evaluates different conversion pipelines and suggests the best one."""

    PIPELINE_TEMPLATES = {
        ConversionEngine.RAPID: {
            "sequence": ["analyze", ConversionEngine.RAPID.value],
            "metrics": {"quality": 0.7, "cost": 1},
        },
        ConversionEngine.BALANCED: {
            "sequence": ["analyze", ConversionEngine.BALANCED.value],
            "metrics": {"quality": 0.85, "cost": 2},
        },
        ConversionEngine.QUALITY: {
            "sequence": ["analyze", ConversionEngine.QUALITY.value],
            "metrics": {"quality": 0.95, "cost": 3},
        },
    }

    def __init__(self, analyzer: PDFAnalyzer):
        self.analyzer = analyzer

    def evaluate(self, pdf_path, metadata=None):
        """Return best pipeline (sequence and metrics) and the analysis."""
        analysis = self.analyzer.analyze_pdf(pdf_path)
        template = self.PIPELINE_TEMPLATES.get(
            analysis.recommended_engine, self.PIPELINE_TEMPLATES[ConversionEngine.RAPID]
        )
        return template["sequence"], template["metrics"], analysis

class BaseConverter:
    def convert(self, pdf_path, output_path, analysis, metadata=None):
        """Método base que debe ser implementado por subclases"""
        raise NotImplementedError("Subclasses must implement convert()")

class RapidConverter(BaseConverter):
    """Conversión básica rápida para documentos simples"""
    def convert(self, pdf_path, output_path, analysis, metadata=None):
        try:
            # Crear EPUB
            book = epub.EpubBook()
            
            # Configurar metadatos
            book.set_title(metadata.get('title', 'Converted Document'))
            book.set_language(metadata.get('language', 'es'))
            
            if 'author' in metadata:
                book.add_author(metadata['author'])

            # Abrir PDF
            pdf = fitz.open(pdf_path)
            
            # Crear capítulos
            chapters = []
            
            for i, page in enumerate(pdf):
                # Extraer texto
                text = page.get_text()
                
                # Crear capítulo
                chapter = epub.EpubHtml(
                    title=f"Page {i+1}", 
                    file_name=f"page_{i+1}.xhtml"
                )
                
                # Contenido HTML simple
                chapter.content = f"""
                <html>
                <head>
                    <title>Page {i+1}</title>
                </head>
                <body>
                    <h1>Page {i+1}</h1>
                    <div>{text}</div>
                </body>
                </html>
                """
                
                book.add_item(chapter)
                chapters.append(chapter)
            
            # Añadir capítulos a la tabla de contenidos
            book.toc = chapters
            
            # Añadir CSS
            style = epub.EpubItem(
                uid="style_default",
                file_name="style/default.css",
                media_type="text/css",
                content="""
                    body { font-family: sans-serif; }
                    h1 { text-align: center; }
                """
            )
            book.add_item(style)
            
            # Añadir elementos al esqueleto del EPUB
            book.add_item(epub.EpubNcx())
            book.add_item(epub.EpubNav())
            
            # Definir la estructura del EPUB
            book.spine = ['nav'] + chapters
            
            # Escribir EPUB a disco
            epub.write_epub(output_path, book)
            
            return {
                "success": True,
                "message": "Conversion completed successfully",
                "quality_metrics": {
                    "text_preserved": 100,
                    "images_preserved": 0,
                    "overall": 70
                }
            }
            
        except Exception as e:
            logger.error(f"Error in rapid conversion: {str(e)}")
            return {
                "success": False,
                "message": f"Error during conversion: {str(e)}",
                "quality_metrics": {
                    "text_preserved": 0,
                    "images_preserved": 0,
                    "overall": 0
                }
            }

class BalancedConverter(BaseConverter):
    """Conversión equilibrada para documentos con texto e imágenes"""
    def convert(self, pdf_path, output_path, analysis, metadata=None):
        try:
            metadata = metadata or {}
            start_time = time.time()

            # Crear EPUB
            book = epub.EpubBook()

            # Configurar metadatos
            book.set_title(metadata.get('title', 'Converted Document'))
            book.set_language(metadata.get('language', 'es'))

            if 'author' in metadata:
                book.add_author(metadata['author'])

            # Determinar número de hilos según recursos disponibles
            max_workers = metadata.get('max_workers') or max(1, os.cpu_count() or 1)
            logger.info(f"Using {max_workers} threads for balanced conversion")

            # Obtener número de páginas
            doc = fitz.open(pdf_path)
            page_count = len(doc)
            doc.close()

            def process_page(page_number):
                local_pdf = fitz.open(pdf_path)
                page = local_pdf.load_page(page_number)

                text = page.get_text()

                html_content = f"""
                <html>
                <head>
                    <title>Page {page_number + 1}</title>
                </head>
                <body>
                    <h1>Page {page_number + 1}</h1>
                    <div>{text}</div>
                """

                images = page.get_images()
                image_items = []

                for img_index, img in enumerate(images):
                    xref = img[0]
                    base_image = local_pdf.extract_image(xref)
                    image_bytes = base_image["image"]
                    image_ext = base_image["ext"]

                    image_filename = f"images/image_p{page_number + 1}_{img_index}.{image_ext}"

                    epub_image = epub.EpubItem(
                        uid=f"image_p{page_number + 1}_{img_index}",
                        file_name=image_filename,
                        media_type=f"image/{image_ext}",
                        content=compress_image(image_bytes, image_ext)
                    )
                    image_items.append(epub_image)

                    html_content += f"""
                    <div class=\"image-container\">
                        <img src=\"{image_filename}\" alt=\"Image\" />
                    </div>
                    """

                html_content += """
                </body>
                </html>
                """

                chapter = epub.EpubHtml(
                    title=f"Page {page_number + 1}",
                    file_name=f"page_{page_number + 1}.xhtml"
                )
                chapter.content = html_content
                local_pdf.close()
                return page_number, chapter, image_items

            # Procesar páginas en paralelo
            chapters = []
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = [executor.submit(process_page, i) for i in range(page_count)]
                results = [f.result() for f in futures]

            # Combinar resultados manteniendo el orden
            results.sort(key=lambda x: x[0])
            for _, chapter, image_items in results:
                for item in image_items:
                    book.add_item(item)
                book.add_item(chapter)
                chapters.append(chapter)

            # Añadir capítulos a la tabla de contenidos
            book.toc = chapters

            # Añadir CSS
            style = epub.EpubItem(
                uid="style_default",
                file_name="style/default.css",
                media_type="text/css",
                content="""
                    body { font-family: sans-serif; margin: 1em; }
                    h1 { text-align: center; }
                    .image-container { text-align: center; margin: 1em 0; }
                    img { max-width: 100%; height: auto; }
                """
            )
            book.add_item(style)

            # Añadir elementos al esqueleto del EPUB
            book.add_item(epub.EpubNcx())
            book.add_item(epub.EpubNav())

            # Definir la estructura del EPUB
            book.spine = ['nav'] + chapters

            # Escribir EPUB a disco
            epub.write_epub(output_path, book)

            end_time = time.time()
            logger.info(
                f"Balanced conversion completed in {end_time - start_time:.2f}s using {max_workers} threads"
            )

            return {
                "success": True,
                "message": "Conversion completed successfully with images",
                "quality_metrics": {
                    "text_preserved": 100,
                    "images_preserved": 90,
                    "overall": 85
                },
                "time_taken": end_time - start_time,
                "workers_used": max_workers,
            }

        except Exception as e:
            logger.error(f"Error in balanced conversion: {str(e)}")
            return {
                "success": False,
                "message": f"Error during conversion: {str(e)}",
                "quality_metrics": {
                    "text_preserved": 0,
                    "images_preserved": 0,
                    "overall": 0
                }
            }

class QualityConverter(BaseConverter):
    """Conversión de alta calidad para documentos complejos, incluye OCR"""
    TEXT_OCR_THRESHOLD = 80

    def convert(self, pdf_path, output_path, analysis, metadata=None):
        try:
            # Crear EPUB
            book = epub.EpubBook()
            
            # Configurar metadatos
            book.set_title(metadata.get('title', 'Converted Document'))
            book.set_language(metadata.get('language', 'es'))
            
            if 'author' in metadata:
                book.add_author(metadata['author'])

            ocr_lang = metadata.get('ocr_languages', 'eng')

            # Abrir PDF
            pdf = fitz.open(pdf_path)
            
            # Crear capítulos
            chapters = []
            
            # Directorio temporal para imagenes procesadas por OCR
            with tempfile.TemporaryDirectory() as tmpdir:
                for i, page in enumerate(pdf):
                    # Intentar extraer texto
                    text = page.get_text()
                    needs_ocr = len(text.strip()) < self.TEXT_OCR_THRESHOLD
                    
                    # Si no hay suficiente texto, aplicar OCR
                    if needs_ocr:
                        # Renderizar página a imagen
                        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                        img_path = os.path.join(tmpdir, f"page_{i}.png")
                        pix.save(img_path)
                        
                        # Aplicar OCR
                        img = Image.open(img_path)
                        text = pytesseract.image_to_string(img, lang=ocr_lang)
                    
                    # Crear capítulo
                    chapter = epub.EpubHtml(
                        title=f"Page {i+1}", 
                        file_name=f"page_{i+1}.xhtml"
                    )
                    
                    # Contenido HTML base
                    html_content = f"""
                    <html>
                    <head>
                        <title>Page {i+1}</title>
                    </head>
                    <body>
                        <h1>Page {i+1}</h1>
                    """
                    
                    # Formatear el texto con párrafos
                    paragraphs = text.split('\n\n')
                    for para in paragraphs:
                        if para.strip():
                            html_content += f"<p>{para}</p>\n"
                    
                    # Extraer imágenes de la página
                    images = page.get_images()
                    image_files = []
                    
                    for img_index, img in enumerate(images):
                        xref = img[0]
                        base_image = pdf.extract_image(xref)
                        image_bytes = base_image["image"]
                        image_ext = base_image["ext"]

                        image_bytes = compress_image(image_bytes, image_ext)

                        # Generar nombre único para la imagen
                        image_filename = f"images/image_p{i+1}_{img_index}.{image_ext}"

                        # Crear objeto imagen para EPUB
                        epub_image = epub.EpubItem(
                            uid=f"image_p{i+1}_{img_index}",
                            file_name=image_filename,
                            media_type=f"image/{image_ext}",
                            content=image_bytes
                        )
                        
                        book.add_item(epub_image)
                        image_files.append(image_filename)
                    
                    # Añadir imágenes al HTML
                    for img_file in image_files:
                        html_content += f"""
                        <div class="image-container">
                            <img src="{img_file}" alt="Image" />
                        </div>
                        """
                    
                    html_content += """
                    </body>
                    </html>
                    """
                    
                    chapter.content = html_content
                    book.add_item(chapter)
                    chapters.append(chapter)
            
            # Añadir capítulos a la tabla de contenidos
            book.toc = chapters
            
            # Añadir CSS
            style = epub.EpubItem(
                uid="style_default",
                file_name="style/default.css",
                media_type="text/css",
                content="""
                    body { font-family: serif; margin: 1.2em; line-height: 1.5; }
                    h1 { text-align: center; font-size: 1.5em; margin: 1em 0; }
                    p { text-indent: 1em; margin: 0.5em 0; }
                    .image-container { text-align: center; margin: 1.5em 0; }
                    img { max-width: 100%; height: auto; }
                """
            )
            book.add_item(style)
            
            # Añadir elementos al esqueleto del EPUB
            book.add_item(epub.EpubNcx())
            book.add_item(epub.EpubNav())
            
            # Definir la estructura del EPUB
            book.spine = ['nav'] + chapters
            
            # Escribir EPUB a disco
            epub.write_epub(output_path, book)
            
            # Calcular métricas de calidad
            total_text = 0
            total_images = 0
            
            for page in pdf:
                total_text += len(page.get_text())
                total_images += len(page.get_images())
            
            text_preserved = 100 if total_text > 0 else 0
            images_preserved = 100 if total_images > 0 else 0
            
            return {
                "success": True,
                "message": "High quality conversion completed successfully",
                "quality_metrics": {
                    "text_preserved": text_preserved,
                    "images_preserved": images_preserved,
                    "overall": 95
                }
            }
            
        except Exception as e:
            logger.error(f"Error in quality conversion: {str(e)}")
            return {
                "success": False,
                "message": f"Error during conversion: {str(e)}",
                "quality_metrics": {
                    "text_preserved": 0,
                    "images_preserved": 0,
                    "overall": 0
                }
            }

class EnhancedPDFToEPUBConverter:
    """Conversor principal que selecciona y utiliza el motor adecuado"""
    def __init__(self):
        self.analyzer = PDFAnalyzer()
        self.engines = {
            ConversionEngine.RAPID: RapidConverter(),
            ConversionEngine.BALANCED: BalancedConverter(),
            ConversionEngine.QUALITY: QualityConverter(),
        }

        self.sequence_evaluator = SequenceEvaluator(self.analyzer)

    def suggest_best_pipeline(self, pdf_path, metadata=None):
        """Suggest an optimal pipeline for the given PDF."""
        return self.sequence_evaluator.evaluate(pdf_path, metadata)

    def convert(self, pdf_path, output_path=None, engine=None, metadata=None, pipeline=None):

        """
        Convierte un PDF a EPUB usando el motor especificado o uno automáticamente seleccionado
        
        Args:
            pdf_path: Ruta al archivo PDF
            output_path: Ruta de salida para el EPUB (opcional)
            engine: Motor de conversión específico (opcional)
            metadata: Metadatos para el EPUB (opcional)
            
        Returns:
            Diccionario con el resultado y métricas
        """
        try:
            # Generar nombre de salida si no se proporciona
            if output_path is None:
                pdf_basename = os.path.basename(pdf_path)
                pdf_name, _ = os.path.splitext(pdf_basename)
                output_path = f"{pdf_name}_{uuid.uuid4().hex[:8]}.epub"
            
            # Metadatos por defecto
            if metadata is None:
                pdf_basename = os.path.basename(pdf_path)
                pdf_name, _ = os.path.splitext(pdf_basename)
                metadata = {
                    'title': pdf_name,
                    'language': 'es',
                }
            
            # 1. Obtener pipeline si no se proporciona
            if pipeline is None:
                pipeline, pipeline_metrics, analysis = self.suggest_best_pipeline(
                    pdf_path, metadata
                )
            else:
                pipeline_metrics = []
                analysis = self.analyzer.analyze_pdf(pdf_path)

            logger.info(f"Pipeline to execute: {pipeline}")

            # 2. Actualizar metadatos con información del análisis
            if analysis.language:
                metadata['language'] = analysis.language
            metadata['ocr_languages'] = get_ocr_lang(analysis.language)

            # 3. Ejecutar la secuencia definida en el pipeline
            selected_engine = engine
            result = None

            table_map = {}
            try:
                for tbl in extract_tables(pdf_path):
                    table_map.setdefault(tbl["page"], []).append(tbl["content"])
            except Exception as e:
                logger.warning(f"Table extraction failed: {e}")

            for step in pipeline:
                if step == "analyze":
                    continue  # análisis ya realizado
                if step in [e.value for e in ConversionEngine]:
                    selected_engine = ConversionEngine[step.upper()]
                    logger.info(f"Starting conversion with {selected_engine.value} engine")
                    result = self.engines[selected_engine].convert(
                        pdf_path, output_path, analysis, metadata
                    )

            if result is None:
                # Fallback to engine selection if pipeline did not trigger conversion
                selected_engine = engine or analysis.recommended_engine
                result = self.engines[selected_engine].convert(
                    pdf_path, output_path, analysis, metadata
                )

            if result["success"]:
                logger.info(f"Conversion successful: {output_path}")

                if table_map:
                    with zipfile.ZipFile(output_path, "a") as zf:
                        for page, tables in table_map.items():
                            page_name = f"EPUB/page_{page}.xhtml"
                            if page_name in zf.namelist():
                                html = zf.read(page_name).decode("utf-8")
                                for table_html in tables:
                                    html = html.replace("</body>", f"{table_html}</body>")
                                zf.writestr(page_name, html)
            else:
                logger.error(f"Conversion failed: {result['message']}")

            # Añadir información adicional al resultado
            result["output_path"] = output_path
            result["engine_used"] = selected_engine.value
            result["analysis"] = {
                "page_count": analysis.page_count,
                "file_size": analysis.file_size,
                "content_type": analysis.content_type.value,
                "complexity_score": analysis.complexity_score,
                "issues": analysis.issues,
                "language": analysis.language,
            }
            result["pipeline_used"] = pipeline
            result["pipeline_metrics"] = pipeline_metrics

            return result
            
        except Exception as e:
            logger.error(f"Conversion error: {str(e)}")
            return {
                "success": False,
                "message": f"Unexpected error during conversion: {str(e)}",
                "quality_metrics": {
                    "text_preserved": 0,
                    "images_preserved": 0,
                    "overall": 0
                }
            }

# Función de utilidad para uso desde línea de comandos


def suggest_best_pipeline(pdf_path):
    """Analiza un PDF y sugiere las mejores opciones de conversión."""
    converter = EnhancedPDFToEPUBConverter()
    analysis = converter.analyzer.analyze_pdf(pdf_path)

    time_factors = {
        ConversionEngine.RAPID: 1,
        ConversionEngine.BALANCED: 2,
        ConversionEngine.QUALITY: 3,
    }

    quality_estimates = {
        ConversionEngine.RAPID: 70,
        ConversionEngine.BALANCED: 85,
        ConversionEngine.QUALITY: 95,
    }

    options = []
    for engine in converter.engines:
        options.append({
            "id": engine.value,
            "estimated_time": analysis.page_count * time_factors[engine],
            "estimated_quality": quality_estimates[engine],
        })

    return {
        "recommended": analysis.recommended_engine.value,
        "options": options,
        "analysis": {
            "page_count": analysis.page_count,
            "file_size": analysis.file_size,
            "content_type": analysis.content_type.value,
            "complexity_score": analysis.complexity_score,
            "issues": analysis.issues,
            "language": analysis.language,
        },
    }


def convert_pdf_to_epub(pdf_path, output_path=None, engine_name=None):
    """Función de conveniencia para uso desde CLI"""
    converter = EnhancedPDFToEPUBConverter()
    
    # Seleccionar motor si se especifica
    engine = None
    if engine_name:
        try:
            engine = ConversionEngine[engine_name.upper()]
        except KeyError:
            print(f"Error: Motor de conversión desconocido: {engine_name}")
            print(f"Opciones válidas: {[e.name for e in ConversionEngine]}")
            return
    
    # Ejecutar conversión
    result = converter.convert(pdf_path, output_path, engine)
    
    if result["success"]:
        print(f"Conversión exitosa: {result['output_path']}")
        print(f"Métricas de calidad: {result['quality_metrics']}")
    else:
        print(f"Error en la conversión: {result['message']}")

# Ejecución directa desde línea de comandos
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Convierte PDF a EPUB con análisis inteligente')
    parser.add_argument('pdf_path', help='Ruta al archivo PDF')
    parser.add_argument('--output', '-o', help='Ruta de salida para el EPUB')
    parser.add_argument('--engine', '-e', choices=['rapid', 'balanced', 'quality'], 
                        help='Motor de conversión a utilizar')
    
    args = parser.parse_args()
    convert_pdf_to_epub(args.pdf_path, args.output, args.engine)
