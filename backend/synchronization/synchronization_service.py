"""
High-level synchronization service.
"""

from __future__ import annotations

from datetime import datetime

from .models.sync_source import SyncSource
from .models.sync_status import SyncStatus
from .rsync_executor import RsyncResult
from .sync_manager import SyncManager


class SynchronizationService:
    """
    Provides application-level synchronization operations
    and maintains synchronization status for each source.
    """

    def __init__(
        self,
        manager: SyncManager | None = None,
    ) -> None:
        self.manager = manager or SyncManager()
        self._statuses: dict[str, SyncStatus] = {}

    def synchronize(
        self,
        source: SyncSource,
    ) -> RsyncResult:
        """
        Synchronize one configured source and update its status.
        """

        if not isinstance(source, SyncSource):
            raise TypeError(
                "source must be a SyncSource instance."
            )

        status = self._statuses.setdefault(
            source.source_id,
            SyncStatus(source.source_id),
        )

        result = self.manager.sync_source(source)

        if result.success:
            status.mark_success()
        else:
            error_message = result.stderr

            if not error_message:
                error_message = (
                    "Synchronization failed."
                )

            status.mark_failure(
                error_message
            )

        return result

    def synchronize_local_source(
        self,
        source_path: str,
        destination_path: str,
) ->     RsyncResult:
        """
        Synchronize a local directory while tracking its status.
        """

        source_id = "local-test"

        status = self._statuses.setdefault(
            source_id,
            SyncStatus(source_id),
        )

        result = self.manager.executor.sync(
            source=source_path,
            destination=destination_path,
        )

        if result.success:
            status.mark_success()
        else:
            error_message = result.stderr or "Synchronization failed."
            status.mark_failure(error_message)

        return result
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

        return {
            "component": "SynchronizationService",
            "rsync_available": self.is_available(),
            "tracked_sources": len(self._statuses),
        }