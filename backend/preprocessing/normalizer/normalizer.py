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
normalizer.py

Normalizes log messages and replaces frequently
occurring words with short tokens.
"""

import re

from .dictionary_manager import DictionaryManager


class LogNormalizer:
    """
    Normalizes log messages.
    """

    def __init__(self, dictionary_manager=None):
        """
        Initialize the normalizer.
        """

        if dictionary_manager is None:
            dictionary_manager = DictionaryManager()

        self.dictionary = dictionary_manager

        self.stop_words = {
            "for",
            "from",
            "the",
            "and",
            "to",
            "of",
            "on",
            "in",
            "a",
            "an",
            "is",
            "was",
            "at",
            "by",
            "with",
        }

    def normalize_text(self, text):
        """
        Normalize a text string.

        Parameters
        ----------
        text : str

        Returns
        -------
        str
        """

        if text is None:
            return ""

        text = str(text).lower()

        text = re.sub(r"\s+", " ", text)

        text = text.strip()

        words = text.split()

        normalized_words = []

        for word in words:

            cleaned_word = re.sub(
                r"[^a-zA-Z0-9_\-./:]",
                "",
                word,
            )

            if not cleaned_word:
                continue

            if cleaned_word in self.stop_words:

                normalized_words.append(cleaned_word)

                continue

            if cleaned_word.isdigit():

                normalized_words.append(cleaned_word)

                continue

            if "." in cleaned_word:

                normalized_words.append(cleaned_word)

                continue

            token = self.dictionary.get_token(
                cleaned_word
            )

            normalized_words.append(token)

        return " ".join(normalized_words)

    def normalize_record(self, record):
        """
        Normalize a LogRecord object.

        Parameters
        ----------
        record : LogRecord

        Returns
        -------
        LogRecord
        """

        if hasattr(record, "message"):

            record.message = self.normalize_text(
                record.message
            )

        return record

    def normalize_records(self, records):
        """
        Normalize a list of records.

        Parameters
        ----------
        records : list

        Returns
        -------
        list
        """

        normalized_records = []

        for record in records:

            normalized_records.append(
                self.normalize_record(record)
            )

        return normalized_records

    def expand_text(self, text):
        """
        Expand tokens back into words.

        Parameters
        ----------
        text : str

        Returns
        -------
        str
        """

        words = text.split()

        expanded_words = []

        for word in words:

            expanded_words.append(
                self.dictionary.expand_token(word)
            )

        return " ".join(expanded_words)

    def save_dictionary(self):
        """
        Save the dictionary to disk.
        """

        self.dictionary.save()

    def clear_dictionary(self):
        """
        Clear the dictionary.
        """

        self.dictionary.clear()

    def dictionary_size(self):
        """
        Return the number of entries.
        """

        return self.dictionary.size()
