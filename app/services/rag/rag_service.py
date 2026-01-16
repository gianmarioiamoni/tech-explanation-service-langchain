# app/services/rag/rag_service.py
#
# Service for RAG-enabled explanations
#
# Responsibilities:
# - Retrieve relevant documents
# - Generate context-aware explanations using preconfigured LCEL chains
# - Decide fallback to generic explanation if no documents match

from typing import List, Optional, Tuple
import logging
from app.services.rag.rag_indexer import RAGIndexer
from app.services.rag.rag_chains_lcel import get_chain
from app.services.explanation.output_formatter import OutputFormatter

logger = logging.getLogger(__name__)

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
        from app.services.explanation.explanation_service import ExplanationService
        self.explanation_service = ExplanationService()  # For generic LLM fallback

    # -------------------------------
    # Context-aware explanation (non-streaming)
    # -------------------------------
    def explain_topic(self, topic: str, strategy: str = "document_stuff") -> Tuple[str, str]:
        # Generate a topic explanation using RAG if possible (non-streaming)
        #
        # Logic flow:
        # 1. Check: documents uploaded in vectorstore?
        # 2. Yes → Retrieve relevant chunks
        #    - Relevant chunks found? → Use RAG chain
        #    - No relevant chunks? → Use generic LLM chain
        # 3. No → Use generic LLM chain
        #
        # Args:
        #     topic: User-provided technical topic
        #     strategy: RAG strategy ("document_stuff" or "map_reduce")
        #
        # Returns:
        #     Tuple of (explanation_text, mode)
        #     mode: "rag" if using documents, "generic" if using general knowledge

        # Step 1: Check if vectorstore has any documents
        if not self.has_documents():
            # No documents uploaded → Generic LLM chain
            logger.info(f"🌐 Topic '{topic}': Using GENERIC LLM (no documents uploaded)")
            print(f"🌐 Mode: GENERIC LLM | Reason: No documents uploaded | Topic: '{topic}'")
            return self._explain_generic(topic), "generic"

        # Step 2: Retrieve relevant documents
        docs = self.indexer.retrieve(topic)
        
        if not docs:
            # No relevant chunks found → Generic LLM chain
            logger.info(f"🌐 Topic '{topic}': Using GENERIC LLM (no relevant chunks found)")
            print(f"🌐 Mode: GENERIC LLM | Reason: Topic not covered in documents | Topic: '{topic}'")
            return self._explain_generic(topic), "generic"

        # Step 3: Relevant chunks found → Use RAG chain
        logger.info(f"🧠 Topic '{topic}': Using RAG (found {len(docs)} relevant chunks)")
        print(f"\n{'='*60}")
        print(f"🧠 Mode: RAG | Chunks: {len(docs)} | Topic: '{topic}'")
        print(f"{'='*60}")
        
        # Show retrieved context for debugging
        print(f"📄 Retrieved Context:")
        for i, doc in enumerate(docs, 1):
            preview = doc.page_content[:150].replace('\n', ' ')
            source = doc.metadata.get('source', 'unknown')
            print(f"  [{i}] {source}: {preview}...")
        print(f"{'='*60}\n")
        
        chain = get_chain(strategy)
        lcel_input = {"topic": topic}
        result = chain.invoke(lcel_input)
        
        return result, "rag"  # Already sanitized by chain
    
    # -------------------------------
    # Context-aware explanation (STREAMING)
    # -------------------------------
    def explain_topic_stream(self, topic: str, strategy: str = "document_stuff"):
        # Generate a topic explanation using RAG if possible (with streaming)
        #
        # Yields chunks of text as they are generated for real-time display
        #
        # Args:
        #     topic: User-provided technical topic
        #     strategy: RAG strategy ("document_stuff" or "map_reduce")
        #
        # Yields:
        #     Tuple of (accumulated_text, mode)
        #     mode: "rag" if using documents, "generic" if using general knowledge
        
        # Step 1: Check if vectorstore has any documents
        if not self.has_documents():
            # No documents uploaded → Generic LLM chain (streaming)
            logger.info(f"🌐 Topic '{topic}': Using GENERIC LLM (no documents uploaded)")
            print(f"🌐 Mode: GENERIC LLM | Reason: No documents uploaded | Topic: '{topic}'")
            accumulated = ""
            for chunk in self.explanation_service.explain_stream(topic):
                accumulated = chunk  # Already accumulated by explain_stream
                yield accumulated, "generic"
            return
        
        # Step 2: Retrieve relevant documents
        docs = self.indexer.retrieve(topic)
        
        if not docs:
            # No relevant chunks found → Generic LLM chain (streaming)
            logger.info(f"🌐 Topic '{topic}': Using GENERIC LLM (no relevant chunks found)")
            print(f"🌐 Mode: GENERIC LLM | Reason: Topic not covered in documents | Topic: '{topic}'")
            accumulated = ""
            for chunk in self.explanation_service.explain_stream(topic):
                accumulated = chunk  # Already accumulated by explain_stream
                yield accumulated, "generic"
            return
        
        # Step 3: Relevant chunks found → Use RAG chain (streaming)
        logger.info(f"🧠 Topic '{topic}': Using RAG (found {len(docs)} relevant chunks)")
        print(f"\n{'='*60}")
        print(f"🧠 Mode: RAG | Chunks: {len(docs)} | Topic: '{topic}'")
        print(f"{'='*60}")
        
        # Show retrieved context for debugging
        print(f"📄 Retrieved Context:")
        for i, doc in enumerate(docs, 1):
            preview = doc.page_content[:150].replace('\n', ' ')
            source = doc.metadata.get('source', 'unknown')
            print(f"  [{i}] {source}: {preview}...")
        print(f"{'='*60}\n")
        
        chain = get_chain(strategy)
        lcel_input = {"topic": topic}
        
        # Stream chunks from RAG chain
        accumulated = ""
        for chunk in chain.stream(lcel_input):
            accumulated += chunk
            yield accumulated, "rag"

    def _explain_generic(self, topic: str) -> str:
        # Fallback to generic LLM explanation (no RAG)
        #
        # Args:
        #     topic: User-provided technical topic
        #
        # Returns:
        #     Sanitized explanation text
        
        from app.services.explanation.explanation_service import ExplanationService
        explanation_service = ExplanationService()
        accumulated = ""
        for chunk in explanation_service.explain_stream(topic):
            accumulated = chunk  # Already accumulated by stream
        return self.formatter.sanitize_output(accumulated)

    def has_documents(self) -> bool:
        # Check if vectorstore has any indexed documents
        #
        # Returns:
        #     True if documents exist, False otherwise
        
        try:
            # Check if collection has any documents
            # Use Chroma's internal collection count
            collection = self.indexer.vstore._collection
            count = collection.count()
            logger.info(f"📊 Vectorstore check: {count} documents indexed")
            print(f"📊 Vectorstore contains {count} documents")
            return count > 0
        except Exception as e:
            logger.warning(f"⚠️ Error checking documents: {e}")
            print(f"⚠️ Error checking vectorstore: {e}")
            return False

    # -------------------------------
    # Helper: add document from file
    # -------------------------------
    def add_document(self, file_path: str):
        # Load, split, and add a document from a file path
        #
        # Args:
        #     file_path: Path to document file (PDF, TXT, DOCX)
        
        # Load documents from file
        docs = self.indexer.load_documents([file_path])
        
        # Split into chunks
        chunks = self.indexer.split_documents(docs)
        
        # Add to vectorstore
        self.indexer.add_documents(chunks)

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
