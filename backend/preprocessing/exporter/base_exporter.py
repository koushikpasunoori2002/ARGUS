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
base_exporter.py

Base class for all exporters.
"""

from abc import ABC, abstractmethod
from pathlib import Path


class BaseExporter(ABC):
    """
    Base class for all exporters.
    """

    def __init__(self, output_path):
        """
        Initialize the exporter.

        Parameters
        ----------
        output_path : str or Path
            Destination file path.
        """

        self.output_path = Path(output_path)

        self.output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

    @abstractmethod
    def export(self, records):
        """
        Export records.

        Parameters
        ----------
        records : list
            List of LogRecord objects.
        """

        raise NotImplementedError

    def exists(self):
        """
        Determine whether the output file exists.
        """

        return self.output_path.exists()

    def size(self):
        """
        Return the file size in bytes.
        """

        if not self.exists():
            return 0

        return self.output_path.stat().st_size

    def path(self):
        """
        Return the export path.
        """

        return str(self.output_path)

    def __repr__(self):

        return (
            f"{self.__class__.__name__}("
            f"path='{self.output_path}')"
        )
