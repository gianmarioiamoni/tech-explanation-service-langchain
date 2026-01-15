# RAG (Retrieval Augmented Generation) Architecture

## 📋 Overview

This module implements a complete RAG system for context-aware technical explanations using LangChain LCEL (LangChain Expression Language).

## 🔄 Logic Flow

```
User Topic
   ↓
┌─────────────────────────────┐
│ RAGService.explain_topic()  │
└─────────────────────────────┘
   ↓
┌─────────────────────────────┐
│ Check: Documents Uploaded?  │
└─────────────────────────────┘
   ↓                    ↓
  YES                  NO
   ↓                    ↓
┌──────────────────┐  ┌─────────────────────┐
│ Retrieve Chunks  │  │ Generic LLM Chain   │
└──────────────────┘  │ (tech_explanation)  │
   ↓                  └─────────────────────┘
┌──────────────────┐
│ Relevant Chunks? │
└──────────────────┘
   ↓          ↓
  YES        NO
   ↓          ↓
┌────────┐  ┌─────────────────────┐
│ RAG    │  │ Generic LLM Chain   │
│ Chain  │  │ (tech_explanation)  │
└────────┘  └─────────────────────┘
   ↓                    ↓
┌─────────────────────────────┐
│    Sanitized Output         │
└─────────────────────────────┘
```

## 🏗️ Architecture

### Core Components

#### 1. **RAGIndexer** (`rag_indexer.py`)
Handles document ingestion and vectorization.

**Responsibilities:**
- Load documents (PDF, TXT, DOCX)
- Split into chunks
- Create embeddings (OpenAI)
- Store in Chroma vectorstore

**Key Methods:**
- `load_documents(paths)` - Load files
- `split_documents(docs)` - Chunk text
- `add_documents(chunks)` - Index in vectorstore
- `retrieve(query, top_k)` - Semantic search
- `clear()` - Delete all indexed docs

---

#### 2. **RAGRetrieverService** (`rag_retriever.py`)
LCEL-compatible retriever for semantic search.

**Responsibilities:**
- Retrieve relevant document chunks
- Return as LCEL Runnable

**Key Methods:**
- `invoke(query)` - Retrieve documents
- `retrieve_runnable()` - Return as `RunnableLambda` for LCEL chains

---

#### 3. **RAG Chains** (`rag_chains_lcel.py`)
LCEL chains for RAG strategies.

**Strategies:**

##### **Document Stuffing** (Default)
```python
{
    "context": topic → retriever → format_docs,
    "topic": topic (passthrough)
}
→ rag_prompt
→ llm
→ sanitize
```

##### **Map-Reduce**
```python
topic → retrieve docs
→ MAP: process each doc separately
→ REDUCE: combine results
→ sanitize
```

---

#### 4. **RAGService** (`rag_service.py`)
High-level orchestrator for RAG operations.

**Responsibilities:**
- Decide: RAG vs Generic LLM
- Execute appropriate chain
- Manage document lifecycle

**Key Methods:**
- `explain_topic(topic, strategy)` - Main entry point
- `add_document(file_path)` - Upload & index file
- `clear_index()` - Remove all docs
- `has_documents()` - Check if docs exist

---

## 🔗 LCEL Chain Details

### Base Chains

#### **Generic LLM Chain** (`tech_explanation_chain.py`)
```python
Input: {"topic": str}
Output: str

prompt | llm | StrOutputParser
```

#### **RAG-Enhanced Chain** (`rag_explanation_chain.py`)
```python
Input: {"topic": str, "context": str}
Output: str

rag_prompt | llm | StrOutputParser
```

### RAG Strategies

#### **Document Stuffing Chain**
Combines all retrieved docs into a single context.

```python
Input: {"topic": str}
Flow:
  1. topic → retriever → format_docs → "context"
  2. topic (passthrough) → "topic"
  3. {topic, context} → rag_chain → sanitize
Output: str (sanitized)
```

**LCEL Implementation:**
```python
{
    "context": RunnableLambda(extract_topic) | retriever | RunnableLambda(format_docs),
    "topic": RunnableLambda(extract_topic)
}
| rag_explanation_chain
| RunnableLambda(sanitize)
```

#### **Map-Reduce Chain**
Processes each doc separately, then combines.

```python
Input: {"topic": str}
Flow:
  1. topic → retriever → docs
  2. MAP: for each doc → rag_chain(topic, doc)
  3. REDUCE: combine all results
  4. sanitize
Output: str (sanitized)
```

---

## 🎯 Usage Examples

### 1. Add Documents
```python
from app.services.rag import RAGService

rag = RAGService()
rag.add_document("path/to/doc.pdf")
```

### 2. Explain with RAG
```python
# Automatically decides: RAG or Generic
result = rag.explain_topic("What is Docker?")
```

### 3. Choose Strategy
```python
# Document stuffing (default)
result = rag.explain_topic("Kubernetes", strategy="document_stuff")

# Map-reduce
result = rag.explain_topic("Kubernetes", strategy="map_reduce")
```

### 4. Clear Index
```python
rag.clear_index()
```

---

## 📦 Dependencies

- `langchain-chroma` - Vectorstore
- `langchain-openai` - Embeddings & LLM
- `langchain-core` - LCEL operators
- `langchain-community` - Document loaders
- `langchain-text-splitters` - Text chunking

---

## 🔧 Configuration

### Vectorstore
- **Type**: Chroma
- **Persist**: `./chroma_db/`
- **Embeddings**: `text-embedding-3-small`

### LLM
- **Model**: `gpt-4o-mini`
- **Temperature**: `0.2`
- **Streaming**: `True`

### Chunking
- **Chunk Size**: `500` tokens
- **Chunk Overlap**: `50` tokens

---

## 🚀 Integration with UI

See `ui/callbacks/upload_callbacks.py` for Gradio integration:
- `upload_documents()` - File upload handler
- `clear_rag_index()` - Clear button handler

---

## ✅ Best Practices

1. **Always check `has_documents()`** before assuming RAG is available
2. **Use appropriate strategy**:
   - `document_stuff` for consolidated context
   - `map_reduce` for diverse/conflicting sources
3. **Clear index** when switching domains/topics
4. **Monitor chunk quality** - adjust `chunk_size` if needed

---

## 📝 Notes

- Empty vectorstore → Automatic fallback to generic LLM
- No relevant chunks → Automatic fallback to generic LLM
- All prompts configured to **avoid Markdown** (plain text only)
- Output is **always sanitized** before returning

