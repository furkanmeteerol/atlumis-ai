from sqlalchemy import select

from app.database.models import Document
from app.services.document import create_document
from app.storage.local import LocalStorage


def test_create_document_success(db_session, tmp_path):
    storage = LocalStorage(base_dir=str(tmp_path))

    document = create_document(
        db=db_session,
        storage=storage,
        filename="example.pdf",
        content_type="application/pdf",
        content=b"%PDF-1.7 example content"
    )

    saved_document = db_session.get(Document, document.id)

    assert saved_document is not None
    assert saved_document.filename == "example.pdf"
    assert saved_document.content_type == "application/pdf"
    assert saved_document.file_size == len(b"%PDF-1.7 example content")
    assert saved_document.status == "uploaded"

    saved_file = tmp_path / document.storage_key

    assert saved_file.exists()
    assert saved_file.read_bytes() == b"%PDF-1.7 example content"


def test_create_document_cleans_up_file_when_database_fails(
    db_session,
    tmp_path,
    monkeypatch
):
    storage = LocalStorage(base_dir=str(tmp_path))

    def failing_commit():
        raise RuntimeError("Simulated database error")

    monkeypatch.setattr(db_session, "commit", failing_commit)

    import pytest

    with pytest.raises(RuntimeError):
        create_document(
            db=db_session,
            storage=storage,
            filename="example.pdf",
            content_type="application/pdf",
            content=b"%PDF-1.7 example content"
        )

    documents = db_session.scalars(
        select(Document)
    ).all()

    assert documents == []

    # Dosya sistemindeki dosya da silinmiş olmalı
    stored_files = list(storage.documents_dir.iterdir())

    assert stored_files == []