# ARGUS: An LLM-RAG Guided Unified Reasoning System for Security Operational Centres
# Copyright 2026 Koushik Pasunoori and Dr Jose Maria Alcaraz Calero
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
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

    def mark_running(self) -> None:
        """
        Record that synchronization has started.

        last_attempted_at represents the time at which
        the synchronization attempt began.
        """

        now = datetime.now().astimezone()

        self.status = "running"
        self.last_attempted_at = now
        self.error_message = None

    def mark_success(self) -> None:
        """
        Record a successful synchronization.

        last_attempted_at is preserved from mark_running().
        last_successful_at records the completion time.
        """

        now = datetime.now().astimezone()

        self.status = "success"
        self.last_successful_at = now
        self.error_message = None

    def mark_failure(
        self,
        error_message: str,
    ) -> None:
        """
        Record a failed synchronization.

        last_attempted_at is preserved from mark_running().
        """

        self.status = "failed"
        self.error_message = error_message

    def to_dict(self) -> dict:
        """
        Return the status as a serializable dictionary.
        """

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
