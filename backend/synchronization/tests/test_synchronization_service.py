"""
Tests for SynchronizationService and synchronization status tracking.
"""

from pathlib import Path
import threading
import time

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


class FakeIngestor:
    """Test double for incremental log ingestion."""

    def __init__(self):
        self.calls = []

    def ingest_source(
        self,
        source_id: str,
        local_path: str,
    ):
        """Record an ingestion request."""
        self.calls.append(
            {
                "source_id": source_id,
                "local_path": local_path,
            }
        )

        return {
            "source_id": source_id,
            "new_records": 1,
            "duplicates_skipped": 0,
            "vectors_stored": 1,
        }


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
        manager=SyncManager(
            executor=executor
        )
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
        manager=SyncManager(
            executor=executor
        )
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


def test_failed_source_does_not_block_other_source():
    """Verify one failed source does not prevent another source from completing."""

    class MultiSourceExecutor:
        """Return different results for different synchronization sources."""

        def __init__(self):
            self.calls = []

        def is_available(self) -> bool:
            """Return rsync availability."""
            return True

        def sync(
            self,
            source: str,
            destination: str | Path,
            options=None,
        ) -> RsyncResult:
            """Return success for one source and failure for another."""

            self.calls.append(source)

            if "192.168.1.20" in source:
                return RsyncResult(
                    success=True,
                    return_code=0,
                    stdout="sync completed",
                    stderr="",
                )

            return RsyncResult(
                success=False,
                return_code=255,
                stdout="",
                stderr="connection refused",
            )

    executor = MultiSourceExecutor()

    service = SynchronizationService(
        manager=SyncManager(
            executor=executor
        )
    )

    successful_source = SyncSource(
        source_id="server-success",
        name="Successful Server",
        host="192.168.1.20",
        username="user",
        remote_path="/var/log/",
        local_path="data/server-success",
    )

    failed_source = SyncSource(
        source_id="server-failed",
        name="Failed Server",
        host="192.168.1.30",
        username="user",
        remote_path="/var/log/",
        local_path="data/server-failed",
    )

    successful_result = service.synchronize(
        successful_source
    )

    failed_result = service.synchronize(
        failed_source
    )

    assert successful_result.success is True
    assert failed_result.success is False

    successful_status = service.get_status(
        "server-success"
    )

    failed_status = service.get_status(
        "server-failed"
    )

    assert successful_status is not None
    assert failed_status is not None

    assert successful_status.status == "success"
    assert failed_status.status == "failed"

    assert successful_status.last_successful_at is not None
    assert failed_status.last_successful_at is None

    assert failed_status.error_message == (
        "connection refused"
    )

    assert len(executor.calls) == 2


def test_scheduled_source_failure_does_not_block_other_source():
    """Verify a scheduled failure does not block another source."""

    import time

    class ScheduledExecutor:
        """Return different results for scheduled sources."""

        def __init__(self):
            self.calls = []

        def is_available(self) -> bool:
            """Return rsync availability."""
            return True

        def sync(
            self,
            source: str,
            destination: str | Path,
            options=None,
        ) -> RsyncResult:
            """Return failure for one source and success for another."""

            self.calls.append(source)

            if "192.168.1.40" in source:
                return RsyncResult(
                    success=False,
                    return_code=255,
                    stdout="",
                    stderr="connection refused",
                )

            return RsyncResult(
                success=True,
                return_code=0,
                stdout="sync completed",
                stderr="",
            )

    executor = ScheduledExecutor()

    service = SynchronizationService(
        manager=SyncManager(
            executor=executor
        )
    )

    failed_source = SyncSource(
        source_id="server-scheduled-failed",
        name="Scheduled Failed Server",
        host="192.168.1.40",
        username="user",
        remote_path="/var/log/",
        local_path="data/server-scheduled-failed",
    )

    successful_source = SyncSource(
        source_id="server-scheduled-success",
        name="Scheduled Successful Server",
        host="192.168.1.50",
        username="user",
        remote_path="/var/log/",
        local_path="data/server-scheduled-success",
    )

    service.run_scheduled_cycle(
        [
            failed_source,
            successful_source,
        ]
    )

    deadline = time.time() + 5

    while time.time() < deadline:
        failed_status = service.get_status(
            "server-scheduled-failed"
        )

        successful_status = service.get_status(
            "server-scheduled-success"
        )

        if (
            failed_status is not None
            and successful_status is not None
            and failed_status.status == "failed"
            and successful_status.status == "success"
        ):
            break

        time.sleep(0.01)

    failed_status = service.get_status(
        "server-scheduled-failed"
    )

    successful_status = service.get_status(
        "server-scheduled-success"
    )

    assert failed_status is not None
    assert successful_status is not None

    assert failed_status.status == "failed"
    assert successful_status.status == "success"

    assert failed_status.error_message == (
        "connection refused"
    )

    assert failed_status.last_successful_at is None
    assert successful_status.last_successful_at is not None

    assert len(executor.calls) == 2


def test_failed_source_can_succeed_on_later_attempt():
    """Verify a failed source can recover on a later synchronization."""

    class RecoveringExecutor:
        """Fail on the first attempt and succeed on the second."""

        def __init__(self):
            self.attempts = 0

        def is_available(self) -> bool:
            """Return rsync availability."""
            return True

        def sync(
            self,
            source: str,
            destination: str | Path,
            options=None,
        ) -> RsyncResult:
            """Return failure first, then success."""

            self.attempts += 1

            if self.attempts == 1:
                return RsyncResult(
                    success=False,
                    return_code=255,
                    stdout="",
                    stderr="connection refused",
                )

            return RsyncResult(
                success=True,
                return_code=0,
                stdout="sync completed",
                stderr="",
            )

    executor = RecoveringExecutor()

    service = SynchronizationService(
        manager=SyncManager(
            executor=executor
        )
    )

    source = SyncSource(
        source_id="server-recovery",
        name="Recovery Server",
        host="192.168.1.60",
        username="user",
        remote_path="/var/log/",
        local_path="data/server-recovery",
    )

    first_result = service.synchronize(source)

    first_status = service.get_status(
        source.source_id
    )

    assert first_result.success is False
    assert first_status is not None
    assert first_status.status == "failed"
    assert first_status.last_successful_at is None

    second_result = service.synchronize(source)

    second_status = service.get_status(
        source.source_id
    )

    assert second_result.success is True
    assert second_status is not None
    assert second_status.status == "success"
    assert second_status.last_successful_at is not None
    assert second_status.error_message is None

    assert executor.attempts == 2


def test_sources_use_independent_sync_intervals():
    """Verify each source maintains its own synchronization schedule."""

    class IntervalExecutor:
        """Record synchronization calls."""

        def __init__(self):
            self.calls = []

        def is_available(self) -> bool:
            """Return rsync availability."""
            return True

        def sync(
            self,
            source: str,
            destination: str | Path,
            options=None,
        ) -> RsyncResult:
            """Record the synchronization request."""

            self.calls.append(source)

            return RsyncResult(
                success=True,
                return_code=0,
                stdout="sync completed",
                stderr="",
            )

    executor = IntervalExecutor()

    service = SynchronizationService(
        manager=SyncManager(
            executor=executor
        ),
        ingestor=FakeIngestor(),

    )

    fast_source = SyncSource(
        source_id="server-fast",
        name="Fast Server",
        host="192.168.1.70",
        username="user",
        remote_path="/var/log/",
        local_path="data/server-fast",
        sync_interval=1,
    )

    slow_source = SyncSource(
        source_id="server-slow",
        name="Slow Server",
        host="192.168.1.80",
        username="user",
        remote_path="/var/log/",
        local_path="data/server-slow",
        sync_interval=10,
    )

    service.run_scheduled_cycle(
        [
            fast_source,
            slow_source,
        ]
    )

    deadline = time.time() + 5

    while time.time() < deadline:
        fast_status = service.get_status(
            "server-fast"
        )

        slow_status = service.get_status(
            "server-slow"
        )

        if (
            fast_status is not None
            and slow_status is not None
            and fast_status.status == "success"
            and slow_status.status == "success"
        ):
            break

        time.sleep(0.01)

    assert service.get_status(
        "server-fast"
    ).status == "success"

    assert service.get_status(
        "server-slow"
    ).status == "success"

    assert service.get_next_sync_in(
        fast_source
    ) <= 1

    assert service.get_next_sync_in(
        slow_source
    ) >= 8

    assert len(executor.calls) == 2


def test_running_source_is_not_scheduled_twice():
    """Verify a source already running is not submitted again."""

    import threading

    class BlockingExecutor:
        """Keep the first synchronization running until released."""

        def __init__(self):
            self.calls = 0
            self.started = threading.Event()
            self.release = threading.Event()

        def is_available(self) -> bool:
            """Return rsync availability."""
            return True

        def sync(
            self,
            source: str,
            destination: str | Path,
            options=None,
        ) -> RsyncResult:
            """Block until the test explicitly releases the job."""

            self.calls += 1
            self.started.set()

            self.release.wait(timeout=5)

            return RsyncResult(
                success=True,
                return_code=0,
                stdout="sync completed",
                stderr="",
            )

    executor = BlockingExecutor()

    service = SynchronizationService(
        manager=SyncManager(
            executor=executor
        )
    )

    source = SyncSource(
        source_id="server-running",
        name="Running Server",
        host="192.168.1.90",
        username="user",
        remote_path="/var/log/",
        local_path="data/server-running",
        sync_interval=1,
    )

    service.run_scheduled_cycle(
        [source]
    )

    assert executor.started.wait(
        timeout=2
    )

    assert service.is_due(source) is False

    service.run_scheduled_cycle(
        [source]
    )

    assert executor.calls == 1

    executor.release.set()

    deadline = time.time() + 5

    while time.time() < deadline:
        status = service.get_status(
            source.source_id
        )

        if (
            status is not None
            and status.status == "success"
        ):
            break

        time.sleep(0.01)

    status = service.get_status(
        source.source_id
    )

    assert status is not None
    assert status.status == "success"
    assert executor.calls == 1


def test_continuous_scheduler_stops_cleanly():
    """Verify the continuous scheduler stops when requested."""

    scheduler_started = threading.Event()
    scheduler_stopped = threading.Event()

    service = SynchronizationService()

    def sources_provider():
        """Provide no sources while testing scheduler shutdown."""

        scheduler_started.set()

        return []

    def run_scheduler():
        """Run the scheduler in a test thread."""

        service.start_continuous_sync(
            sources_provider,
            check_interval=0.01,
        )

        scheduler_stopped.set()

    scheduler_thread = threading.Thread(
        target=run_scheduler,
        daemon=True,
    )

    scheduler_thread.start()

    assert scheduler_started.wait(
        timeout=2
    )

    service.stop_continuous_sync()

    scheduler_thread.join(
        timeout=2
    )

    assert not scheduler_thread.is_alive()
    assert scheduler_stopped.is_set()


def test_scheduler_continues_after_provider_error():
    """Verify a provider error does not terminate the scheduler."""

    scheduler_started = threading.Event()
    provider_failed = threading.Event()

    service = SynchronizationService()

    calls = {"count": 0}

    def sources_provider():
        """Raise once, then continue returning no sources."""

        calls["count"] += 1

        scheduler_started.set()

        if calls["count"] == 1:
            provider_failed.set()

            raise RuntimeError(
                "temporary provider failure"
            )

        return []

    def run_scheduler():
        """Run the scheduler in a test thread."""

        service.start_continuous_sync(
            sources_provider,
            check_interval=0.01,
        )

    scheduler_thread = threading.Thread(
        target=run_scheduler,
        daemon=True,
    )

    scheduler_thread.start()

    assert scheduler_started.wait(
        timeout=2
    )

    assert provider_failed.wait(
        timeout=2
    )

    deadline = time.time() + 2

    while time.time() < deadline:
        if calls["count"] >= 2:
            break

        time.sleep(0.01)

    assert calls["count"] >= 2
    assert scheduler_thread.is_alive()

    service.stop_continuous_sync()

    scheduler_thread.join(
        timeout=2
    )

    assert not scheduler_thread.is_alive()


def test_worker_exception_is_isolated():
    """Verify an unexpected worker exception is recorded as a failure."""

    class ExceptionExecutor:
        """Raise an unexpected exception during synchronization."""

        def is_available(self) -> bool:
            """Return rsync availability."""
            return True

        def sync(
            self,
            source: str,
            destination: str | Path,
            options=None,
        ) -> RsyncResult:
            """Raise an unexpected synchronization exception."""

            raise RuntimeError(
                "unexpected synchronization error"
            )

    executor = ExceptionExecutor()

    service = SynchronizationService(
        manager=SyncManager(
            executor=executor
        )
    )

    source = SyncSource(
        source_id="server-exception",
        name="Exception Server",
        host="192.168.1.100",
        username="user",
        remote_path="/var/log/",
        local_path="data/server-exception",
    )

    service.run_scheduled_cycle(
        [source]
    )

    deadline = time.time() + 5

    while time.time() < deadline:
        status = service.get_status(
            source.source_id
        )

        if (
            status is not None
            and status.status == "failed"
        ):
            break

        time.sleep(0.01)

    status = service.get_status(
        source.source_id
    )

    assert status is not None
    assert status.status == "failed"
    assert status.error_message == (
        "unexpected synchronization error"
    )
    assert status.last_attempted_at is not None
    assert status.last_successful_at is None


def test_status_is_serializable():
    """Verify synchronization status can be converted to a dictionary."""

    status = SyncStatus(
        source_id="server-test"
    )

    status.mark_running()
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
        manager=SyncManager(
            executor=executor
        )
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
        manager=SyncManager(
            executor=executor
        )
    )

    assert service.info()["tracked_sources"] == 0

    service.synchronize(create_source())

    assert service.info()["tracked_sources"] == 1

def test_successful_sync_triggers_incremental_ingestion():
    """Verify successful rsync triggers incremental log ingestion."""

    executor = FakeExecutor(
        RsyncResult(
            success=True,
            return_code=0,
            stdout="sync completed",
            stderr="",
        )
    )

    ingestor = FakeIngestor()

    service = SynchronizationService(
        manager=SyncManager(
            executor=executor
        ),
        ingestor=ingestor,
    )

    source = create_source()

    result = service.synchronize(source)

    assert result.success is True

    assert len(ingestor.calls) == 1

    assert ingestor.calls[0]["source_id"] == (
        source.source_id
    )

    assert ingestor.calls[0]["local_path"] == (
        source.local_path
    )


def test_failed_sync_does_not_trigger_incremental_ingestion():
    """Verify failed rsync does not trigger log ingestion."""

    executor = FakeExecutor(
        RsyncResult(
            success=False,
            return_code=255,
            stdout="",
            stderr="connection refused",
        )
    )

    ingestor = FakeIngestor()

    service = SynchronizationService(
        manager=SyncManager(
            executor=executor
        ),
        ingestor=ingestor,
    )

    source = create_source()

    result = service.synchronize(source)

    assert result.success is False

    assert len(ingestor.calls) == 0


def test_ingestion_failure_does_not_fail_successful_sync():
    """Verify ingestion failure does not change a successful rsync result."""

    class FailingIngestor:
        """Test double that raises during incremental ingestion."""

        def ingest_source(
            self,
            source_id: str,
            local_path: str,
        ):
            """Raise an ingestion error."""
            raise RuntimeError(
                "incremental ingestion failed"
            )

    executor = FakeExecutor(
        RsyncResult(
            success=True,
            return_code=0,
            stdout="sync completed",
            stderr="",
        )
    )

    service = SynchronizationService(
        manager=SyncManager(
            executor=executor
        ),
        ingestor=FailingIngestor(),
    )

    source = create_source()

    result = service.synchronize(source)

    assert result.success is True
    assert result.return_code == 0

    status = service.get_status(
        source.source_id
    )

    assert status is not None
    assert status.status == "success"
    assert status.error_message is None