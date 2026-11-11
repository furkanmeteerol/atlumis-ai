from io import BytesIO

from pypdf import PdfReader


def extract_text_from_pdf(content: bytes) -> str:
    pdf_file = BytesIO(content)
    reader = PdfReader(pdf_file)

    extracted_pages = []

    for page in reader.pages:
        page_text = page.extract_text() or ""
        extracted_pages.append(page_text)

    return "\n\n".join(extracted_pages)


def extract_text_from_txt(content: bytes) -> str:
    return content.decode("utf-8")