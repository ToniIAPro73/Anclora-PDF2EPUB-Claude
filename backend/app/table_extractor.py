from typing import List, Dict, Any


def extract_tables(pdf_path: str, output: str = "html") -> List[Dict[str, Any]]:
    """Extract tables from a PDF file.

    Args:
        pdf_path: Path to the PDF file.
        output: "html" to return HTML strings, "dataframe" for pandas DataFrame objects.

    Returns:
        List of dictionaries with page number and table content in the requested format.
    """
    import camelot

    tables = camelot.read_pdf(pdf_path, pages="all")
    extracted = []
    for table in tables:
        content = table.df if output == "dataframe" else table.df.to_html(index=False)
        extracted.append({"page": int(table.page), "content": content})
    return extracted
