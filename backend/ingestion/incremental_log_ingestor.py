"""
Incremental log ingestion.

Processes synchronized log files, detects already indexed
records, and stores only new log embeddings in ChromaDB.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

from backend.database.chroma import ChromaDatabase
from backend.llm.embeddings import EmbeddingManager
from backend.preprocessing.pipeline import PreprocessingPipeline
from backend.rag.chunking import ChunkManager


class IncrementalLogIngestor:
    """
    Incrementally ingest synchronized log files into ChromaDB.
    """

    def __init__(
        self,
        database=None,
        embedding_manager=None,
        preprocessing_pipeline=None,
    ):
        self.database = (
            database
            if database is not None
            else ChromaDatabase()
        )

        self.embedding_manager = (
            embedding_manager
            or EmbeddingManager()
        )

        self.preprocessing_pipeline = (
            preprocessing_pipeline
            or PreprocessingPipeline()
        )

    # ----------------------------------------------------------
    # Public API
    # ----------------------------------------------------------

    def ingest_source(
        self,
        source_id: str,
        local_path: str | Path,
    ) -> dict:
        """
        Incrementally ingest supported log files from a source.
        """

        if not isinstance(source_id, str) or not source_id.strip():
            raise ValueError(
                "source_id must be a non-empty string."
            )

        path = Path(local_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Log source path does not exist: {path}"
            )

        if not path.is_dir():
            raise ValueError(
                f"Log source path must be a directory: {path}"
            )

        files = self._discover_files(path)

        records_parsed = 0
        new_records = []
        new_record_ids = set()
        duplicate_records = 0
        files_processed = 0

        for file_path in files:

            try:
                _, records = (
                    self.preprocessing_pipeline
                    .process_with_metadata(file_path)
                )

            except ValueError:
                # Unsupported or unknown log types are ignored.
                continue

            files_processed += 1
            records_parsed += len(records)

            for record in records:

                record_id = self._record_id(
                    source_id=source_id,
                    record=record,
                )

                existing = self.database.get(
                    ids=[record_id]
                )

                if existing.get("ids") or record_id in new_record_ids:
                    duplicate_records += 1
                    continue

                new_record_ids.add(record_id)

                chunk_manager = ChunkManager(
                    chunk_size=500,
                    overlap=50,
                )

                chunks = chunk_manager.add_record(
                    record=record,
                    source=str(file_path),
                )

                for chunk in chunks:
                    chunk.chunk_id = record_id

                new_records.extend(chunks)

        if new_records:

            embeddings = (
                self.embedding_manager.embed_chunks(
                    new_records
                )
            )

            ids = [
                chunk.chunk_id
                for chunk in new_records
            ]

            documents = [
                chunk.text
                for chunk in new_records
            ]

            metadatas = []

            for chunk in new_records:

                metadata = {
                    **chunk.metadata,
                    "chunk_id": chunk.chunk_id,
                    "source": chunk.source,
                    "source_id": source_id,
                }

                metadata = {
                    key: value
                    for key, value in metadata.items()
                    if value is not None
                }

                metadatas.append(metadata)

            batch_size = 5000

            for start in range(0, len(ids), batch_size):
                end = start + batch_size

                self.database.add(
                    ids=ids[start:end],
                    embeddings=embeddings[start:end],
                    documents=documents[start:end],
                    metadatas=metadatas[start:end],
                )

        return {
            "source_id": source_id,
            "path": str(path),
            "files_discovered": len(files),
            "files_processed": files_processed,
            "records_parsed": records_parsed,
            "new_records": len(new_records),
            "duplicates_skipped": duplicate_records,
            "embeddings_created": len(new_records),
            "vectors_stored": len(new_records),
        }

    # ----------------------------------------------------------
    # File discovery
    # ----------------------------------------------------------

    def _discover_files(
        self,
        path: Path,
    ) -> list[Path]:
        """
        Discover supported log files recursively.
        """

        supported_prefixes = (
            "auth",
            "syslog",
            "kern",
            "dpkg",
            "dmesg",
            "apache",
            "nginx",
            "docker",
            "apport",
        )

        files = []

        for file_path in path.rglob("*"):

            if not file_path.is_file():
                continue

            filename = file_path.name.lower()

            if filename.startswith(
                supported_prefixes
            ):
                files.append(file_path)

        return sorted(files)

    # ----------------------------------------------------------
    # Stable ID generation
    # ----------------------------------------------------------

    def _record_id(
        self,
        source_id: str,
        record,
    ) -> str:
        """
        Generate a deterministic ID for a log record.
        """

        values = [
            source_id,
            getattr(record, "source_file", ""),
            getattr(record, "log_type", ""),
            getattr(record, "timestamp", ""),
            getattr(record, "hostname", ""),
            getattr(record, "process", ""),
            str(getattr(record, "pid", "")),
            getattr(record, "message", ""),
        ]

        canonical = "|".join(
            str(value)
            for value in values
        )

        digest = hashlib.sha256(
            canonical.encode("utf-8")
        ).hexdigest()

        return f"log_{digest}"

    # ----------------------------------------------------------
    # Information
    # ----------------------------------------------------------

    def info(self) -> dict:
        """
        Return ingestion component metadata.
        """

        return {
            "component": "IncrementalLogIngestor",
            "database": "ChromaDB",
            "embedding_manager": (
                self.embedding_manager.model_information()
            ),
            "duplicate_detection": "stable record hash",
        }