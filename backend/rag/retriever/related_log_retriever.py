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
Retrieves log records related to an initial set of semantic results.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from backend.database.chroma import ChromaDatabase


class RelatedLogRetriever:
    """
    Expands semantic retrieval results by finding nearby records
    belonging to the same source and process context.
    """

    def __init__(
        self,
        database: Optional[ChromaDatabase] = None,
        time_window_seconds: int = 60,
        max_results: int = 20,
    ):
        if time_window_seconds <= 0:
            raise ValueError("time_window_seconds must be greater than 0.")
        if max_results <= 0:
            raise ValueError("max_results must be greater than 0.")

        self.database = (
            database if database is not None else ChromaDatabase()
        )
        self.time_window_seconds = time_window_seconds
        self.max_results = max_results

    def retrieve(
        self,
        seed_results: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """
        Retrieve records related to the supplied semantic results.
        """

        seeds = self._convert_results(seed_results)

        if not seeds:
            return []

        related_records: Dict[str, Dict[str, Any]] = {}

        for seed in seeds:
            metadata = seed.get("metadata", {})

            source = metadata.get("source")
            log_type = metadata.get("log_type")
            process = metadata.get("process")
            timestamp = self._parse_timestamp(
                metadata.get("timestamp")
            )

            if not source or not log_type or not process or timestamp is None:
                continue

            candidates = self.database.get(
                where={
                    "$and": [
                        {"source": source},
                        {"log_type": log_type},
                        {"process": process},
                    ]
                }
            )

            for record in self._convert_results(candidates):
                record_metadata = record.get("metadata", {})

                record_timestamp = self._parse_timestamp(
                    record_metadata.get("timestamp")
                )

                if record_timestamp is None:
                    continue

                difference = abs(
                    (record_timestamp - timestamp).total_seconds()
                )

                if difference > self.time_window_seconds:
                    continue

                if not self._matches_optional_identity(
                    seed_metadata=metadata,
                    record_metadata=record_metadata,
                ):
                    continue

                record_id = record.get("id")

                if record_id is not None:
                    related_records[record_id] = record

        return sorted(
            related_records.values(),
            key=self._timestamp_sort_key,
        )[:self.max_results]

    def _matches_optional_identity(
        self,
        seed_metadata: Dict[str, Any],
        record_metadata: Dict[str, Any],
    ) -> bool:
        """
        Refine matching using user and IP only when available
        in the seed record.
        """

        for field in ("user", "ip"):
            seed_value = seed_metadata.get(field)

            if seed_value is None:
                continue

            record_value = record_metadata.get(field)

            if record_value is not None and record_value != seed_value:
                return False

        return True

    def _convert_results(
        self,
        results: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """
        Convert ChromaDB result structures into individual records.

        Handles both nested result lists and direct lists/dictionaries
        returned by different ChromaDB operations.
        """

        ids = results.get("ids", [])
        documents = results.get("documents", [])
        metadatas = results.get("metadatas", [])
        distances = results.get("distances", [])

        if ids and isinstance(ids[0], list):
            ids = ids[0]

        if documents and isinstance(documents[0], list):
            documents = documents[0]

        if metadatas and isinstance(metadatas[0], list):
            metadatas = metadatas[0]

        if distances and isinstance(distances[0], list):
            distances = distances[0]

        if isinstance(metadatas, dict):
            metadatas = [metadatas]

        records = []

        count = max(
            len(ids),
            len(documents),
            len(metadatas),
        )

        for index in range(count):
            records.append(
                {
                    "id": (
                        ids[index]
                        if index < len(ids)
                        else None
                    ),
                    "document": (
                        documents[index]
                        if index < len(documents)
                        else None
                    ),
                    "metadata": (
                        metadatas[index]
                        if index < len(metadatas)
                        else {}
                    ),
                    "distance": (
                        distances[index]
                        if index < len(distances)
                        else None
                    ),
                }
            )

        return records

    def _parse_timestamp(
        self,
        value: Any,
    ) -> Optional[datetime]:
        """
        Safely parse an ISO timestamp.

        Invalid or corrupted timestamps are ignored.
        """

        if not value or not isinstance(value, str):
            return None

        try:
            timestamp = datetime.fromisoformat(value)

            if timestamp.tzinfo is None:
                timestamp = timestamp.replace(
                    tzinfo=timezone.utc
                )

            return timestamp

        except (TypeError, ValueError, OverflowError):
            return None

    def _timestamp_sort_key(
        self,
        record: Dict[str, Any],
    ) -> datetime:
        """
        Return a timestamp suitable for chronological sorting.
        """

        timestamp = self._parse_timestamp(
            record.get("metadata", {}).get("timestamp")
        )

        if timestamp is None:
            return datetime.max.replace(
                tzinfo=timezone.utc
            )

        return timestamp

    def info(self) -> Dict[str, Any]:
        """
        Return retriever configuration information.
        """

        return {
            "time_window_seconds": self.time_window_seconds,
            "max_results": self.max_results,
            "database": self.database.info(),
        }

    def __repr__(self) -> str:
        return (
            f"RelatedLogRetriever("
            f"time_window_seconds={self.time_window_seconds})"
        )
