from pathlib import Path


MAX_FILE_SIZE = 10 * 1024 * 1024

ALLOWED_TYPES = {
    ".pdf": "application/pdf",
    ".txt": "text/plain"
}


class DocumentValidationError(Exception):
    pass


def validate_document(
    filename: str,
    content_type: str | None,
    content: bytes
) -> None:

    extension = Path(filename).suffix.lower()

    if extension not in ALLOWED_TYPES:
        raise DocumentValidationError(
            "Only PDF and TXT files are allowed."
        )

    if content_type != ALLOWED_TYPES[extension]:
        raise DocumentValidationError(
            "Invalid file content type."
        )

    if not content:
        raise DocumentValidationError(
            "File is empty."
        )

    if len(content) > MAX_FILE_SIZE:
        raise DocumentValidationError(
            "File size exceeds the 10 MB limit."
        )

    if extension == ".pdf":
        if not content.startswith(b"%PDF-"):
            raise DocumentValidationError(
                "File content is not a valid PDF."
            )

    elif extension == ".txt":
        try:
            content.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise DocumentValidationError(
                "TXT file must use UTF-8 encoding."
            ) from exc