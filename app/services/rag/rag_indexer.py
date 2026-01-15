# app/services/rag/rag_indexer.py
#
# Service responsible for indexing documents for RAG
# Handles loading, splitting, embedding, and storing in Chroma vectorstore
#

from typing import List
from pathlib import Path
from langchain_text_splitters import CharacterTextSplitter, MarkdownHeaderTextSplitter
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document


class RAGIndexer:
    # Service to index documents for RAG retrieval
    #
    # Attributes:
    #     vectorstore: Chroma instance for embeddings storage
    #     embeddings: OpenAIEmbeddings instance
    #
    # Methods:
    #     load_documents(files) -> List[Document]
    #     split_documents(docs) -> List[Document]
    #     index_documents(docs) -> None
    #     add_documents(docs) -> None
    #     update_document(doc, doc_id) -> None
    #     delete_document(doc_id) -> None
    #     clear_index() -> None

    def __init__(self, persist_dir: str = "chroma_index"):
        # Initialize embeddings and Chroma vectorstore
        #
        # Args:
        #     persist_dir: directory to persist Chroma vectorstore
        #
        self.embeddings = OpenAIEmbeddings()
        self.persist_dir = persist_dir
        self.vectorstore = Chroma(
            persist_directory=self.persist_dir,
            embedding_function=self.embeddings
        )

    # -------------------------------
    # Document loading
    # -------------------------------
    def load_documents(self, files: List[str]) -> List[Document]:
        # Load documents from a list of file paths
        #
        # Supports PDF, DOCX, and TXT
        #
        loaded_docs = []
        for file_path in files:
            path = Path(file_path)
            if not path.exists():
                continue  # skip missing files

            # PDF loader
            if path.suffix.lower() == ".pdf":
                loader = PyPDFLoader(str(path))
            # DOCX loader
            elif path.suffix.lower() in [".docx", ".doc"]:
                loader = Docx2txtLoader(str(path))
            # TXT loader
            elif path.suffix.lower() == ".txt":
                loader = TextLoader(str(path))
            else:
                continue  # unsupported file

            docs = loader.load()
            loaded_docs.extend(docs)

        return loaded_docs

    # -------------------------------
    # Document splitting
    # -------------------------------
    def split_documents(self, docs: List[Document], method: str = "character") -> List[Document]:
        # Split loaded documents into chunks
        #
        # Args:
        #     docs: list of Documents
        #     method: "character" or "markdown"
        #
        split_docs = []
        for doc in docs:
            if method == "markdown":
                splitter = MarkdownHeaderTextSplitter(chunk_size=1000, chunk_overlap=100)
            else:
                splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)

            chunks = splitter.split_documents([doc])
            split_docs.extend(chunks)

        return split_docs

    # -------------------------------
    # Indexing / adding documents
    # -------------------------------
    def index_documents(self, docs: List[Document]):
        # Index multiple documents in the vectorstore
        #
        # Args:
        #     docs: list of Documents
        #
        self.vectorstore.add_documents(docs)
        self.vectorstore.persist()  # save to disk

    def add_documents(self, docs: List[Document]):
        # Alias for index_documents
        self.index_documents(docs)

    # -------------------------------
    # Update / delete / clear
    # -------------------------------
    def update_document(self, doc: Document, doc_id: str):
        # Update a document in vectorstore
        # Requires a unique id field in metadata
        #
        self.vectorstore.update_documents([doc], ids=[doc_id])
        self.vectorstore.persist()

    def delete_document(self, doc_id: str):
        # Delete a document from vectorstore by id
        self.vectorstore.delete(ids=[doc_id])
        self.vectorstore.persist()

    def clear_index(self):
        # Clear entire vectorstore
        self.vectorstore.delete()
        self.vectorstore.persist()
