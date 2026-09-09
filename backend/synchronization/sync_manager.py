"""
Synchronization manager.
"""

from __future__ import annotations

from pathlib import Path

from .models.sync_source import SyncSource
from .rsync_executor import RsyncExecutor, RsyncResult


class SyncManager:
    """
    Coordinates synchronization for configured sources.

    The manager is responsible for:
    - validating the source
    - checking whether synchronization is enabled
    - passing server-specific rsync options
    - executing rsync
    - returning the synchronization result

    Scheduling and configuration management are handled separately.
    """

    def __init__(
        self,
        executor: RsyncExecutor | None = None,
    ) -> None:
        self.executor = executor or RsyncExecutor()

    def sync_source(
        self,
        source: SyncSource,
    ) -> RsyncResult:
        """
        Synchronize one configured source using its
        server-specific rsync configuration.
        """

        if not isinstance(source, SyncSource):
            raise TypeError(
                "source must be a SyncSource instance."
            )

        if not source.enabled:
            return RsyncResult(
                success=False,
                return_code=-2,
                stdout="",
                stderr=(
                    f"Synchronization is disabled for "
                    f"source '{source.source_id}'."
                ),
            )

        destination = Path(
            source.local_path
        )

        return self.executor.sync(
            source=source.rsync_source,
            destination=destination,
            options=source.rsync_options,
        )

    def is_available(self) -> bool:
        """
        Check whether the rsync runtime is available.
        """

        return self.executor.is_available()

    def info(self) -> dict:
        """
        Return manager metadata.
        """

        return {
            "component": "SyncManager",
            "rsync_available": self.is_available(),
        }