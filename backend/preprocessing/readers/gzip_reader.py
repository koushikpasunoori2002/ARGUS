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
gzip_reader.py

Reads compressed (.gz) log files.
"""

import gzip
from pathlib import Path


class GzipReader:
    """
    Reads gzip compressed log files.
    """

    def __init__(self, encoding="utf-8", errors="ignore"):

        self.encoding = encoding

        self.errors = errors

    # ------------------------------------------------------------------
    # Read Entire File
    # ------------------------------------------------------------------

    def read(self, file_path):
        """
        Reads the entire compressed file and returns it as a string.
        """

        file_path = Path(file_path)

        if not file_path.exists():

            raise FileNotFoundError(
                f"{file_path} does not exist."
            )

        if file_path.suffix != ".gz":

            raise ValueError(
                f"{file_path} is not a gzip (.gz) file."
            )

        with gzip.open(
            file_path,
            mode="rt",
            encoding=self.encoding,
            errors=self.errors,
        ) as file:

            return file.read()

    # ------------------------------------------------------------------
    # Read Line By Line
    # ------------------------------------------------------------------

    def read_lines(self, file_path):
        """
        Reads the compressed file and returns a list of lines.
        """

        file_path = Path(file_path)

        if not file_path.exists():

            raise FileNotFoundError(
                f"{file_path} does not exist."
            )

        if file_path.suffix != ".gz":

            raise ValueError(
                f"{file_path} is not a gzip (.gz) file."
            )

        with gzip.open(
            file_path,
            mode="rt",
            encoding=self.encoding,
            errors=self.errors,
        ) as file:

            return file.readlines()

    # ------------------------------------------------------------------
    # Reader Information
    # ------------------------------------------------------------------

    def info(self):
        """
        Returns reader metadata.
        """

        return {

            "reader": "GzipReader",

            "version": "1.0",

            "supports": [

                ".gz",

            ],

            "mode": "text",

        }
