"""
Tests for RsyncExecutor.
"""

from pathlib import Path

import pytest

from backend.synchronization.rsync_executor import RsyncExecutor


@pytest.fixture
def executor():
    """Create an RsyncExecutor instance."""
    return RsyncExecutor()


def test_rsync_is_available(executor):
    """Verify that rsync is available through WSL."""
    assert executor.is_available() is True


def test_rsync_local_directory_sync(executor, tmp_path):
    """
    Verify that the contents of a local source directory
    are copied into the destination directory.
    """

    source = tmp_path / "source"
    destination = tmp_path / "destination"

    source.mkdir()

    test_file = source / "test.log"
    test_file.write_text(
        "Automated rsync test\n",
        encoding="utf-8",
    )

    result = executor.sync(
        source=str(source) + "/",
        destination=str(destination),
    )

    assert result.success is True
    assert result.return_code == 0

    copied_file = destination / "test.log"

    assert copied_file.exists()
    assert copied_file.read_text(
        encoding="utf-8"
    ) == "Automated rsync test\n"


def test_empty_source_raises_error(executor, tmp_path):
    """Verify that an empty source is rejected."""

    destination = tmp_path / "destination"

    with pytest.raises(ValueError):
        executor.sync(
            source="",
            destination=destination,
        )


def test_destination_is_created(executor, tmp_path):
    """
    Verify that a missing destination directory is created
    and populated with the source contents.
    """

    source = tmp_path / "source"
    destination = (
        tmp_path
        / "nested"
        / "destination"
    )

    source.mkdir()

    test_file = source / "example.log"
    test_file.write_text(
        "Destination creation test\n",
        encoding="utf-8",
    )

    result = executor.sync(
        source=str(source) + "/",
        destination=destination,
    )

    assert result.success is True
    assert result.return_code == 0
    assert destination.exists()

    copied_file = destination / "example.log"

    assert copied_file.exists()
    assert copied_file.read_text(
        encoding="utf-8"
    ) == "Destination creation test\n"