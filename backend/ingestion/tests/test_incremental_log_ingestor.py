"""
Tests for incremental log ingestion.
"""

from pathlib import Path

from backend.database.chroma import ChromaDatabase
from backend.ingestion.incremental_log_ingestor import (
    IncrementalLogIngestor,
)


PROJECT_ROOT = Path(__file__).resolve().parents[3]


def test_incremental_ingestion_skips_duplicates(tmp_path):
    """
    Verify that ingesting the same log source twice
    does not create duplicate vectors.
    """

    source_directory = tmp_path / "server-a"
    source_directory.mkdir()

    source_file = source_directory / "auth.log"

    source_file.write_text(
        "Aug 10 10:00:00 test sshd[1234]: "
        "Failed password for invalid user admin "
        "from 192.168.1.10 port 22 ssh2\n"
        "Aug 10 10:01:00 test sshd[1234]: "
        "Accepted password for user admin "
        "from 192.168.1.10 port 22 ssh2\n",
        encoding="utf-8",
    )

    database = ChromaDatabase(
        persist_directory=tmp_path / "chroma",
        collection_name="incremental_test",
    )

    ingestor = IncrementalLogIngestor(
        database=database,
    )

    first_result = ingestor.ingest_source(
        source_id="server-a",
        local_path=source_directory,
    )

    assert first_result["files_discovered"] == 1
    assert first_result["files_processed"] == 1
    assert first_result["records_parsed"] == 2
    assert first_result["new_records"] == 2
    assert first_result["duplicates_skipped"] == 0
    assert first_result["embeddings_created"] == 2
    assert first_result["vectors_stored"] == 2

    assert database.count() == 2

    second_result = ingestor.ingest_source(
        source_id="server-a",
        local_path=source_directory,
    )

    assert second_result["files_discovered"] == 1
    assert second_result["files_processed"] == 1
    assert second_result["records_parsed"] == 2
    assert second_result["new_records"] == 0
    assert second_result["duplicates_skipped"] == 2
    assert second_result["embeddings_created"] == 0
    assert second_result["vectors_stored"] == 0

    assert database.count() == 2

    database.clear()


def test_incremental_ingestion_indexes_new_records(tmp_path):
    """
    Verify that new records are indexed while existing
    records remain unchanged.
    """

    source_directory = tmp_path / "server-a"
    source_directory.mkdir()

    source_file = source_directory / "auth.log"

    source_file.write_text(
        "Aug 10 10:00:00 test sshd[1234]: "
        "Failed password for invalid user admin "
        "from 192.168.1.10 port 22 ssh2\n",
        encoding="utf-8",
    )

    database = ChromaDatabase(
        persist_directory=tmp_path / "chroma",
        collection_name="incremental_new_records_test",
    )

    ingestor = IncrementalLogIngestor(
        database=database,
    )

    first_result = ingestor.ingest_source(
        source_id="server-a",
        local_path=source_directory,
    )

    assert first_result["new_records"] == 1
    assert database.count() == 1

    with source_file.open(
        "a",
        encoding="utf-8",
    ) as file:

        file.write(
            "Aug 10 10:02:00 test sshd[1234]: "
            "Failed password for invalid user root "
            "from 192.168.1.20 port 22 ssh2\n"
        )

    second_result = ingestor.ingest_source(
        source_id="server-a",
        local_path=source_directory,
    )

    assert second_result["records_parsed"] == 2
    assert second_result["new_records"] == 1
    assert second_result["duplicates_skipped"] == 1
    assert second_result["embeddings_created"] == 1
    assert second_result["vectors_stored"] == 1

    assert database.count() == 2

    database.clear()