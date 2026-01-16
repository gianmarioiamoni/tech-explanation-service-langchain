# Test Suite Documentation

## 📋 Overview

Comprehensive test suite for the Tech Explanation Service, covering:
- ✅ LCEL chains (generic & RAG)
- ✅ Explanation services (streaming, formatting)
- ✅ RAG services (indexing, retrieval, relevance filtering)
- ✅ History services (persistence, search, formatting)
- ✅ Shared services (singleton pattern)

## 🚀 Running Tests

### Run All Tests
```bash
python -m pytest tests/ -v
```

### Run Specific Test Files
```bash
# Chain tests
python -m pytest tests/test_chain.py -v

# Explanation & formatting
python -m pytest tests/test_explanation_service.py -v

# RAG functionality
python -m pytest tests/test_rag_service.py -v

# History management
python -m pytest tests/test_history_services.py -v

# Singleton pattern
python -m pytest tests/test_shared_services.py -v
```

### Run Tests Without API Calls
Some tests require OpenAI API (LLM/embedding calls). To run only unit tests that don't require API:

```bash
python -m pytest tests/test_history_services.py tests/test_shared_services.py tests/test_explanation_service.py::TestOutputFormatter -v
```

### Run with Coverage (if pytest-cov installed)
```bash
python -m pytest tests/ --cov=app --cov=ui --cov-report=html
```

## 📊 Test Structure

```
tests/
├── __init__.py
├── test_chain.py                  # LCEL chain integration tests
├── test_explanation_service.py    # Explanation & output formatting
├── test_rag_service.py           # RAG indexing, retrieval, conditional logic
├── test_history_services.py      # History management (CRUD, search, format)
├── test_shared_services.py       # Singleton pattern verification
└── README.md                     # This file
```

## 🧪 Test Coverage

### 1. `test_chain.py` - LCEL Chains
**Class: TestGenericChain**
- ✅ `test_chain_invoke_returns_string` - Generic chain returns valid response
- ✅ `test_chain_stream_yields_chunks` - Streaming produces progressive chunks
- ✅ `test_chain_handles_simple_topic` - Single-word topics are handled

**Class: TestRAGChain**
- ✅ `test_rag_chain_requires_topic_and_context` - RAG chain accepts topic + context
- ✅ `test_rag_chain_stream_with_context` - RAG streaming works

### 2. `test_explanation_service.py` - Explanation & Formatting
**Class: TestExplanationService**
- ✅ `test_explain_stream_yields_accumulated_text` - Streaming accumulates text
- ✅ `test_explain_multiple_stream_yields_topic_pairs` - Multi-topic streaming

**Class: TestOutputFormatter**
- ✅ `test_sanitize_output_removes_markdown` - Markdown removal
- ✅ `test_sanitize_output_removes_code_blocks` - Code block removal
- ✅ `test_parse_topics_splits_comma_separated` - Topic parsing
- ✅ `test_parse_topics_handles_extra_whitespace` - Whitespace handling
- ✅ `test_aggregate_topics_output_combines_topics` - Topic aggregation
- ✅ **`test_aggregate_avoids_topic_duplication`** - **Prevents topic duplication (Bug Fix #1)**

### 3. `test_rag_service.py` - RAG Functionality
**Class: TestRAGIndexer**
- ✅ `test_load_documents_from_txt_file` - Document loading
- ✅ `test_split_documents_creates_chunks` - Document chunking
- ✅ `test_retrieve_returns_list` - Retrieval returns list

**Class: TestRAGService**
- ✅ `test_has_documents_returns_false_when_empty` - Empty vectorstore detection
- ✅ `test_has_documents_returns_true_after_adding` - Document presence detection
- ✅ `test_explain_topic_uses_generic_when_no_docs` - Fallback to generic LLM
- ✅ `test_explain_topic_uses_rag_with_relevant_docs` - RAG mode activation
- ✅ **`test_explain_topic_uses_generic_for_irrelevant_topic`** - **Relevance filtering (Bug Fix #2)**
- ✅ `test_explain_topic_stream_yields_progressive_chunks` - Streaming RAG
- ✅ `test_clear_index_empties_vectorstore` - Index clearing

### 4. `test_history_services.py` - History Management
**Class: TestHistoryFormatter**
- ✅ `test_truncate_shortens_long_text` - Text truncation
- ✅ `test_truncate_preserves_short_text` - Short text preservation
- ✅ `test_parse_topic_from_selection_extracts_topic` - Topic extraction
- ✅ `test_parse_topic_from_selection_ignores_date_headers` - Date filtering
- ✅ `test_create_history_choices_generates_dropdown_choices` - Dropdown formatting
- ✅ `test_create_delete_choices_formats_for_deletion` - Delete dropdown

**Class: TestHistoryQueryService**
- ✅ `test_search_history_finds_matching_topics` - Search functionality
- ✅ `test_search_history_is_case_insensitive` - Case-insensitive search
- ✅ `test_search_history_returns_empty_for_no_match` - No-match handling
- ✅ `test_group_by_date_groups_chats_by_day` - Date grouping

**Class: TestHistoryLoader**
- ✅ `test_find_chat_by_topic_returns_matching_chat` - Chat retrieval
- ✅ `test_find_chat_by_topic_returns_none_for_no_match` - Not-found handling
- ✅ `test_get_chats_by_date_returns_chats_for_date` - Date filtering
- ✅ `test_format_chats_for_date_combines_chats` - Multi-chat formatting

### 5. `test_shared_services.py` - Singleton Pattern
**Class: TestSharedServices**
- ✅ `test_rag_service_is_singleton_across_modules` - RAGService singleton
- ✅ `test_document_registry_is_singleton` - DocumentRegistry singleton
- ✅ `test_chroma_persistence_is_singleton` - ChromaPersistence singleton
- ✅ `test_shared_service_state_is_consistent` - State consistency

## 🐛 Bug Fixes Verified by Tests

### Bug #1: Topic Duplication
**Test:** `test_aggregate_avoids_topic_duplication`  
**File:** `tests/test_explanation_service.py`  
**Verifies:** Topic name doesn't appear twice at start of output

### Bug #2: RAG Used for Irrelevant Topics
**Test:** `test_explain_topic_uses_generic_for_irrelevant_topic`  
**File:** `tests/test_rag_service.py`  
**Verifies:** System uses generic LLM when documents are irrelevant (distance > 1.5)

## ⚙️ Configuration

Pytest configuration is in `pytest.ini`:
- Test discovery: `test_*.py` files, `Test*` classes, `test_*` functions
- Test path: `tests/`
- Markers: `unit`, `integration`, `slow`, `rag`, `ui`

## 📝 Notes

### API-Dependent Tests
Tests that call OpenAI API may fail due to:
- Network issues
- Rate limiting
- API key not set

These failures are expected in CI/CD without API keys.

### ChromaDB Tests
RAG tests use temporary vectorstores (`test_chroma_db/`) that are automatically cleaned up.

### Singleton Tests
Shared service tests verify that callbacks use the same instance across modules, preventing stale state bugs.

## 🎯 Best Practices

1. **Run tests before commits**
2. **Run API-free tests in CI/CD** (faster, no external dependencies)
3. **Run full test suite locally** (includes LLM integration tests)
4. **Update tests when adding features**
5. **Add regression tests for bug fixes**

## 📈 Test Metrics

- **Total Tests:** 41
- **Unit Tests (API-free):** 24
- **Integration Tests (API):** 17
- **Bug Regression Tests:** 2
- **Coverage Target:** >80% (core services)

