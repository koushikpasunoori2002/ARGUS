"""
Synchronization status model.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class SyncStatus:
    """
    Stores the current synchronization status for one source.
    """

    source_id: str
    status: str = "never_synced"
    last_attempted_at: datetime | None = None
    last_successful_at: datetime | None = None
    error_message: str | None = None

    def mark_success(self) -> None:
        """Record a successful synchronization."""

        now = datetime.now().astimezone()

        self.status = "success"
        self.last_attempted_at = now
        self.last_successful_at = now
        self.error_message = None

    def mark_failure(self, error_message: str) -> None:
        """Record a failed synchronization."""

        now = datetime.now().astimezone()

        self.status = "failed"
        self.last_attempted_at = now
        self.error_message = error_message

    def to_dict(self) -> dict:
        """Return the status as a serializable dictionary."""

        return {
            "source_id": self.source_id,
            "status": self.status,
            "last_attempted_at": (
                self.last_attempted_at.isoformat()
                if self.last_attempted_at
                else None
            ),
            "last_successful_at": (
                self.last_successful_at.isoformat()
                if self.last_successful_at
                else None
            ),
            "error_message": self.error_message,
        }