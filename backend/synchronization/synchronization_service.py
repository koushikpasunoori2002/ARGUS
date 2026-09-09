"""
High-level synchronization service.
"""

from __future__ import annotations

import logging
import threading
import time
from concurrent.futures import ThreadPoolExecutor

from .models.sync_source import SyncSource
from .models.sync_status import SyncStatus
from .rsync_executor import RsyncResult
from .sync_manager import SyncManager


logger = logging.getLogger(__name__)


class SynchronizationService:
    """
    Provides application-level synchronization operations,
    maintains synchronization status, and supports independent
    per-server scheduling.
    """

    def __init__(
        self,
        manager: SyncManager | None = None,
    ) -> None:
        self.manager = manager or SyncManager()

        self._statuses: dict[str, SyncStatus] = {}

        # The next scheduled time for each server.
        # This keeps every server on its own independent schedule.
        self._next_sync_times: dict[str, float] = {}

        # Servers currently executing an rsync operation.
        self._running_sources: set[str] = set()

        self._state_lock = threading.Lock()

        # Independent synchronization jobs can run concurrently.
        self._executor = ThreadPoolExecutor(
            max_workers=10,
            thread_name_prefix="LogLlamalyzer-Rsync",
        )

        # Used to stop the scheduler.
        self._stop_event = threading.Event()

    def synchronize(
        self,
        source: SyncSource,
    ) -> RsyncResult:
        """
        Synchronize one configured source and update its status.

        The next scheduled execution time is calculated from the
        time at which this scheduling cycle started, rather than
        from the completion time of the rsync process.
        """

        if not isinstance(source, SyncSource):
            raise TypeError(
                "source must be a SyncSource instance."
            )

        status = self._statuses.setdefault(
            source.source_id,
            SyncStatus(source.source_id),
        )

        logger.info(
            "Synchronization starting: %s "
            "(interval=%ss)",
            source.source_id,
            source.sync_interval,
        )

        result = self.manager.sync_source(source)

        if result.success:

            status.mark_success()

            logger.info(
                "Synchronization succeeded: %s "
                "(interval=%ss)",
                source.source_id,
                source.sync_interval,
            )

        else:

            error_message = result.stderr

            if not error_message:
                error_message = (
                    "Synchronization failed."
                )

            status.mark_failure(
                error_message
            )

            logger.error(
                "Synchronization failed: %s "
                "(return_code=%s, error=%s)",
                source.source_id,
                result.return_code,
                error_message.strip(),
            )

        return result

    def _run_source_in_background(
        self,
        source: SyncSource,
    ) -> RsyncResult:
        """
        Execute one synchronization job in a worker thread.
        """

        try:

            return self.synchronize(source)

        except Exception as exc:

            logger.exception(
                "Unexpected synchronization error: %s",
                source.source_id,
            )

            status = self._statuses.setdefault(
                source.source_id,
                SyncStatus(source.source_id),
            )

            status.mark_failure(
                str(exc)
            )

            return RsyncResult(
                success=False,
                return_code=-4,
                stdout="",
                stderr=str(exc),
            )

        finally:

            with self._state_lock:
                self._running_sources.discard(
                    source.source_id
                )

    def _schedule_source(
        self,
        source: SyncSource,
        scheduled_time: float,
    ) -> bool:
        """
        Submit one server for independent synchronization.

        The next execution time is based on the scheduled time,
        not on rsync completion time.
        """

        if not source.enabled:
            return False

        with self._state_lock:

            if source.source_id in self._running_sources:

                logger.debug(
                    "Synchronization already running: %s",
                    source.source_id,
                )

                return False

            self._running_sources.add(
                source.source_id
            )

            # Maintain the source's own schedule.
            next_time = (
                scheduled_time
                + source.sync_interval
            )

            self._next_sync_times[
                source.source_id
            ] = next_time

        try:

            self._executor.submit(
                self._run_source_in_background,
                source,
            )

            logger.info(
                "Synchronization job submitted: %s "
                "(interval=%ss, next_sync_in=%ss)",
                source.source_id,
                source.sync_interval,
                source.sync_interval,
            )

            return True

        except Exception as exc:

            with self._state_lock:

                self._running_sources.discard(
                    source.source_id
                )

                logger.exception(
                    "Unable to submit synchronization job: %s",
                    source.source_id,
                )

            return False

    def synchronize_local_source(
        self,
        source_path: str,
        destination_path: str,
    ) -> RsyncResult:
        """
        Synchronize a local directory while tracking its status.
        """

        source_id = "local-test"

        status = self._statuses.setdefault(
            source_id,
            SyncStatus(source_id),
        )

        logger.info(
            "Local synchronization starting: %s -> %s",
            source_path,
            destination_path,
        )

        result = self.manager.executor.sync(
            source=source_path,
            destination=destination_path,
        )

        if result.success:

            status.mark_success()

            logger.info(
                "Local synchronization succeeded: %s -> %s",
                source_path,
                destination_path,
            )

        else:

            error_message = (
                result.stderr
                or "Synchronization failed."
            )

            status.mark_failure(
                error_message
            )

            logger.error(
                "Local synchronization failed: %s",
                error_message.strip(),
            )

        return result

    def is_due(
        self,
        source: SyncSource,
    ) -> bool:
        """
        Determine whether a source is due for synchronization.
        """

        if not isinstance(source, SyncSource):
            raise TypeError(
                "source must be a SyncSource instance."
            )

        if not source.enabled:
            return False

        with self._state_lock:

            if source.source_id in self._running_sources:
                return False

            next_sync = self._next_sync_times.get(
                source.source_id
            )

        # A source with no schedule has never been
        # scheduled and is therefore immediately due.
        if next_sync is None:
            return True

        return time.monotonic() >= next_sync

    def run_scheduled_cycle(
        self,
        sources: list[SyncSource],
    ) -> dict[str, RsyncResult]:
        """
        Submit every source that is currently due.

        Each source maintains its own independent schedule.
        """

        if not isinstance(sources, list):
            raise TypeError(
                "sources must be a list."
            )

        results: dict[str, RsyncResult] = {}

        current_time = time.monotonic()

        for source in sources:

            if not isinstance(source, SyncSource):
                raise TypeError(
                    "Every item in sources must be "
                    "a SyncSource instance."
                )

            if not source.enabled:
                continue

            if self.is_due(source):

                logger.info(
                    "Server is due for synchronization: "
                    "%s (interval=%ss)",
                    source.source_id,
                    source.sync_interval,
                )

                submitted = self._schedule_source(
                    source,
                    current_time,
                )

                if submitted:
                    logger.info(
                        "Independent synchronization started: "
                        "%s",
                        source.source_id,
                    )

        return results

    def start_continuous_sync(
        self,
        sources_provider,
        check_interval: float = 1.0,
    ) -> None:
        """
        Continuously check configured sources and submit each
        server independently when its own interval expires.

        The scheduler checks every check_interval seconds, while
        each server follows its individual sync_interval.
        """

        if not callable(sources_provider):
            raise TypeError(
                "sources_provider must be callable."
            )

        if (
            not isinstance(check_interval, (int, float))
            or isinstance(check_interval, bool)
            or check_interval <= 0
        ):
            raise ValueError(
                "check_interval must be greater than 0."
            )

        self._stop_event.clear()

        logger.info(
            "Continuous synchronization scheduler started "
            "(check_interval=%ss)",
            check_interval,
        )

        while not self._stop_event.is_set():

            try:

                sources = sources_provider()

                logger.debug(
                    "Scheduler cycle checking %s sources.",
                    len(sources),
                )

                self.run_scheduled_cycle(
                    sources
                )

            except Exception:

                logger.exception(
                    "Unexpected error during "
                    "synchronization scheduler cycle."
                )

            self._stop_event.wait(
                check_interval
            )

        logger.info(
            "Continuous synchronization scheduler stopped."
        )

    def stop_continuous_sync(self) -> None:
        """
        Stop the continuous synchronization scheduler.
        """

        logger.info(
            "Stopping continuous synchronization scheduler."
        )

        self._stop_event.set()

        self._executor.shutdown(
            wait=False,
            cancel_futures=True,
        )

        logger.info(
            "Synchronization worker pool stopped."
        )

    def get_next_sync_in(
        self,
        source: SyncSource,
    ) -> int | None:
        """
        Return the approximate number of seconds until
        the source is next due.

        Returns None for disabled sources.
        """

        if not isinstance(source, SyncSource):
            raise TypeError(
                "source must be a SyncSource instance."
            )

        if not source.enabled:
            return None

        with self._state_lock:

            if source.source_id in self._running_sources:
                return 0

            next_sync = self._next_sync_times.get(
                source.source_id
            )

        if next_sync is None:
            return 0

        remaining = (
            next_sync - time.monotonic()
        )

        return max(
            0,
            int(remaining)
        )

    def get_status(
        self,
        source_id: str,
    ) -> SyncStatus | None:
        """
        Return the current status for one source.
        """

        return self._statuses.get(source_id)

    def get_all_statuses(self) -> dict[str, dict]:
        """
        Return all tracked synchronization statuses.
        """

        return {
            source_id: status.to_dict()
            for source_id, status in self._statuses.items()
        }

    def is_available(self) -> bool:
        """
        Return whether rsync is available.
        """

        return self.manager.is_available()

    def info(self) -> dict:
        """
        Return service metadata.
        """

        with self._state_lock:
            running_sources = len(
                self._running_sources
            )

        return {
            "component": "SynchronizationService",
            "rsync_available": self.is_available(),
            "tracked_sources": len(self._statuses),
            "running_sources": running_sources,
        }