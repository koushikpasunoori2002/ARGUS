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
parser_factory.py

Factory for creating log parser instances.
"""

from backend.config.log_types_config import LogTypesConfig

from .auth_parser import AuthParser
from .syslog_parser import SyslogParser
from .kern_parser import KernParser
from .dpkg_parser import DpkgParser
from .dmesg_parser import DmesgParser


class ParserFactory:
    """
    Creates the appropriate parser for a configured log type.
    """

    _AVAILABLE_PARSERS = {
        "AuthParser": AuthParser,
        "SyslogParser": SyslogParser,
        "KernParser": KernParser,
        "DpkgParser": DpkgParser,
        "DmesgParser": DmesgParser,
    }

    @classmethod
    def create(cls, log_type: str):
        """
        Create a parser for the specified configured log type.

        Parameters
        ----------
        log_type : str
            Log type detected by FileDetector.

        Returns
        -------
        BaseParser
            Instance of the configured parser.

        Raises
        ------
        TypeError
            If log_type is not a string.
        ValueError
            If the log type is not configured or the configured
            parser is not available.
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

        config = LogTypesConfig()

        try:
            parser_name = config.get_parser_name(
                log_type
            )

        except KeyError as exc:
            raise ValueError(
                f"No parser configured for log type: "
                f"'{log_type}'."
            ) from exc

        parser_class = cls._AVAILABLE_PARSERS.get(
            parser_name
        )

        if parser_class is None:
            raise ValueError(
                f"Configured parser '{parser_name}' "
                f"for log type '{log_type}' is not available."
            )

        return parser_class()
