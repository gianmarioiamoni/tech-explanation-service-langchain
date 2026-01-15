# app/services/rag/rag_chains_lcel.py
#
# LCEL chains configurations for RAG strategies
#
# Responsibilities:
# - Provide preconfigured LCEL chains for RAG
# - Support strategies like document-stuffing, map-reduce, or custom context injection
# - Can be reused by RAGService or other services

from langchain_core.runnables import RunnableSequence, RunnableMap, RunnableParallel, Runnable
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
document_stuff_chain = RunnableSequence(
    # Step 1: Retrieve documents relevant to the topic
    [
        retriever.retrieve_runnable(),  # Returns a list of documents
        # Step 2: Combine retrieved docs into a single context string
        Runnable(lambda docs: "\n\n".join([doc["content"] for doc in docs])),
        # Step 3: Call LLM with topic + combined context
        Runnable(lambda context: tech_explanation_chain.invoke({"topic": context})),  # tech_explanation_chain from your app
        # Step 4: Sanitize output
        Runnable(formatter.sanitize_output),
    ]
)

# -------------------------------
# Map-Reduce Chain
# -------------------------------
# This strategy processes each retrieved document separately and then combines answers
map_reduce_chain = RunnableSequence(
    [
        retriever.retrieve_runnable(),
        # Step 1: Process each document individually (map)
        RunnableParallel(
            Runnable(lambda doc: tech_explanation_chain.invoke({"topic": doc["content"]})),
            return_exceptions=False
        ),
        # Step 2: Aggregate individual answers (reduce)
        Runnable(lambda answers: "\n\n".join(answers)),
        # Step 3: Sanitize final output
        Runnable(formatter.sanitize_output),
    ]
)

# -------------------------------
# Expose chain getters
# -------------------------------
def get_chain(strategy: str = "document_stuff") -> RunnableSequence:
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
