"""
Tests for SyncSource and SyncManager.
"""

import pytest

from backend.synchronization.models.sync_source import SyncSource
from backend.synchronization.rsync_executor import RsyncResult
from backend.synchronization.sync_manager import SyncManager


class FakeExecutor:
    """Test double for RsyncExecutor."""

    def __init__(self, available=True):
        self.available = available
        self.calls = []

    def is_available(self):
        return self.available

    def sync(self, source, destination, options=None):
        self.calls.append(
            {
                "source": source,
                "destination": destination,
                "options": options,
            }
        )

        return RsyncResult(
            success=True,
            return_code=0,
            stdout="sync completed",
            stderr="",
        )


def create_source(enabled=True):
    """Create a valid synchronization source."""
    return SyncSource(
        source_id="server-test",
        name="Test Server",
        host="192.168.1.10",
        username="user",
        remote_path="/var/log/",
        local_path="data/server-test",
        enabled=enabled,
    )


def test_sync_source_rsync_source():
    """Verify rsync source formatting."""

    source = create_source()

    assert source.rsync_source == (
        "user@192.168.1.10:/var/log/"
    )


def test_sync_source_to_dict():
    """Verify source serialization."""

    source = create_source()

    result = source.to_dict()

    assert result["source_id"] == "server-test"
    assert result["name"] == "Test Server"
    assert result["host"] == "192.168.1.10"
    assert result["username"] == "user"
    assert result["remote_path"] == "/var/log/"
    assert result["local_path"] == "data/server-test"
    assert result["enabled"] is True


def test_sync_source_rejects_invalid_values():
    """Verify required string fields are validated."""

    with pytest.raises(ValueError):
        SyncSource(
            source_id="",
            name="Test Server",
            host="192.168.1.10",
            username="user",
            remote_path="/var/log/",
            local_path="data/server-test",
        )


def test_sync_source_rejects_invalid_enabled_value():
    """Verify enabled must be boolean."""

    with pytest.raises(TypeError):
        SyncSource(
            source_id="server-test",
            name="Test Server",
            host="192.168.1.10",
            username="user",
            remote_path="/var/log/",
            local_path="data/server-test",
            enabled="yes",
        )


def test_sync_manager_syncs_enabled_source(tmp_path):
    """Verify enabled sources are synchronized."""

    executor = FakeExecutor()
    manager = SyncManager(executor=executor)

    source = create_source()

    source.local_path = str(
        tmp_path / "server-test"
    )

    result = manager.sync_source(source)

    assert result.success is True
    assert result.return_code == 0

    assert len(executor.calls) == 1

    call = executor.calls[0]

    assert call["source"] == (
        "user@192.168.1.10:/var/log/"
    )

    assert call["destination"] == (
        tmp_path / "server-test"
    )


def test_sync_manager_skips_disabled_source(tmp_path):
    """Verify disabled sources are not synchronized."""

    executor = FakeExecutor()
    manager = SyncManager(executor=executor)

    source = create_source(enabled=False)

    source.local_path = str(
        tmp_path / "server-test"
    )

    result = manager.sync_source(source)

    assert result.success is False
    assert result.return_code == -2
    assert executor.calls == []


def test_sync_manager_rejects_invalid_source():
    """Verify source type validation."""

    manager = SyncManager(
        executor=FakeExecutor()
    )

    with pytest.raises(TypeError):
        manager.sync_source(
            "invalid-source"
        )


def test_sync_manager_reports_rsync_availability():
    """Verify rsync availability is exposed."""

    available_manager = SyncManager(
        executor=FakeExecutor(
            available=True
        )
    )

    unavailable_manager = SyncManager(
        executor=FakeExecutor(
            available=False
        )
    )

    assert available_manager.is_available() is True
    assert unavailable_manager.is_available() is False


def test_sync_manager_info():
    """Verify manager metadata."""

    manager = SyncManager(
        executor=FakeExecutor(
            available=True
        )
    )

    info = manager.info()

    assert info["component"] == "SyncManager"
    assert info["rsync_available"] is True