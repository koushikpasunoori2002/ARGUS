"""
Tests for related log retrieval.
"""

from backend.rag.retriever import Retriever
from backend.rag.retriever.related_log_retriever import RelatedLogRetriever


def test_related_log_retrieval_expands_semantic_results():
    """
    Related retrieval should expand semantic results into
    the surrounding security event sequence.
    """

    retriever = Retriever(top_k=3)

    seed_results = retriever.retrieve(
        "failed SSH authentication brute force attack"
    )

    related_retriever = RelatedLogRetriever(
        database=retriever.database,
        time_window_seconds=60,
    )

    related_results = related_retriever.retrieve(seed_results)

    assert len(seed_results["ids"][0]) == 3
    assert len(related_results) >= len(seed_results["ids"][0])

    event_types = [
        record["metadata"].get("event_type")
        for record in related_results
    ]

    assert "AUTH_FAILURE" in event_types
    assert "AUTH_SUCCESS" in event_types


def test_related_log_retrieval_returns_chronological_results():
    """
    Related records should be returned in chronological order.
    """

    retriever = Retriever(top_k=3)

    seed_results = retriever.retrieve(
        "failed SSH authentication brute force attack"
    )

    related_retriever = RelatedLogRetriever(
        database=retriever.database,
        time_window_seconds=60,
    )

    related_results = related_retriever.retrieve(seed_results)

    timestamps = [
        record["metadata"].get("timestamp")
        for record in related_results
    ]

    assert timestamps == sorted(timestamps)


def test_related_log_retrieval_ignores_invalid_timestamps():
    """
    Invalid timestamps should not cause related retrieval to fail.
    """

    retriever = Retriever(top_k=3)

    seed_results = retriever.retrieve(
        "failed SSH authentication brute force attack"
    )

    related_retriever = RelatedLogRetriever(
        database=retriever.database,
        time_window_seconds=60,
    )

    related_results = related_retriever.retrieve(seed_results)

    for record in related_results:
        timestamp = record["metadata"].get("timestamp")
        assert timestamp
        assert "\x00" not in timestamp


def test_related_log_retrieval_handles_empty_results():
    """
    Empty semantic results should return an empty related-result list.
    """

    related_retriever = RelatedLogRetriever(
        time_window_seconds=60,
    )

    assert related_retriever.retrieve(
        {
            "ids": [[]],
            "documents": [[]],
            "metadatas": [[]],
            "distances": [[]],
        }
    ) == []