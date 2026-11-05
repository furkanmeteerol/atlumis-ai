import logging
from pathlib import Path
from uuid import uuid4

from sqlalchemy.orm import Session

from app.database.models import Document
from app.storage.local import LocalStorage


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

def create_document(
    db: Session,
    storage: LocalStorage,
    filename: str,
    content_type: str | None,
    content: bytes
    ) -> Document:

    validate_document(
        filename=filename,
        content_type=content_type,
        content=content
    )

    document_id = uuid4()
    extension = Path(filename).suffix.lower()

    storage_key = storage.save(
        document_id=document_id,
        extension=extension,
        content=content
    )

    document = Document(
        id=document_id,
        filename=filename,
        storage_key=storage_key,
        content_type=content_type,
        file_size=len(content),
        status="uploaded"
    )

    try:
        db.add(document)
        db.commit()

        return document

    except Exception:
        db.rollback()

        try:
            storage.delete(storage_key)
        except Exception:
            logging.exception(
                "Failed to delete stored file after database error: %s",
                storage_key
            )

        raise