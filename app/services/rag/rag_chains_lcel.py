# app/services/rag/rag_chains_lcel.py
#
# LCEL chains configurations for RAG strategies
#
# Responsibilities:
# - Provide preconfigured LCEL chains for RAG
# - Support strategies like document-stuffing, map-reduce, or custom context injection
# - Can be reused by RAGService or other services

from langchain_core.runnables import RunnableSequence, RunnableMap, RunnableParallel, RunnableLambda
from app.services.rag.rag_retriever import RAGRetrieverService as RAGRetriever
from app.services.explanation.output_formatter import OutputFormatter
from app.chains.tech_explanation_chain import tech_explanation_chain

# -------------------------------
# Initialize shared components
# -------------------------------
retriever = RAGRetriever()
formatter = OutputFormatter()

# -------------------------------
# Document Stuffing Chain
# -------------------------------
# This strategy injects all retrieved documents as context before calling the LLM
def build_document_stuff_chain():
    # Build a chain that retrieves documents and uses them as context
    #
    # Input: {"topic": str}
    # Output: sanitized explanation string
    
    def retrieve_and_format(input_dict):
        # Retrieve documents and format them with the topic
        topic = input_dict["topic"]
        docs = retriever.invoke(topic)
        
        if not docs:
            # No relevant docs, just use topic
            context = topic
        else:
            # Combine docs into context
            context = "\n\n".join([doc.page_content for doc in docs])
            context = f"Context:\n{context}\n\nTopic: {topic}"
        
        return {"topic": context}
    
    return (
        RunnableLambda(retrieve_and_format)
        | tech_explanation_chain
        | RunnableLambda(formatter.sanitize_output)
    )

document_stuff_chain = build_document_stuff_chain()

# -------------------------------
# Map-Reduce Chain
# -------------------------------
# This strategy processes each retrieved document separately and then combines answers
def build_map_reduce_chain():
    # Build a chain that processes each document separately then combines
    #
    # Input: {"topic": str}
    # Output: sanitized explanation string
    
    def retrieve_and_process(input_dict):
        # Retrieve documents and process each one
        topic = input_dict["topic"]
        docs = retriever.invoke(topic)
        
        if not docs:
            # No relevant docs, just use topic
            return tech_explanation_chain.invoke({"topic": topic})
        
        # Process each document with the LLM
        results = []
        for doc in docs:
            doc_context = f"Context:\n{doc.page_content}\n\nTopic: {topic}"
            result = tech_explanation_chain.invoke({"topic": doc_context})
            results.append(result)
        
        # Combine all results
        combined = "\n\n".join(results)
        return combined
    
    return (
        RunnableLambda(retrieve_and_process)
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
