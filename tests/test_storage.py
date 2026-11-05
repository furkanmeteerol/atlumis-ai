from uuid import uuid4

import pytest

from app.storage.local import LocalStorage


def test_save_file(tmp_path):
    storage = LocalStorage(base_dir=str(tmp_path))
    document_id = uuid4()
    content = b"%PDF-1.7 example content"

    storage_key = storage.save(
        document_id=document_id,
        extension=".pdf",
        content=content
    )

    expected_key = f"documents/{document_id}.pdf"

    assert storage_key == expected_key

    saved_file = tmp_path / expected_key

    assert saved_file.exists()
    assert saved_file.read_bytes() == content


def test_save_creates_documents_directory(tmp_path):
    storage = LocalStorage(base_dir=str(tmp_path))

    assert storage.documents_dir.exists()
    assert storage.documents_dir.is_dir()


def test_delete_file(tmp_path):
    storage = LocalStorage(base_dir=str(tmp_path))
    document_id = uuid4()

    storage_key = storage.save(
        document_id=document_id,
        extension=".txt",
        content=b"Hello Atlumis AI!"
    )

    storage.delete(storage_key)

    saved_file = tmp_path / storage_key

    assert not saved_file.exists()


def test_delete_nonexistent_file(tmp_path):
    storage = LocalStorage(base_dir=str(tmp_path))

    storage.delete("documents/nonexistent.txt")


def test_save_rejects_unsupported_extension(tmp_path):
    storage = LocalStorage(base_dir=str(tmp_path))

    with pytest.raises(ValueError):
        storage.save(
            document_id=uuid4(),
            extension=".exe",
            content=b"executable content"
        )


@pytest.mark.parametrize(
    "storage_key",
    [
        "../secret.txt",
        "documents/../../secret.txt",
        "/etc/passwd",
        "C:\\Windows\\system.ini"
    ]
)
def test_delete_rejects_unsafe_storage_key(tmp_path, storage_key):
    storage = LocalStorage(base_dir=str(tmp_path))

    with pytest.raises(ValueError):
        storage.delete(storage_key)