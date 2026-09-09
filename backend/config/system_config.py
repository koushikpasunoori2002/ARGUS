"""
Configuration manager for system.config.
"""

from __future__ import annotations

import json
from pathlib import Path


class SystemConfig:
    """
    Loads and manages synchronization settings stored
    in system.config.
    """

    def __init__(
        self,
        config_path: str | Path = "config/system.config",
    ) -> None:
        self.config_path = Path(config_path)

        if not self.config_path.exists():
            raise FileNotFoundError(
                f"Configuration file not found: "
                f"{self.config_path}"
            )

    def load(self) -> dict:
        """
        Load the complete system configuration.
        """

        with self.config_path.open(
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

        if not isinstance(data, dict):
            raise ValueError(
                "system.config must contain a JSON object."
            )

        return data

    def get_synchronization_config(self) -> dict:
        """
        Return the synchronization configuration.
        """

        data = self.load()

        synchronization = data.get(
            "synchronization",
            {},
        )

        if not isinstance(
            synchronization,
            dict,
        ):
            raise ValueError(
                "'synchronization' must be a JSON object."
            )

        return synchronization

    def is_enabled(self) -> bool:
        """
        Return whether synchronization is globally enabled.
        """

        synchronization = (
            self.get_synchronization_config()
        )

        enabled = synchronization.get(
            "enabled",
            True,
        )

        if not isinstance(enabled, bool):
            raise ValueError(
                "'enabled' must be a boolean."
            )

        return enabled

    def get_default_interval(self) -> int:
        """
        Return the default synchronization interval.
        """

        synchronization = (
            self.get_synchronization_config()
        )

        interval = synchronization.get(
            "default_interval_seconds",
            60,
        )

        if (
            not isinstance(interval, int)
            or isinstance(interval, bool)
            or interval < 1
        ):
            raise ValueError(
                "'default_interval_seconds' must be "
                "an integer greater than 0."
            )

        return interval

    def get_scheduler_check_interval(self) -> int:
        """
        Return the scheduler polling interval.
        """

        synchronization = (
            self.get_synchronization_config()
        )

        interval = synchronization.get(
            "scheduler_check_interval_seconds",
            1,
        )

        if (
            not isinstance(interval, int)
            or isinstance(interval, bool)
            or interval < 1
        ):
            raise ValueError(
                "'scheduler_check_interval_seconds' "
                "must be an integer greater than 0."
            )

        return interval

    def get_all(self) -> dict:
        """
        Return the complete system configuration.
        """

        return self.load()