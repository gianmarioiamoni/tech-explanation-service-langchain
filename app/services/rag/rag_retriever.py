# app/services/rag/rag_retriever.py
#
# Service for RAG retrieval
# Retrieves context from indexed documents and generates context-aware responses

from typing import List, Optional
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI, OpenAI
from langchain_core.prompts import PromptTemplate
# NOTE: LLMChain removed in LangChain 1.0+ - Use LCEL (pipe operator) instead
# Old: chain = LLMChain(llm=llm, prompt=prompt)
# New: chain = prompt | llm
from app.services.rag.rag_indexer import RAGIndexer
from langchain_core.documents import Document


class RAGRetrieverService:
    # Service to handle retrieval-augmented generation (RAG)
    #
    # Attributes:
    #     indexer: RAGIndexer instance
    #     vectorstore: Chroma vectorstore from indexer
    #     llm: LLM instance (OpenAI by default)
    #
    # Methods:
    #     retrieve(topic) -> List[Document]
    #     generate_response(topic) -> str
    #     has_context(topic) -> bool

    def __init__(self, indexer: Optional[RAGIndexer] = None):
        # Initialize the retriever with a RAGIndexer
        #
        self.indexer = indexer or RAGIndexer()
        self.vectorstore: Chroma = self.indexer.vectorstore
        self.llm = OpenAI(temperature=0.2)

        # Define a simple RAG prompt template
        self.prompt_template = PromptTemplate(
            input_variables=["topic", "context_docs"],
            template=(
                "You are a technical assistant.\n"
                "Use the following context to answer the user's question.\n\n"
                "Context:\n{context_docs}\n\n"
                "Question: {topic}\n"
                "Answer:"
            )
        )
        # Use LCEL (LangChain Expression Language) pipe operator
        self.chain = self.prompt_template | self.llm

    # -------------------------------
    # Retrieval
    # -------------------------------
    def retrieve(self, topic: str, top_k: int = 5) -> List[Document]:
        # Retrieve the most relevant documents for the topic
        #
        # Args:
        #     topic: the user's query
        #     top_k: number of top documents to retrieve
        #
        if not self.vectorstore:
            return []

        retriever = self.vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": top_k})
        docs = retriever.get_relevant_documents(topic)
        return docs

    def has_context(self, topic: str, top_k: int = 5) -> bool:
        # Check if there is sufficient context for the topic
        docs = self.retrieve(topic, top_k)
        return len(docs) > 0

    # -------------------------------
    # Generation
    # -------------------------------
    def generate_response(self, topic: str, top_k: int = 5) -> str:
        # Generate a response using retrieved context
        #
        docs = self.retrieve(topic, top_k)

        if not docs:
            return ""  # No context found

        # Concatenate documents content
        context_text = "\n\n".join([doc.page_content for doc in docs])

        # Run LCEL chain (use invoke instead of run)
        answer = self.chain.invoke({"topic": topic, "context_docs": context_text})
        return answer
