# app/services/rag/rag_chains_lcel.py
#
# LCEL chains configurations for RAG strategies
#
# Responsibilities:
# - Provide preconfigured LCEL chains for RAG
# - Support strategies like document-stuffing, map-reduce, or custom context injection
# - Properly separate topic and context using LCEL operators
# - Can be reused by RAGService or other services

from langchain_core.runnables import RunnablePassthrough, RunnableLambda, RunnableParallel
from langchain_core.documents import Document
from typing import List

from app.services.rag.rag_retriever import RAGRetrieverService as RAGRetriever
from app.services.explanation.output_formatter import OutputFormatter
from app.chains.tech_explanation_chain import tech_explanation_chain
from app.chains.rag_explanation_chain import rag_explanation_chain

# -------------------------------
# Initialize shared components
# -------------------------------
retriever = RAGRetriever()
formatter = OutputFormatter()

# -------------------------------
# Helper functions for document formatting
# -------------------------------
def format_docs(docs: List[Document]) -> str:
    # Format retrieved documents into a single context string
    #
    # Args:
    #     docs: List of Document objects from retriever
    #
    # Returns:
    #     Formatted context string
    
    if not docs:
        return ""
    
    return "\n\n".join([doc.page_content for doc in docs])

# -------------------------------
# Document Stuffing Chain (Proper LCEL)
# -------------------------------
# This strategy retrieves documents and injects them as context
# Input: {"topic": str}
# Output: sanitized explanation string
#
# LCEL Flow:
# 1. Pass topic through unchanged
# 2. Retrieve docs for topic in parallel
# 3. Format docs as context string
# 4. Pass both topic and context to RAG prompt
# 5. LLM generates response
# 6. Sanitize output

def build_document_stuff_chain():
    # Build proper LCEL chain with separated topic and context
    
    return (
        # Step 1: Create parallel branches
        {
            "context": RunnableLambda(lambda x: x["topic"]) | retriever | RunnableLambda(format_docs),
            "topic": RunnableLambda(lambda x: x["topic"])  # Pass through
        }
        # Step 2: Pass to RAG chain (expects {topic, context})
        | rag_explanation_chain
        # Step 3: Sanitize output
        | RunnableLambda(formatter.sanitize_output)
    )

document_stuff_chain = build_document_stuff_chain()

# -------------------------------
# Map-Reduce Chain (Proper LCEL)
# -------------------------------
# This strategy processes each document separately, then combines results
# Input: {"topic": str}
# Output: sanitized explanation string
#
# LCEL Flow:
# 1. Retrieve documents
# 2. Map: Process each doc individually with topic
# 3. Reduce: Combine all results
# 4. Sanitize output

def build_map_reduce_chain():
    # Build proper LCEL chain for map-reduce strategy
    
    def map_reduce_logic(input_dict):
        # Map-reduce implementation
        topic = input_dict["topic"]
        docs = retriever.invoke(topic)
        
        if not docs:
            # No docs: fallback to generic chain
            return tech_explanation_chain.invoke({"topic": topic})
        
        # MAP: Process each document separately
        results = []
        for doc in docs:
            # Each doc gets its own context
            result = rag_explanation_chain.invoke({
                "topic": topic,
                "context": doc.page_content
            })
            results.append(result)
        
        # REDUCE: Combine results
        combined = "\n\n---\n\n".join(results)
        return combined
    
    return (
        RunnableLambda(map_reduce_logic)
        | RunnableLambda(formatter.sanitize_output)
    )

map_reduce_chain = build_map_reduce_chain()

# -------------------------------
# Expose chain getters
# -------------------------------
def get_chain(strategy: str = "document_stuff"):
    # Return a preconfigured LCEL chain based on strategy name
    #
    # Args:
    #     strategy: "document_stuff" or "map_reduce"
    #
    # Returns:
    #     RunnableSequence LCEL chain ready for invocation
    if strategy == "map_reduce":
        return map_reduce_chain
    # Default strategy
    return document_stuff_chain
