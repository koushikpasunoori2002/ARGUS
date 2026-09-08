"""
Configuration manager for hosts.config.
"""

from __future__ import annotations

import json
from pathlib import Path

from backend.synchronization.models.sync_source import SyncSource


class HostsConfig:
    """
    Loads and manages server definitions stored in hosts.config.
    """

    def __init__(
        self,
        config_path: str | Path = "config/hosts.config",
    ) -> None:
        self.config_path = Path(config_path)

        if not self.config_path.exists():
            raise FileNotFoundError(
                f"Configuration file not found: "
                f"{self.config_path}"
            )

    def load(self) -> list[SyncSource]:
        """
        Load all configured servers.
        """

        with self.config_path.open(
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

        if not isinstance(data, dict):
            raise ValueError(
                "hosts.config must contain a JSON object."
            )

        servers = data.get("servers", [])

        if not isinstance(servers, list):
            raise ValueError(
                "'servers' must be a JSON array."
            )

        return [
            SyncSource(**server)
            for server in servers
        ]

    def save(
        self,
        sources: list[SyncSource],
    ) -> None:
        """
        Save server definitions to hosts.config.
        """

        if not isinstance(sources, list):
            raise TypeError(
                "sources must be a list."
            )

        data = {
            "servers": [
                source.to_dict()
                for source in sources
            ]
        }

        self.config_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with self.config_path.open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                data,
                file,
                indent=2,
            )
            file.write("\n")

    def get_all(self) -> list[SyncSource]:
        """Return all configured servers."""

        return self.load()

    def get(
        self,
        source_id: str,
    ) -> SyncSource | None:
        """Return one server by its ID."""

        for source in self.load():
            if source.source_id == source_id:
                return source

        return None

    def add(
        self,
        source: SyncSource,
    ) -> None:
        """Add a new server."""

        if not isinstance(source, SyncSource):
            raise TypeError(
                "source must be a SyncSource instance."
            )

        sources = self.load()

        if any(
            item.source_id == source.source_id
            for item in sources
        ):
            raise ValueError(
                f"Server '{source.source_id}' already exists."
            )

        sources.append(source)
        self.save(sources)

    def update(
        self,
        source: SyncSource,
    ) -> None:
        """Update an existing server."""

        if not isinstance(source, SyncSource):
            raise TypeError(
                "source must be a SyncSource instance."
            )

        sources = self.load()

        for index, existing in enumerate(sources):
            if existing.source_id == source.source_id:
                sources[index] = source
                self.save(sources)
                return

        raise ValueError(
            f"Server '{source.source_id}' does not exist."
        )

    def delete(
        self,
        source_id: str,
    ) -> None:
        """Delete a server by ID."""

        sources = self.load()

        updated = [
            source
            for source in sources
            if source.source_id != source_id
        ]

        if len(updated) == len(sources):
            raise ValueError(
                f"Server '{source_id}' does not exist."
            )

        self.save(updated)