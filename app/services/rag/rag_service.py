# app/services/rag/rag_service.py
#
# Service for RAG-enabled explanations
#
# Responsibilities:
# - Retrieve relevant documents
# - Generate context-aware explanations using preconfigured LCEL chains
# - Decide fallback to generic explanation if no documents match

from typing import List, Optional
from app.services.rag.rag_indexer import RAGIndexer
from app.services.rag.rag_chains_lcel import get_chain
from app.services.explanation.output_formatter import OutputFormatter

class RAGService:
    # RAG Service using LCEL chains for retrieval-augmented generation
    #
    # Args:
    #     None
    #
    # Returns:
    #     None

    def __init__(self):
        self.indexer = RAGIndexer()              # Handles indexing & vector store
        self.formatter = OutputFormatter()       # Sanitizes output

    # -------------------------------
    # Context-aware explanation
    # -------------------------------
    def explain_topic(self, topic: str, strategy: str = "document_stuff") -> str:
        # Generate a topic explanation using RAG if possible
        #
        # Args:
        #     topic: User-provided technical topic
        #     strategy: RAG strategy ("document_stuff" or "map_reduce")
        #
        # Returns:
        #     Sanitized explanation text

        # Step 1: Retrieve relevant documents
        docs = self.indexer.retrieve(topic)
        if not docs:
            # Fallback: no relevant docs, return generic explanation
            from app.services.explanation.explanation_service import ExplanationService
            explanation_service = ExplanationService()
            accumulated = ""
            for chunk in explanation_service.explain_stream(topic):
                accumulated += chunk
            return self.formatter.sanitize_output(accumulated)

        # Step 2: Select LCEL chain based on strategy
        chain = get_chain(strategy)

        # Step 3: Prepare input for LCEL chain
        # Input includes topic + retrieved documents
        lcel_input = {"topic": topic}

        # Step 4: Invoke chain (document-stuffing or map-reduce)
        result = chain.invoke(lcel_input)

        # Step 5: Return sanitized output
        return self.formatter.sanitize_output(result)

    # -------------------------------
    # Helper: add documents to index
    # -------------------------------
    def add_documents(self, documents: List[dict]):
        # Adds documents to RAG indexer
        #
        # Args:
        #     documents: List of dicts {"content": str, "metadata": dict}
        self.indexer.add_documents(documents)

    # -------------------------------
    # Helper: clear index
    # -------------------------------
    def clear_index(self):
        # Clears the RAG index
        self.indexer.clear()
