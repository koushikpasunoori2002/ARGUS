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
file_info.py

Stores metadata describing a log file.
"""

from dataclasses import dataclass
from pathlib import Path


@dataclass
class FileInfo:
    """
    Stores metadata about a detected log file.
    """

    path: Path
    filename: str
    log_type: str
    compressed: bool
    rotation: int
    extension: str
    reader: str

    # --------------------------------------------------------------
    # Convenience Properties
    # --------------------------------------------------------------

    @property
    def exists(self):
        """
        Returns True if the file exists.
        """

        return self.path.exists()

    @property
    def directory(self):
        """
        Returns the parent directory.
        """

        return self.path.parent

    @property
    def stem(self):
        """
        Returns the filename without its suffix.
        """

        return self.path.stem

    @property
    def suffix(self):
        """
        Returns the file suffix.
        """

        return self.path.suffix

    # --------------------------------------------------------------
    # Serialization
    # --------------------------------------------------------------

    def to_dict(self):
        """
        Convert metadata into a dictionary.
        """

        return {

            "path": str(self.path),

            "filename": self.filename,

            "log_type": self.log_type,

            "compressed": self.compressed,

            "rotation": self.rotation,

            "extension": self.extension,

            "reader": self.reader,

        }

    # --------------------------------------------------------------
    # String Representation
    # --------------------------------------------------------------

    def __str__(self):

        return (
            f"\nPath        : {self.path}"
            f"\nFilename    : {self.filename}"
            f"\nType        : {self.log_type}"
            f"\nCompressed  : {self.compressed}"
            f"\nRotation    : {self.rotation}"
            f"\nExtension   : {self.extension}"
            f"\nReader      : {self.reader}"
        )

    def __repr__(self):

        return (
            "FileInfo("
            f"filename='{self.filename}', "
            f"log_type='{self.log_type}', "
            f"compressed={self.compressed}, "
            f"rotation={self.rotation}, "
            f"reader='{self.reader}'"
            ")"
        )
