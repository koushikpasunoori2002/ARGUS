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
log_types_config.py

Loads configurable log-type and parser definitions
from config/system.config.
"""

from __future__ import annotations

from backend.config.system_config import SystemConfig


class LogTypesConfig:
    """
    Provides access to log-type and parser definitions
    stored in system.config.
    """

    def __init__(
        self,
        system_config=None,
    ):
        self.system_config = (
            system_config
            if system_config is not None
            else SystemConfig()
        )

        self._log_types = (
            self._load_log_types()
        )

    def _load_log_types(self) -> dict:
        """
        Load and validate log-type definitions.
        """

        config = self.system_config.get_all()

        log_types = config.get(
            "log_types",
            {},
        )

        if not isinstance(log_types, dict):
            raise ValueError(
                "'log_types' must be a JSON object."
            )

        for log_type, definition in log_types.items():

            if not isinstance(
                log_type,
                str,
            ) or not log_type.strip():
                raise ValueError(
                    "Log type names must be "
                    "non-empty strings."
                )

            if not isinstance(
                definition,
                dict,
            ):
                raise ValueError(
                    f"Definition for log type "
                    f"'{log_type}' must be an object."
                )

            parser_name = definition.get(
                "parser"
            )

            if not isinstance(
                parser_name,
                str,
            ) or not parser_name.strip():
                raise ValueError(
                    f"Parser definition for "
                    f"'{log_type}' must be a "
                    f"non-empty string."
                )

        return log_types

    def get_parser_name(
        self,
        log_type: str,
    ) -> str:
        """
        Return the configured parser name
        for a log type.
        """

        if not isinstance(
            log_type,
            str,
        ):
            raise TypeError(
                "log_type must be a string."
            )

        log_type = log_type.strip()

        if not log_type:
            raise ValueError(
                "log_type cannot be empty."
            )

        definition = self._log_types.get(
            log_type
        )

        if definition is None:
            raise KeyError(
                f"Log type '{log_type}' "
                "is not configured."
            )

        return definition["parser"]

    def get_log_type(
        self,
        log_type: str,
    ) -> dict:
        """
        Return the complete definition
        for one log type.
        """

        if not isinstance(
            log_type,
            str,
        ):
            raise TypeError(
                "log_type must be a string."
            )

        log_type = log_type.strip()

        if not log_type:
            raise ValueError(
                "log_type cannot be empty."
            )

        if log_type not in self._log_types:
            raise KeyError(
                f"Log type '{log_type}' "
                "is not configured."
            )

        return self._log_types[
            log_type
        ]

    def get_all(self) -> dict:
        """
        Return all configured log types.
        """

        return self._log_types.copy()

    def supported_log_types(self) -> list[str]:
        """
        Return configured log-type names.
        """

        return list(
            self._log_types.keys()
        )

    def info(self) -> dict:
        """
        Return configuration metadata.
        """

        return {
            "component": "LogTypesConfig",
            "log_type_count": len(
                self._log_types
            ),
            "log_types": (
                self.supported_log_types()
            ),
        }

    def __repr__(self):
        return (
            "LogTypesConfig("
            f"log_types="
            f"{self.supported_log_types()}"
            ")"
        )
