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
json_exporter.py

Exports log records to JSON format.
"""

from pathlib import Path
import json

from .base_exporter import BaseExporter


class JSONExporter(BaseExporter):
    """
    Export records to JSON.
    """

    def __init__(self, output_path):

        super().__init__(output_path)

    def _convert_record(self, record):
        """
        Convert a record into a dictionary.
        """

        if isinstance(record, dict):
            return record

        if hasattr(record, "__dict__"):
            return vars(record)

        return {"value": str(record)}

    def export(self, records):
        """
        Export records to a JSON file.

        Parameters
        ----------
        records : list
            List of LogRecord objects.

        Returns
        -------
        str
        """

        data = []

        for record in records:

            data.append(
                self._convert_record(record)
            )

        with open(
            self.output_path,
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                data,
                file,
                indent=4,
                default=str,
            )

        return str(self.output_path)

    def read(self):
        """
        Read exported JSON records.
        """

        if not self.exists():
            return []

        with open(
            self.output_path,
            "r",
            encoding="utf-8",
        ) as file:

            return json.load(file)

    def clear(self):
        """
        Remove all records from the file.
        """

        with open(
            self.output_path,
            "w",
            encoding="utf-8",
        ) as file:

            json.dump([], file)

    def count(self):
        """
        Return the number of stored records.
        """

        return len(self.read())

    def __repr__(self):

        return (
            f"JSONExporter("
            f"path='{self.output_path}')"
        )
