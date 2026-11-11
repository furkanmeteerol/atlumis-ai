import pytest
from pypdf import PdfWriter
from pypdf.errors import PdfReadError
from reportlab.pdfgen import canvas

from app.services.text_extraction import (
    extract_text_from_pdf,
    extract_text_from_txt
)


def test_extract_text_from_txt():
    content = "Hello Atlumis AI! This is a test.".encode("utf-8")

    result = extract_text_from_txt(content)

    assert result == "Hello Atlumis AI! This is a test."


def test_extract_text_from_txt_with_turkish_characters():
    content = "Merhaba! Türkçe karakterler: ğ, ü, ş, ı, ö, ç.".encode("utf-8")

    result = extract_text_from_txt(content)

    assert result == "Merhaba! Türkçe karakterler: ğ, ü, ş, ı, ö, ç."


def test_extract_text_from_txt_invalid_encoding():
    content = b"\xff\xfe\xfa"

    with pytest.raises(UnicodeDecodeError):
        extract_text_from_txt(content)


def test_extract_text_from_empty_pdf():
    writer = PdfWriter()
    writer.add_blank_page(width=300, height=300)

    from io import BytesIO

    pdf_buffer = BytesIO()
    writer.write(pdf_buffer)

    result = extract_text_from_pdf(pdf_buffer.getvalue())

    assert result == ""


def test_extract_text_from_invalid_pdf():
    content = b"This is not a PDF file."

    with pytest.raises(PdfReadError):
        extract_text_from_pdf(content)


def test_extract_text_from_pdf_with_text():
    from io import BytesIO

    pdf_buffer = BytesIO()

    pdf = canvas.Canvas(pdf_buffer)
    pdf.drawString(100, 750, "Hello Atlumis AI!")
    pdf.drawString(100, 730, "This is a PDF extraction test.")
    pdf.save()

    content = pdf_buffer.getvalue()

    result = extract_text_from_pdf(content)

    assert "Hello Atlumis AI!" in result
    assert "This is a PDF extraction test." in result