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
chunk_manager.py

Manages collections of Chunk objects.
"""

from .chunker import Chunker


class ChunkManager:
    """
    Creates and manages Chunk objects.
    """

    def __init__(
        self,
        chunk_size=500,
        overlap=50,
    ):

        self.chunker = Chunker(
            chunk_size=chunk_size,
            overlap=overlap,
        )

        self.chunks = []

        self._chunk_counter = 1

    def _assign_unique_ids(self, chunks):
        """
        Assign globally unique IDs to chunks.
        """

        for chunk in chunks:

            chunk.chunk_id = (
                f"chunk_{self._chunk_counter}"
            )

            self._chunk_counter += 1

    def add_text(
        self,
        text,
        source="unknown",
        metadata=None,
    ):
        """
        Create chunks from text and store them.
        """

        new_chunks = self.chunker.chunk_text(
            text=text,
            source=source,
            metadata=metadata,
        )

        self._assign_unique_ids(
            new_chunks
        )

        self.chunks.extend(
            new_chunks
        )

        return new_chunks

    def add_record(
        self,
        record,
        source="unknown",
    ):
        """
        Create chunks from a LogRecord and store them.
        """

        new_chunks = self.chunker.chunk_record(
            record=record,
            source=source,
        )

        self._assign_unique_ids(
            new_chunks
        )

        self.chunks.extend(
            new_chunks
        )

        return new_chunks

    def get_chunks(self):
        """
        Return all stored chunks.
        """

        return self.chunks

    def get_chunk(self, chunk_id):
        """
        Retrieve a chunk by ID.
        """

        for chunk in self.chunks:

            if chunk.chunk_id == chunk_id:
                return chunk

        return None

    def count(self):
        """
        Return the number of stored chunks.
        """

        return len(self.chunks)

    def clear(self):
        """
        Remove all stored chunks.
        """

        self.chunks.clear()

        self._chunk_counter = 1

    def __len__(self):

        return len(self.chunks)

    def __repr__(self):

        return (
            f"ChunkManager("
            f"chunks={len(self.chunks)})"
        )
