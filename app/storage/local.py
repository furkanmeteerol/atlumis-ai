from pathlib import Path, PurePosixPath
from uuid import UUID


class LocalStorage:

    def __init__(self, base_dir: str = "data"):
        self.base_dir = Path(base_dir).resolve()
        self.documents_dir = self.base_dir / "documents"

        self.documents_dir.mkdir(
            parents=True,
            exist_ok=True
        )

    def save(
        self,
        document_id: UUID,
        extension: str,
        content: bytes
    ) -> str:

        if extension not in {".pdf", ".txt"}:
            raise ValueError("Unsupported file extension.")

        filename = f"{document_id}{extension}"
        file_path = self.documents_dir / filename

        with open(file_path, "wb") as file:
            file.write(content)

        return f"documents/{filename}"

    def delete(self, storage_key: str) -> None:

        relative_path = PurePosixPath(storage_key)

        if relative_path.is_absolute() or ".." in relative_path.parts:
            raise ValueError("Invalid storage key.")

        file_path = self.base_dir.joinpath(
            *relative_path.parts
        ).resolve()

        try:
            file_path.relative_to(self.base_dir)
        except ValueError as exc:
            raise ValueError("Invalid storage key.") from exc

        if file_path.exists():
            file_path.unlink()