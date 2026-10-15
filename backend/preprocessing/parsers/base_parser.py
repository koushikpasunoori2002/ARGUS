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
base_parser.py

Abstract base class for all log parsers.
"""

from abc import ABC, abstractmethod


class BaseParser(ABC):

    @abstractmethod
    def parse(self, text):
        """
        Parse log text into LogRecord objects.
        """
        pass

    @abstractmethod
    def supports(self):
        """
        Return the supported log type.
        """
        pass

    @abstractmethod
    def info(self):
        """
        Return parser metadata.
        """
        pass
