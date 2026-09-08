"""
Tests for SynchronizationService and synchronization status tracking.
"""

from pathlib import Path

from backend.synchronization.models.sync_source import SyncSource
from backend.synchronization.models.sync_status import SyncStatus
from backend.synchronization.rsync_executor import RsyncResult
from backend.synchronization.synchronization_service import (
    SynchronizationService,
)
from backend.synchronization.sync_manager import SyncManager


class FakeExecutor:
    """Test double for the rsync executor."""

    def __init__(self, result: RsyncResult):
        self.result = result

    def is_available(self) -> bool:
        """Return rsync availability."""
        return True

    def sync(
        self,
        source: str,
        destination: str | Path,
        options=None,
    ) -> RsyncResult:
        """Return the predefined synchronization result."""
        return self.result


def create_source() -> SyncSource:
    """Create a valid synchronization source."""
    return SyncSource(
        source_id="server-test",
        name="Test Server",
        host="192.168.1.10",
        username="user",
        remote_path="/var/log/",
        local_path="data/server-test",
    )


def test_successful_sync_updates_status():
    """Verify successful synchronization updates status."""

    executor = FakeExecutor(
        RsyncResult(
            success=True,
            return_code=0,
            stdout="sync completed",
            stderr="",
        )
    )

    service = SynchronizationService(
        manager=SyncManager(executor=executor)
    )

    source = create_source()

    result = service.synchronize(source)

    assert result.success is True

    status = service.get_status(
        source.source_id
    )

    assert status is not None
    assert status.status == "success"
    assert status.last_attempted_at is not None
    assert status.last_successful_at is not None
    assert status.error_message is None


def test_failed_sync_updates_status():
    """Verify failed synchronization updates status."""

    executor = FakeExecutor(
        RsyncResult(
            success=False,
            return_code=255,
            stdout="",
            stderr="connection refused",
        )
    )

    service = SynchronizationService(
        manager=SyncManager(executor=executor)
    )

    source = create_source()

    result = service.synchronize(source)

    assert result.success is False

    status = service.get_status(
        source.source_id
    )

    assert status is not None
    assert status.status == "failed"
    assert status.last_attempted_at is not None
    assert status.last_successful_at is None
    assert status.error_message == "connection refused"


def test_status_is_serializable():
    """Verify synchronization status can be converted to a dictionary."""

    status = SyncStatus(
        source_id="server-test"
    )

    status.mark_success()

    result = status.to_dict()

    assert result["source_id"] == "server-test"
    assert result["status"] == "success"
    assert result["last_attempted_at"] is not None
    assert result["last_successful_at"] is not None
    assert result["error_message"] is None


def test_all_statuses_returns_tracked_sources():
    """Verify all tracked source statuses are returned."""

    executor = FakeExecutor(
        RsyncResult(
            success=True,
            return_code=0,
            stdout="sync completed",
            stderr="",
        )
    )

    service = SynchronizationService(
        manager=SyncManager(executor=executor)
    )

    source = create_source()

    service.synchronize(source)

    statuses = service.get_all_statuses()

    assert "server-test" in statuses
    assert statuses["server-test"]["status"] == "success"


def test_unknown_source_has_no_status():
    """Verify unknown sources return no status."""

    service = SynchronizationService()

    assert service.get_status(
        "unknown-source"
    ) is None


def test_info_reports_tracked_source_count():
    """Verify service metadata reports tracked sources."""

    executor = FakeExecutor(
        RsyncResult(
            success=True,
            return_code=0,
            stdout="sync completed",
            stderr="",
        )
    )

    service = SynchronizationService(
        manager=SyncManager(executor=executor)
    )

    assert service.info()["tracked_sources"] == 0

    service.synchronize(create_source())

    assert service.info()["tracked_sources"] == 1