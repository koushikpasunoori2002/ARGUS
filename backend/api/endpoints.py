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
endpoints.py

Security analysis API endpoints for ARGUS.
"""

from fastapi import APIRouter, HTTPException

from backend.api.schemas import (
    AnalyzeRequest,
    AnalyzeResponse,
)

from backend.database.chroma import ChromaDatabase

from backend.rag.context import ContextBuilder
from backend.rag.retriever import Retriever
from backend.rag.retriever.related_log_retriever import RelatedLogRetriever
from backend.knowledge.knowledge_retriever import KnowledgeRetriever
from backend.llm.embeddings import EmbeddingManager
from backend.llm.generation import RAGAnalyzer


router = APIRouter()

embedding_manager = EmbeddingManager()

@router.post("/analyze", response_model=AnalyzeResponse)
def analyze(request: AnalyzeRequest):

    query = request.query.strip()

    if not query:
        raise HTTPException(
            status_code=400,
            detail="Query cannot be empty."
        )

    # ----------------------------------------------------------
    # Log retrieval
    # ----------------------------------------------------------

    log_retriever = Retriever(
        embedding_manager=embedding_manager,
        top_k=3
    )

    # ----------------------------------------------------------
    # Related log retrieval
    # ----------------------------------------------------------

    related_log_retriever = RelatedLogRetriever()

    # ----------------------------------------------------------
    # Security knowledge retrieval
    # ----------------------------------------------------------

    knowledge_database = ChromaDatabase(
        collection_name="security_knowledge"
    )

    knowledge_retriever = KnowledgeRetriever(
        database=knowledge_database,
        embedding_manager=embedding_manager,
        top_k=3
    )

    # ----------------------------------------------------------
    # Build RAG context
    # ----------------------------------------------------------

    context_builder = ContextBuilder(
        log_retriever=log_retriever,
        knowledge_retriever=knowledge_retriever,
        related_log_retriever=related_log_retriever,
        top_k_logs=3,
        top_k_knowledge=3
    )

    context = context_builder.build(
        query,
        source_id=request.source_id,
    )

    # ----------------------------------------------------------
    # Generate security analysis
    # ----------------------------------------------------------

    analyzer = RAGAnalyzer()

    response = analyzer.analyze(
        context
    )

    # ----------------------------------------------------------
    # Response metadata
    # ----------------------------------------------------------

    metadata = {
        "model": response.model,
        "log_count": len(
            context.log_results
        ),
        "related_log_count": len(
            context.related_log_results
        ),
        "knowledge_count": len(
            context.knowledge_results
        ),
        "top_k_logs": context_builder.top_k_logs,
        "top_k_knowledge": context_builder.top_k_knowledge,
        "rag": True,
    }

    # ----------------------------------------------------------
    # API response
    # ----------------------------------------------------------

    return AnalyzeResponse(
        query=query,
        answer=response.answer,
        evidence=context.log_results,
        related_log_results=context.related_log_results,
        knowledge=context.knowledge_results,
        metadata=metadata,
    )
