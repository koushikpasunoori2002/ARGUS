"""
End-to-end security analysis performance test.

Pipeline:

Log data
    ->
Log Retriever
    +
Knowledge Retriever
    ->
ContextBuilder
    ->
RAGContext
    ->
PromptBuilder
    ->
Ollama LLM
    ->
Security Analysis
"""

from pathlib import Path
import sys
import time


# --------------------------------------------------------------
# Project Root
# --------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[3]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# --------------------------------------------------------------
# Imports
# --------------------------------------------------------------

from backend.rag.context import ContextBuilder
from backend.rag.context import RAGContext

from backend.rag.retriever import Retriever

from backend.knowledge import KnowledgeRetriever

from backend.database.chroma import ChromaDatabase

from backend.llm.embeddings import EmbeddingManager

from backend.llm.generation import PromptBuilder
from backend.llm.generation import LLMClient
from backend.llm.generation import LLMResponse


# --------------------------------------------------------------
# Test Queries
# --------------------------------------------------------------

QUERIES = [
    "failed SSH authentication brute force attack",
    "suspicious repeated login attempts",
    "unauthorised access through SSH",
]


# --------------------------------------------------------------
# Main Test
# --------------------------------------------------------------

def main():

    print("=" * 70)
    print("END-TO-END SECURITY ANALYSIS PERFORMANCE TEST")
    print("=" * 70)

    # ----------------------------------------------------------
    # Step 1 — Initialise embedding model
    # ----------------------------------------------------------

    print("\n[1] Initialising embedding model...")

    embedding_manager = EmbeddingManager()

    print(
        "Embedding Model:",
        embedding_manager.model_information()
    )

    print(
        "Embedding Dimension:",
        embedding_manager.embedding_dimension()
    )

    print("Embedding Model: PASS")

    # ----------------------------------------------------------
    # Step 2 — Create log database
    # ----------------------------------------------------------

    print("\n[2] Creating log database...")

    log_database = ChromaDatabase(
        collection_name="security_performance_log_test",
        persist_directory="data/test_security_performance_log",
    )

    log_database.clear()

    print("Log Database: PASS")

    # ----------------------------------------------------------
    # Step 3 — Create knowledge database
    # ----------------------------------------------------------

    print("\n[3] Creating knowledge database...")

    knowledge_database = ChromaDatabase(
        collection_name="security_performance_knowledge_test",
        persist_directory="data/test_security_performance_knowledge",
    )

    knowledge_database.clear()

    print("Knowledge Database: PASS")

    # ----------------------------------------------------------
    # Step 4 — Create retrievers
    # ----------------------------------------------------------

    print("\n[4] Creating retrievers...")

    log_retriever = Retriever(
        database=log_database,
        embedding_manager=embedding_manager,
        top_k=2,
    )

    knowledge_retriever = KnowledgeRetriever(
        database=knowledge_database,
        embedding_manager=embedding_manager,
        top_k=2,
    )

    print("Log Retriever: PASS")
    print("Knowledge Retriever: PASS")

    # ----------------------------------------------------------
    # Step 5 — Create log records
    # ----------------------------------------------------------

    log_records = [
        {
            "id": "performance_log_001",
            "document": (
                "Failed password for root "
                "from 192.168.1.20 port 22 ssh2"
            ),
            "metadata": {
                "source": "auth.log",
                "log_type": "auth",
                "severity": "HIGH",
            },
        },
        {
            "id": "performance_log_002",
            "document": (
                "Failed password for admin "
                "from 192.168.1.30 port 22 ssh2"
            ),
            "metadata": {
                "source": "auth.log",
                "log_type": "auth",
                "severity": "HIGH",
            },
        },
        {
            "id": "performance_log_003",
            "document": (
                "Successful login for user osboxes"
            ),
            "metadata": {
                "source": "auth.log",
                "log_type": "auth",
                "severity": "INFO",
            },
        },
    ]

    print(
        "\nLog Records:",
        len(log_records)
    )

    # ----------------------------------------------------------
    # Step 6 — Generate log embeddings
    # ----------------------------------------------------------

    log_texts = [
        record["document"]
        for record in log_records
    ]

    log_embeddings = embedding_manager.embed_texts(
        log_texts
    )

    print(
        "Log Embedding Shape:",
        log_embeddings.shape
    )

    # ----------------------------------------------------------
    # Step 7 — Store log records
    # ----------------------------------------------------------

    log_database.add(
        ids=[
            record["id"]
            for record in log_records
        ],
        documents=log_texts,
        embeddings=log_embeddings.tolist(),
        metadatas=[
            record["metadata"]
            for record in log_records
        ],
    )

    print(
        "Log Vectors Stored:",
        log_database.count()
    )

    # ----------------------------------------------------------
    # Step 8 — Create security knowledge
    # ----------------------------------------------------------

    knowledge_records = [
        {
            "id": "performance_kb_001",
            "document": (
                "Repeated failed SSH authentication "
                "attempts may indicate a brute-force attack."
            ),
            "metadata": {
                "source": "security_knowledge.txt",
                "category": "authentication",
            },
        },
        {
            "id": "performance_kb_002",
            "document": (
                "Brute-force attacks involve repeated "
                "authentication attempts against a service."
            ),
            "metadata": {
                "source": "security_knowledge.txt",
                "category": "authentication",
            },
        },
    ]

    print(
        "Knowledge Records:",
        len(knowledge_records)
    )

    # ----------------------------------------------------------
    # Step 9 — Generate knowledge embeddings
    # ----------------------------------------------------------

    knowledge_texts = [
        record["document"]
        for record in knowledge_records
    ]

    knowledge_embeddings = embedding_manager.embed_texts(
        knowledge_texts
    )

    print(
        "Knowledge Embedding Shape:",
        knowledge_embeddings.shape
    )

    # ----------------------------------------------------------
    # Step 10 — Store knowledge records
    # ----------------------------------------------------------

    knowledge_database.add(
        ids=[
            record["id"]
            for record in knowledge_records
        ],
        documents=knowledge_texts,
        embeddings=knowledge_embeddings.tolist(),
        metadatas=[
            record["metadata"]
            for record in knowledge_records
        ],
    )

    print(
        "Knowledge Vectors Stored:",
        knowledge_database.count()
    )

    # ----------------------------------------------------------
    # Step 11 — Create ContextBuilder
    # ----------------------------------------------------------

    print("\n[5] Creating ContextBuilder...")

    context_builder = ContextBuilder(
        log_retriever=log_retriever,
        knowledge_retriever=knowledge_retriever,
        top_k_logs=2,
        top_k_knowledge=2,
    )

    print(
        "Context Builder Information:"
    )

    print(
        context_builder.info()
    )

    # ----------------------------------------------------------
    # Step 12 — Create PromptBuilder
    # ----------------------------------------------------------

    print("\n[6] Creating PromptBuilder...")

    prompt_builder = PromptBuilder()

    print("Prompt Builder: PASS")

    # ----------------------------------------------------------
    # Step 13 — Initialise LLM
    # ----------------------------------------------------------

    print("\n[7] Initialising local LLM...")

    llm_client = LLMClient()

    print(
        "LLM Information:"
    )

    print(
        llm_client.info()
    )

    if not llm_client.is_available():

        raise RuntimeError(
            "Ollama is not available."
        )

    print("Ollama Availability: PASS")

    if not llm_client.model_available():

        raise RuntimeError(
            "llama3.1:8b is not available."
        )

    print("Model Availability: PASS")

    # ----------------------------------------------------------
    # Step 14 — Run security analysis queries
    # ----------------------------------------------------------

    results = []

    print("\n" + "=" * 70)
    print("SECURITY ANALYSIS PERFORMANCE")
    print("=" * 70)

    for index, query in enumerate(
        QUERIES,
        start=1,
    ):

        print("\n" + "-" * 70)
        print(f"QUERY {index}")
        print("-" * 70)

        print("Query:", query)

        # ------------------------------------------------------
        # Retrieval timing
        # ------------------------------------------------------

        retrieval_start = time.perf_counter()

        context = context_builder.build(
            query
        )

        retrieval_time = (
            time.perf_counter()
            - retrieval_start
        )

        if not isinstance(
            context,
            RAGContext,
        ):

            raise AssertionError(
                "ContextBuilder did not return RAGContext."
            )

        if len(context.log_results) != 2:

            raise AssertionError(
                "Expected 2 retrieved log results."
            )

        if len(context.knowledge_results) != 2:

            raise AssertionError(
                "Expected 2 retrieved knowledge results."
            )

        # ------------------------------------------------------
        # Prompt timing
        # ------------------------------------------------------

        prompt_start = time.perf_counter()

        prompt = prompt_builder.build(
            context
        )

        prompt_time = (
            time.perf_counter()
            - prompt_start
        )

        if not prompt:

            raise AssertionError(
                "Generated prompt is empty."
            )

        # ------------------------------------------------------
        # LLM timing
        # ------------------------------------------------------

        llm_start = time.perf_counter()

        response = llm_client.generate(
            prompt
        )

        llm_time = (
            time.perf_counter()
            - llm_start
        )

        if not isinstance(
            response,
            LLMResponse,
        ):

            raise AssertionError(
                "LLM did not return LLMResponse."
            )

        if not response.answer:

            raise AssertionError(
                "LLM returned an empty answer."
            )

        # ------------------------------------------------------
        # Relevance validation
        # ------------------------------------------------------

        answer_lower = response.answer.lower()

        relevant_terms = [
            "ssh",
            "authentication",
            "failed",
        ]

        found_terms = [
            term
            for term in relevant_terms
            if term in answer_lower
        ]

        relevance_pass = len(found_terms) >= 2

        if not relevance_pass:

            raise AssertionError(
                "Generated analysis does not appear "
                "relevant to the security query."
            )

        # ------------------------------------------------------
        # Ollama timing
        # ------------------------------------------------------

        ollama_duration = (
            response.metadata.get(
                "total_duration",
                0
            ) / 1e9
        )

        prompt_tokens = response.metadata.get(
            "prompt_eval_count"
        )

        output_tokens = response.metadata.get(
            "eval_count"
        )

        # ------------------------------------------------------
        # Store result
        # ------------------------------------------------------

        results.append(
            {
                "query": query,
                "retrieval_time": retrieval_time,
                "prompt_time": prompt_time,
                "llm_time": llm_time,
                "ollama_duration": ollama_duration,
                "prompt_tokens": prompt_tokens,
                "output_tokens": output_tokens,
                "relevant_terms": found_terms,
            }
        )

        # ------------------------------------------------------
        # Display result
        # ------------------------------------------------------

        print("\nRetrieved Logs:", len(context.log_results))
        print(
            "Retrieved Knowledge:",
            len(context.knowledge_results)
        )

        print(
            "Prompt Length:",
            len(prompt),
            "characters"
        )

        print(
            "Retrieval Time:",
            f"{retrieval_time:.4f}",
            "seconds"
        )

        print(
            "Prompt Build Time:",
            f"{prompt_time:.4f}",
            "seconds"
        )

        print(
            "LLM Wall Time:",
            f"{llm_time:.4f}",
            "seconds"
        )

        print(
            "Ollama Duration:",
            f"{ollama_duration:.4f}",
            "seconds"
        )

        print(
            "Prompt Tokens:",
            prompt_tokens
        )

        print(
            "Output Tokens:",
            output_tokens
        )

        print(
            "Relevant Terms:",
            found_terms
        )

        print(
            "Security Analysis Relevance: PASS"
        )

        print("\nGenerated Analysis:")
        print(response.answer)

    # ----------------------------------------------------------
    # Step 15 — Calculate performance summary
    # ----------------------------------------------------------

    print("\n" + "=" * 70)
    print("PERFORMANCE SUMMARY")
    print("=" * 70)

    average_retrieval = (
        sum(
            result["retrieval_time"]
            for result in results
        )
        / len(results)
    )

    average_prompt = (
        sum(
            result["prompt_time"]
            for result in results
        )
        / len(results)
    )

    average_llm = (
        sum(
            result["llm_time"]
            for result in results
        )
        / len(results)
    )

    average_ollama = (
        sum(
            result["ollama_duration"]
            for result in results
        )
        / len(results)
    )

    print(
        "Queries Tested:",
        len(results)
    )

    print(
        "Average Retrieval Time:",
        f"{average_retrieval:.4f}",
        "seconds"
    )

    print(
        "Average Prompt Build Time:",
        f"{average_prompt:.4f}",
        "seconds"
    )

    print(
        "Average LLM Wall Time:",
        f"{average_llm:.4f}",
        "seconds"
    )

    print(
        "Average Ollama Duration:",
        f"{average_ollama:.4f}",
        "seconds"
    )

    print(
        "All Queries Relevant:",
        all(
            len(result["relevant_terms"]) >= 2
            for result in results
        )
    )

    # ----------------------------------------------------------
    # Step 16 — Cleanup
    # ----------------------------------------------------------

    print("\n[8] Cleaning test databases...")

    log_database.clear()
    knowledge_database.clear()

    print("Cleanup: PASS")

    # ----------------------------------------------------------
    # Final result
    # ----------------------------------------------------------

    print("\n" + "=" * 70)
    print("END-TO-END SECURITY ANALYSIS PERFORMANCE TEST PASSED")
    print("=" * 70)


# --------------------------------------------------------------
# Entry Point
# --------------------------------------------------------------

if __name__ == "__main__":
    main()