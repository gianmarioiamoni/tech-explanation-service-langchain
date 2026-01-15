# RAG (Retrieval Augmented Generation) Architecture

## 📋 Overview

This module implements a **Conditional RAG** (also known as **Hybrid RAG**) system for context-aware technical explanations using LangChain LCEL (LangChain Expression Language).

### What is Conditional RAG?

Conditional RAG is an intelligent pattern used in real-world production systems that dynamically chooses the best generation strategy based on available context:

- **If the topic is covered in uploaded documents** → Use RAG chain (context-aware)
- **If the topic is NOT covered (or no documents exist)** → Use generic LLM chain

**💡 Key Insight:** The fallback to "pure" LLM is **not a workaround** — it's a **deliberate feature**. This ensures the system always provides useful answers, whether or not relevant documentation is available.

### Benefits of Conditional RAG

1. **Always Useful**: Never returns "no answer" — provides generic knowledge when docs don't cover the topic
2. **Cost Efficient**: Doesn't waste tokens on irrelevant context
3. **Better Quality**: Uses specialized prompts for each scenario (RAG vs generic)
4. **Production-Ready**: Same pattern used by ChatGPT, Notion AI, and other enterprise systems

## 🔄 Conditional RAG Logic Flow

This is the **intentional decision logic** that powers our Hybrid RAG system:

```
User Topic
   ↓
┌─────────────────────────────────────────────────┐
│         RAGService.explain_topic()              │
│     (Conditional RAG Decision Point)            │
└─────────────────────────────────────────────────┘
   ↓
┌─────────────────────────────────────────────────┐
│ Decision 1: Are documents uploaded?             │
│ (has_documents())                               │
└─────────────────────────────────────────────────┘
   ↓                                    ↓
  YES                                  NO
   │                                    │
   │                                    ↓
   │                          ┌─────────────────────┐
   │                          │ 🎯 Generic LLM      │
   │                          │ (Pure Knowledge)    │
   │                          │                     │
   │                          │ Reason: No docs     │
   │                          │ uploaded yet        │
   │                          └─────────────────────┘
   ↓
┌─────────────────────────────────────────────────┐
│ Decision 2: Topic covered in documents?         │
│ (retriever.invoke() → relevant chunks?)         │
└─────────────────────────────────────────────────┘
   ↓                                    ↓
  YES                                  NO
   │                                    │
   ↓                                    ↓
┌─────────────────────┐      ┌─────────────────────┐
│ 📚 RAG Chain        │      │ 🎯 Generic LLM      │
│ (Context-Aware)     │      │ (Pure Knowledge)    │
│                     │      │                     │
│ Uses: topic +       │      │ Reason: Topic not   │
│       context       │      │ covered in docs     │
└─────────────────────┘      └─────────────────────┘
   ↓                                    ↓
   └────────────────┬───────────────────┘
                    ↓
          ┌─────────────────────┐
          │  Sanitized Output   │
          │  (Always useful!)   │
          └─────────────────────┘
```

### Decision Logic Summary

| Condition | Action | Chain Used | Reason |
|-----------|--------|------------|--------|
| No documents uploaded | Generic LLM | `tech_explanation_chain` | Nothing to retrieve from |
| Documents uploaded, but topic not covered | Generic LLM | `tech_explanation_chain` | **Feature**: Provide answer anyway |
| Documents uploaded AND topic covered | RAG | `rag_explanation_chain` | **Feature**: Use context for accuracy |

**Key Takeaway:** Every path leads to a useful answer. The system is **never stuck**.

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

## 🎯 Why Conditional RAG is a Feature, Not a Workaround

### The Problem with "RAG-Only" Systems

Traditional RAG systems fail when:
- No documents are uploaded yet
- The user asks about topics outside the documentation
- Retrieved chunks are irrelevant

Result: **"I don't have enough information"** → Poor UX

### Our Solution: Conditional RAG

```
┌──────────────────────────────────────────────┐
│  "Explain Docker"                            │
└──────────────────────────────────────────────┘
   ↓
┌──────────────────────────────────────────────┐
│  Documents about Kubernetes uploaded         │
│  Retrieval: No Docker chunks found           │
└──────────────────────────────────────────────┘
   ↓
┌──────────────────────────────────────────────┐
│  🎯 FEATURE: Use generic LLM knowledge       │
│  Answer provided: "Docker is a platform..."  │
└──────────────────────────────────────────────┘
```

**This is intentional behavior, not a bug!**

### Real-World Examples

This is the same pattern used by:
- **ChatGPT Enterprise**: Custom docs + general knowledge
- **Notion AI**: Workspace context + general answers
- **GitHub Copilot**: Project code + general programming knowledge
- **Perplexity AI**: Web sources + LLM reasoning

### When Each Mode is Used

| User Question | Documents | Retrieval Result | Mode Used | Why |
|---------------|-----------|------------------|-----------|-----|
| "Explain Docker" | None uploaded | N/A | Generic LLM | No docs available |
| "Explain Docker" | K8s docs uploaded | No relevant chunks | Generic LLM | **Topic not covered** |
| "Explain Docker" | Docker docs uploaded | 5 relevant chunks | RAG | **Topic covered** |
| "What is a container?" | Docker docs uploaded | 3 relevant chunks | RAG | Related to docs |

---

## ✅ Best Practices

1. **Trust the decision logic** - Don't force RAG when generic is better
2. **Use appropriate strategy**:
   - `document_stuff` for consolidated context
   - `map_reduce` for diverse/conflicting sources
3. **Clear index** when switching domains/topics
4. **Monitor chunk quality** - adjust `chunk_size` if needed
5. **Don't over-index** - Too many docs can dilute relevance

---

## 📝 Implementation Notes

### Automatic Behavior (No Configuration Needed)

- ✅ Empty vectorstore → Generic LLM
- ✅ No relevant chunks → Generic LLM  
- ✅ Relevant chunks found → RAG chain
- ✅ All transitions are seamless
- ✅ User never sees an error

### Prompt Configuration

- All prompts (both RAG and generic) configured to **avoid Markdown** (plain text only)
- Output is **always sanitized** before returning
- Consistent formatting regardless of which chain is used

### Performance Characteristics

| Scenario | Retrieval Cost | LLM Cost | Latency |
|----------|---------------|----------|---------|
| No docs | ❌ Skip | ✅ Standard | Fast |
| Docs, no match | ✅ Small | ✅ Standard | Medium |
| Docs, with match | ✅ Small | ✅ Standard + context | Medium-High |

**Optimization:** Failed retrievals don't waste LLM tokens on irrelevant context.

---

## 🚀 Advantages of Our Conditional RAG Implementation

### 1. **Always Provides Value**
```
Traditional RAG: "Topic not found in documents" ❌
Our System:     "Here's what I know about that topic" ✅
```

### 2. **Cost Efficient**
- Doesn't inject irrelevant context (saves tokens)
- Only uses RAG when beneficial
- Generic LLM for out-of-scope queries

### 3. **Better User Experience**
- No "I don't know" responses
- Seamless transitions between modes
- User doesn't need to know which mode is active

### 4. **Production-Grade Reliability**
- Handles empty vectorstores gracefully
- Handles partial document coverage
- Handles completely unrelated queries

### 5. **Extensibility**
- Easy to add more decision criteria
- Can implement confidence thresholds
- Can add user override options

### Example Conversation Flow

```
User: "What is Docker?"
System: (No docs) → Generic LLM
Output: "Docker is a platform for developing..."

[User uploads Docker documentation]

User: "What is Docker?"
System: (Docs + match) → RAG chain
Output: "According to your documentation, Docker is..."

User: "What is Kubernetes?"
System: (Docs but no match) → Generic LLM
Output: "Kubernetes is an orchestration platform..."

[User uploads Kubernetes documentation]

User: "What is Kubernetes?"
System: (Docs + match) → RAG chain
Output: "According to your documentation, Kubernetes is..."
```

**The system adapts to available context automatically.** 🎯

