# app/services/rag/rag_retriever.py
#
# Service to handle retrieval for RAG using LCEL
#
# Responsibilities:
# - Retrieve relevant document chunks
# - Return them for downstream generation
# - Designed to integrate with LCEL RAG pipeline

from langchain_core.runnables import Runnable, RunnableLambda
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
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

    def __init__(self, vectorstore_path: str = "./chroma_db", top_k: int = 5, embedding_model: str = "text-embedding-3-small"):
        self.vectorstore_path = vectorstore_path
        self.top_k = top_k
        # Initialize embeddings (MUST match RAGIndexer embeddings)
        self.embeddings = OpenAIEmbeddings(model=embedding_model)
        # Initialize Chroma vectorstore with same embeddings
        self.vstore = Chroma(persist_directory=vectorstore_path, embedding_function=self.embeddings)

    def invoke(self, query: str, config=None) -> list[Document]:
        # Retrieve documents from vectorstore
        # (Compatible with LCEL Runnable interface)
        #
        # Args:
        #     query: user question or topic
        #     config: optional RunnableConfig (for LCEL compatibility)
        #
        # Returns:
        #     List of top_k Document objects

        if not query:
            return []

        # Use as retriever
        retriever = self.vstore.as_retriever(search_type="similarity", search_kwargs={"k": self.top_k})
        results = retriever.invoke(query, config=config)
        return results

    def retrieve_runnable(self) -> RunnableLambda:
        # Return a RunnableLambda for use in LCEL chains
        #
        # Returns:
        #     RunnableLambda that retrieves documents for a given query

        return RunnableLambda(lambda query: self.invoke(query))
