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
Synchronization source model.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class SyncSource:
    """
    Represents one configured synchronization source.

    The source contains connection, filesystem, scheduling,
    and rsync configuration information.
    """

    source_id: str
    name: str
    host: str
    username: str
    remote_path: str
    local_path: str
    enabled: bool = True
    sync_interval: int = 60
    rsync_options: list[str] = field(
        default_factory=lambda: ["-avz"]
    )

    def __post_init__(self) -> None:
        """Validate the source configuration."""

        fields = {
            "source_id": self.source_id,
            "name": self.name,
            "host": self.host,
            "username": self.username,
            "remote_path": self.remote_path,
            "local_path": self.local_path,
        }

        for field_name, value in fields.items():

            if (
                not isinstance(value, str)
                or not value.strip()
            ):
                raise ValueError(
                    f"{field_name} must be a non-empty string."
                )

        if not isinstance(self.enabled, bool):

            raise TypeError(
                "enabled must be a boolean."
            )

        if (
            not isinstance(self.sync_interval, int)
            or isinstance(self.sync_interval, bool)
            or self.sync_interval < 1
        ):

            raise ValueError(
                "sync_interval must be an integer "
                "greater than 0."
            )

        if not isinstance(self.rsync_options, list):

            raise TypeError(
                "rsync_options must be a list."
            )

        for option in self.rsync_options:

            if (
                not isinstance(option, str)
                or not option.strip()
            ):
                raise ValueError(
                    "Every rsync option must be a "
                    "non-empty string."
                )

    @property
    def rsync_source(self) -> str:
        """
        Return the source in rsync SSH format.
        """

        return (
            f"{self.username}@{self.host}:"
            f"{self.remote_path}"
        )

    def to_dict(self) -> dict:
        """Return the source as a dictionary."""

        return {
            "source_id": self.source_id,
            "name": self.name,
            "host": self.host,
            "username": self.username,
            "remote_path": self.remote_path,
            "local_path": self.local_path,
            "enabled": self.enabled,
            "sync_interval": self.sync_interval,
            "rsync_options": self.rsync_options,
        }
