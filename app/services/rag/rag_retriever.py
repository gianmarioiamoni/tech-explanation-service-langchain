# app/services/rag/rag_retriever.py
#
# Service to handle retrieval for RAG using LCEL
#
# Responsibilities:
# - Retrieve relevant document chunks
# - Return them for downstream generation
# - Designed to integrate with LCEL RAG pipeline

from langchain_core.runnables import Runnable, RunnableLambda
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

class RAGRetrieverService(Runnable):
    # Runnable service to retrieve document chunks based on query
    #
    # Args:
    #     vectorstore_path: path to Chroma vectorstore
    #     top_k: number of documents to return
    #
    # Returns:
    #     List of relevant Documents

    def __init__(self, vectorstore_path: str = "./chroma_db", top_k: int = 5):
        self.vectorstore_path = vectorstore_path
        self.top_k = top_k
        # Initialize Chroma vectorstore (embedding function already saved)
        self.vstore = Chroma(persist_directory=vectorstore_path)

    def invoke(self, query: str) -> list[Document]:
        # Retrieve documents from vectorstore
        #
        # Args:
        #     query: user question or topic
        #
        # Returns:
        #     List of top_k Document objects

        if not query:
            return []

        # Use as retriever
        retriever = self.vstore.as_retriever(search_type="similarity", search_kwargs={"k": self.top_k})
        results = retriever.get_relevant_documents(query)
        return results

    def retrieve_runnable(self) -> RunnableLambda:
        # Return a RunnableLambda for use in LCEL chains
        #
        # Returns:
        #     RunnableLambda that retrieves documents for a given query

        return RunnableLambda(lambda query: self.invoke(query))
