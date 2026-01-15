# app/services/rag/rag_indexer.py
#
# Service to handle indexing of documents for RAG
#
# Responsibilities:
# - Load documents from disk
# - Split documents into chunks
# - Create embeddings
# - Store in vectorstore (Chroma)
# - Designed to be used with LCEL

from typing import List
from langchain_core.runnables import Runnable, RunnableParallel
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter, MarkdownHeaderTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader
import os
import shutil

class RAGIndexer:
    # Service for indexing documents for RAG retrieval
    #
    # Args:
    #     vectorstore_path: Path to store/reload Chroma vectorstore
    #     embedding_model: OpenAI embedding model
    #
    # Returns:
    #     None

    def __init__(self, vectorstore_path: str = "./chroma_db", embedding_model: str = "text-embedding-3-small"):
        # Initialize Chroma vectorstore and embeddings
        self.vectorstore_path = vectorstore_path
        self.embeddings = OpenAIEmbeddings(model=embedding_model)

        if os.path.exists(vectorstore_path):
            # Load existing vectorstore
            self.vstore = Chroma(persist_directory=vectorstore_path, embedding_function=self.embeddings)
        else:
            # Initialize new vectorstore
            self.vstore = Chroma(persist_directory=vectorstore_path, embedding_function=self.embeddings)

    def load_documents(self, paths: List[str]) -> List[Document]:
        # Load documents from given file paths
        #
        # Args:
        #     paths: list of file paths (pdf, txt, md)
        #
        # Returns:
        #     List of Document objects

        docs = []
        for path in paths:
            ext = os.path.splitext(path)[1].lower()
            if ext == ".pdf":
                loader = PyPDFLoader(path)
            else:
                loader = TextLoader(path)
            docs.extend(loader.load())
        return docs

    def split_documents(self, docs: List[Document], method: str = "character") -> List[Document]:
        # Split documents into chunks
        #
        # Args:
        #     docs: list of Document objects
        #     method: splitting method (character or markdown)
        #
        # Returns:
        #     List of chunked Document objects

        if method == "markdown":
            splitter = MarkdownHeaderTextSplitter(chunk_size=500, chunk_overlap=50)
        else:
            splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)

        all_chunks = []
        for doc in docs:
            all_chunks.extend(splitter.split_documents([doc]))
        return all_chunks

    def add_documents(self, docs: List[Document]):
        # Add chunked documents to vectorstore
        # (Auto-persisted by langchain-chroma to disk)
        #
        # Args:
        #     docs: list of chunked Document objects
        #
        # Returns:
        #     None

        if docs:
            self.vstore.add_documents(docs)
            # Note: langchain-chroma auto-persists to persist_directory
            # No need to call .persist() manually

    def retrieve(self, query: str, top_k: int = 5) -> List[Document]:
        # Retrieve relevant documents from vectorstore
        #
        # Args:
        #     query: search query or topic
        #     top_k: number of documents to retrieve
        #
        # Returns:
        #     List of relevant Document objects

        if not query or not query.strip():
            return []
        
        retriever = self.vstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": top_k}
        )
        return retriever.invoke(query)

    def clear(self):
        # Clear the vectorstore by deleting all indexed documents
        #
        # Returns:
        #     None

        # Check current count before clearing
        try:
            count_before = self.vstore._collection.count()
            print(f"🗑️ Clearing vectorstore: {count_before} documents indexed")
        except:
            count_before = "unknown"
            print(f"🗑️ Clearing vectorstore...")

        # Get all document IDs and delete them
        try:
            # Get all IDs from the collection
            collection = self.vstore._collection
            all_docs = collection.get()
            if all_docs and 'ids' in all_docs and all_docs['ids']:
                doc_ids = all_docs['ids']
                # Delete all documents by ID
                collection.delete(ids=doc_ids)
                print(f"✅ Deleted {len(doc_ids)} documents from collection")
            else:
                print(f"✅ Collection was already empty")
        except Exception as e:
            print(f"⚠️ Could not delete documents via API: {e}")
            print(f"⚠️ Falling back to directory deletion...")
            
            # Fallback: Delete the entire directory
            if os.path.exists(self.vectorstore_path):
                shutil.rmtree(self.vectorstore_path)
                print(f"✅ Deleted vectorstore directory")
                
                # Reinitialize
                self.vstore = Chroma(
                    persist_directory=self.vectorstore_path,
                    embedding_function=self.embeddings
                )
        
        # Confirm it's empty
        try:
            count_after = self.vstore._collection.count()
            print(f"✅ Vectorstore cleared: {count_before} → {count_after} documents")
            if count_after == 0:
                print(f"✅ Vectorstore is now empty")
            else:
                print(f"⚠️ Warning: Vectorstore still has {count_after} documents!")
        except Exception as e:
            print(f"⚠️ Could not verify count: {e}")
