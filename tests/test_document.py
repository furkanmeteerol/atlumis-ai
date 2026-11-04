import pytest

from app.services.document import (
    validate_document,
    DocumentValidationError,
    MAX_FILE_SIZE
)


def test_validate_valid_pdf():
    validate_document(
        filename="report.pdf",
        content_type="application/pdf",
        content=b"%PDF-1.7 example content"
    )


def test_validate_valid_txt():
    validate_document(
        filename="report.txt",
        content_type="text/plain",
        content=b"Hello, this is a valid text file."
    )


def test_reject_unsupported_extension():
    with pytest.raises(DocumentValidationError):
        validate_document(
            filename="image.png",
            content_type="image/png",
            content=b"image content"
        )


def test_reject_invalid_content_type():
    with pytest.raises(DocumentValidationError):
        validate_document(
            filename="report.pdf",
            content_type="text/plain",
            content=b"%PDF-1.7 example content"
        )


def test_reject_empty_file():
    with pytest.raises(DocumentValidationError):
        validate_document(
            filename="report.txt",
            content_type="text/plain",
            content=b""
        )


def test_reject_file_over_size_limit():
    with pytest.raises(DocumentValidationError):
        validate_document(
            filename="report.txt",
            content_type="text/plain",
            content=b"A" * (MAX_FILE_SIZE + 1)
        )


def test_reject_invalid_pdf_content():
    with pytest.raises(DocumentValidationError):
        validate_document(
            filename="report.pdf",
            content_type="application/pdf",
            content=b"This is not a PDF file."
        )


def test_reject_invalid_utf8_txt():
    with pytest.raises(DocumentValidationError):
        validate_document(
            filename="report.txt",
            content_type="text/plain",
            content=b"\xff\xfe\xfa"
        )