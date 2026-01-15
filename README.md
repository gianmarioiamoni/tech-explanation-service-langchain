---
title: Tech Explanation Service
emoji: 🤖
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: 6.3.0
app_file: spaces_app.py
pinned: false
python_version: 3.11
---

# 🤖 Tech Explanation Service

A **production-ready** AI service that generates clear, structured technical explanations using **LangChain LCEL**, **OpenAI GPT-4o-mini**, and **Conditional RAG** (Retrieval Augmented Generation).

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3110/)
[![LangChain](https://img.shields.io/badge/🦜_LangChain-1.0+-green.svg)](https://python.langchain.com/)
[![Gradio 6.3](https://img.shields.io/badge/gradio-6.3.0-orange.svg)](https://gradio.app/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## ✨ Key Features

### 🎯 Conditional RAG (Hybrid AI)
- **Intelligent Context Switching**: Uses uploaded documentation when relevant, falls back to general LLM knowledge when not
- **Always Provides Value**: Never returns "I don't know" — adapts to available context
- **Production Pattern**: Same approach used by ChatGPT Enterprise, Notion AI, and GitHub Copilot

### 📚 Advanced History Management
- **Persistent Storage**: Chat history saved to Hugging Face Hub with write permissions
- **Smart Organization**: Chats grouped by creation day with newest-first ordering
- **Full-Text Search**: Find past explanations instantly
- **Date-Based Aggregation**: View all chats from a specific day
- **Selective Deletion**: Remove unwanted conversations

### 🚀 Real-Time Streaming
- **Progressive Output**: See explanations generate token-by-token
- **LCEL-Powered**: Efficient streaming using LangChain Expression Language
- **Stop Control**: Interrupt generation mid-stream with dedicated stop button

### 📥 Multi-Format Export
- **Download Options**: Export explanations as Markdown, PDF, or Word (DOCX)
- **Professional Formatting**: Clean layouts with proper typography (ReportLab for PDF)
- **One-Click Export**: Easy format selection with accordion menu

### 🧠 Multi-Topic Processing
- **Batch Explanations**: Handle multiple topics in one request (comma-separated)
- **Aggregation Modes**:
  - **Single Chat**: Combine all topics into one explanation
  - **Separate Chats**: Save each topic independently
- **Visual Separators**: Clear topic boundaries with dividers

### 🏗️ Clean Architecture
- **Domain-Driven Design**: Services organized by domain (explanation, history, RAG)
- **Separation of Concerns**: UI callbacks separated from business logic
- **Modular Components**: Easy to extend and maintain
- **Type Safety**: Strict typing with Python type hints

---

## 🔄 How Conditional RAG Works

Our system implements **Conditional RAG** (also known as **Hybrid RAG**), an intelligent pattern that dynamically chooses the best generation strategy:

```
User Topic
   ↓
┌─────────────────────────────────────────┐
│  Are documents uploaded?                │
└─────────────────────────────────────────┘
   ↓                           ↓
  YES                         NO
   │                           │
   │                           ↓
   │                 ┌─────────────────┐
   │                 │  Generic LLM    │
   │                 │  (Pure GPT-4o)  │
   │                 └─────────────────┘
   ↓
┌─────────────────────────────────────────┐
│  Is topic covered in documents?         │
│  (Semantic search for relevant chunks)  │
└─────────────────────────────────────────┘
   ↓                           ↓
  YES                         NO
   │                           │
   ↓                           ↓
┌─────────────┐      ┌─────────────────┐
│  RAG Chain  │      │  Generic LLM    │
│  (Context)  │      │  (Pure GPT-4o)  │
└─────────────┘      └─────────────────┘
   ↓                           ↓
   └──────────┬────────────────┘
              ↓
    ┌──────────────────┐
    │  Always Useful!  │
    └──────────────────┘
```

### Why This Matters

| Scenario | Traditional RAG | Our Conditional RAG |
|----------|----------------|---------------------|
| No documents uploaded | ❌ "No information available" | ✅ Provides general knowledge |
| Documents uploaded, topic not covered | ❌ "Topic not found" | ✅ Provides general knowledge |
| Documents uploaded, topic covered | ✅ Uses context | ✅ Uses context |

**Key Insight:** The fallback to "pure" LLM is **not a bug** — it's a **deliberate feature** that ensures the system always provides useful answers.

This is the same pattern used by:
- **ChatGPT Enterprise** (custom docs + general knowledge)
- **Notion AI** (workspace context + general answers)
- **GitHub Copilot** (project code + general programming)
- **Perplexity AI** (web sources + LLM reasoning)

---

## 🎬 Quick Start

### Try It Now (Hugging Face Spaces)

Visit the [live demo](https://huggingface.co/spaces/YOUR_USERNAME/tech-explanation-service) — no setup required!

### Local Development

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/tech-explanation-service-langchain.git
cd tech-explanation-service-langchain

# Create conda environment
conda create -n tech-explain python=3.11
conda activate tech-explain

# Install dependencies
pip install -r requirements.txt

# Set OpenAI API key
echo "OPENAI_API_KEY=your-key-here" > .env

# Run locally
python spaces_app.py
```

Access at `http://localhost:7860`

---

## 📖 Usage Guide

### Basic Explanation
1. Enter a technical topic (e.g., "Docker containers")
2. Click **✨ Explain** or press Enter
3. Watch the explanation stream in real-time

### Using RAG (Context-Aware Explanations)
1. Click **📂 Upload Technical Documents**
2. Select PDF, TXT, or DOCX files
3. Wait for indexing confirmation
4. Ask questions about the uploaded content
5. System automatically uses context when relevant

### Multi-Topic Queries
```
Input: "Docker, Kubernetes, Microservices"
```
- **Aggregate Mode**: Single combined explanation
- **Separate Mode**: Three individual chats saved

### Managing History
- **Search**: Type keywords in the search box
- **Load Chat**: Select from dropdown (grouped by date)
- **Delete**: Choose chat and click delete
- **View Day**: Click on a date to see all chats from that day

### Exporting Content
1. Generate an explanation
2. Click **📥 Download**
3. Select format: **Markdown**, **PDF**, or **Word**
4. File downloads automatically

---

## 🏗️ Architecture

### Project Structure

```
tech-explanation-service-langchain/
├── app/
│   ├── chains/                          # LCEL chain definitions
│   │   ├── tech_explanation_chain.py   # Generic LLM chain
│   │   └── rag_explanation_chain.py    # RAG-enhanced chain
│   ├── services/
│   │   ├── explanation/                 # Core explanation logic
│   │   │   ├── explanation_service.py  # LLM streaming service
│   │   │   └── output_formatter.py     # Text sanitization
│   │   ├── history/                     # History management
│   │   │   ├── history_repository.py   # CRUD operations (HF Hub)
│   │   │   ├── history_query_service.py # Search & filtering
│   │   │   ├── history_formatter.py    # UI formatting
│   │   │   └── history_loader.py       # Chat loading
│   │   └── rag/                         # RAG system
│   │       ├── rag_service.py          # Orchestrator (Conditional RAG)
│   │       ├── rag_indexer.py          # Document ingestion & vectorstore
│   │       ├── rag_retriever.py        # Semantic search
│   │       └── rag_chains_lcel.py      # RAG LCEL chains
│   └── main.py                          # FastAPI app (optional)
├── ui/
│   ├── gradio_app.py                    # Main UI definition
│   ├── callbacks/                       # Event handlers
│   │   ├── explanation_callbacks.py    # Explain logic
│   │   ├── history_callbacks.py        # History operations
│   │   ├── search_callbacks.py         # Search logic
│   │   ├── download_callbacks.py       # Export logic
│   │   └── upload_callbacks.py         # RAG document upload
│   └── utils/
│       ├── ui_messages.py              # UI text constants
│       └── document_exporter.py        # Export to PDF/MD/DOCX
├── spaces_app.py                        # Hugging Face Spaces entrypoint
├── requirements.txt                     # Python dependencies
└── README.md                            # This file
```

### Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **LLM** | OpenAI GPT-4o-mini | Fast, cost-effective reasoning |
| **Framework** | LangChain 1.0+ (LCEL) | Chain orchestration & streaming |
| **Vector Store** | Chroma | Document embeddings & retrieval |
| **Embeddings** | OpenAI text-embedding-3-small | Semantic search |
| **UI** | Gradio 6.3 | Interactive web interface |
| **API** | FastAPI 0.115.5 | Backend service (optional) |
| **Storage** | Hugging Face Hub | Persistent chat history |
| **Document Processing** | pypdf, docx2txt, ReportLab | PDF/DOCX parsing & generation |

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# Required
OPENAI_API_KEY=sk-...

# Optional (for history persistence on HF Spaces)
HF_TOKEN=hf_...
```

### LLM Settings

Configure in `app/chains/tech_explanation_chain.py`:

```python
llm = ChatOpenAI(
    model="gpt-4o-mini",      # Model name
    temperature=0.2,          # Consistency (0-1)
    streaming=True,           # Enable streaming
)
```

### RAG Settings

Configure in `app/services/rag/rag_indexer.py`:

```python
# Chunking
chunk_size=500              # Tokens per chunk
chunk_overlap=50            # Overlap between chunks

# Embeddings
embedding_model="text-embedding-3-small"

# Retrieval
top_k=5                     # Chunks to retrieve
```

---

## 🧪 Testing

### Run All Tests

```bash
pytest tests/ -v
```

### Test Coverage

```bash
pytest --cov=app --cov=ui tests/
```

### Manual Testing

```bash
# Test basic explanation
python -m app.chains.tech_explanation_chain

# Test RAG system
python -m app.services.rag.rag_service

# Test UI
python spaces_app.py
```

---

## 🚀 Deployment

### Hugging Face Spaces

1. **Create Space** on [Hugging Face](https://huggingface.co/new-space)
   - SDK: Gradio
   - Python: 3.11

2. **Configure Secrets**
   ```
   OPENAI_API_KEY=sk-...
   HF_TOKEN=hf_... (with WRITE permissions for history)
   ```

3. **Push Code**
   ```bash
   git remote add hf https://huggingface.co/spaces/YOUR_USERNAME/SPACE_NAME
   git push hf main
   ```

4. **Auto-Deploy** — Space builds automatically!

### Local Server (FastAPI)

```bash
# Development
uvicorn app.main:app --reload

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

Access API docs at `http://localhost:8000/docs`

---

## 📊 Performance

### Latency Benchmarks

| Operation | Avg Time | Notes |
|-----------|----------|-------|
| Basic explanation | 2-4s | First token ~500ms |
| RAG retrieval | 0.5-1s | Semantic search |
| RAG explanation | 3-5s | Retrieval + generation |
| History load | 0.2-0.5s | From HF Hub |
| Document indexing | 2-10s | Depends on file size |

### Cost Estimates (per 1000 requests)

| Scenario | Tokens Used | Cost (USD) |
|----------|-------------|------------|
| Generic explanation (avg) | ~500 output | $0.15 |
| RAG explanation (avg) | ~800 output | $0.24 |
| Embeddings (per document) | ~1000 | $0.0001 |

**Note:** Using GPT-4o-mini keeps costs ~15x lower than GPT-4.

---

## 🛠️ Advanced Features

### Custom RAG Strategies

Implement in `app/services/rag/rag_chains_lcel.py`:

```python
# Document Stuffing (default)
# Combines all chunks into single context
result = rag_service.explain_topic(topic, strategy="document_stuff")

# Map-Reduce
# Processes each chunk separately, then combines
result = rag_service.explain_topic(topic, strategy="map_reduce")
```

### Extending with New Services

1. Create service in `app/services/your_domain/`
2. Add callback in `ui/callbacks/your_callbacks.py`
3. Register in `ui/gradio_app.py`
4. Update `app/services/__init__.py`

### Custom Output Formats

Add exporters in `ui/utils/document_exporter.py`:

```python
@staticmethod
def export_to_html(topic: str, content: str) -> str:
    # Your implementation
    pass
```

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Follow the code style (see `.editorconfig`)
4. Add tests for new features
5. Commit with clear messages
6. Push and create a Pull Request

### Development Guidelines

- **Type Safety**: Use type hints everywhere
- **Docstrings**: Document all public functions
- **SOLID Principles**: Keep functions focused and modular
- **Testing**: Maintain >80% coverage
- **Comments**: Use `#` for single/multi-line comments (no `"""` for comments)

---

## 📚 Documentation

- **LCEL Guide**: [LangChain Expression Language](https://python.langchain.com/docs/expression_language/)
- **Gradio Docs**: [Gradio Documentation](https://gradio.app/docs/)
- **OpenAI API**: [OpenAI Platform](https://platform.openai.com/docs)
- **Chroma**: [Chroma Vector Database](https://docs.trychroma.com/)

---

## 🐛 Troubleshooting

### Common Issues

**Q: "OPENAI_API_KEY not found"**
```bash
# Solution: Create .env file
echo "OPENAI_API_KEY=your-key" > .env
```

**Q: "Cannot import module 'app'"**
```bash
# Solution: Install in editable mode
pip install -e .
```

**Q: "History not persisting on HF Spaces"**
```bash
# Solution: 
# 1. Create HF_TOKEN secret in Space settings
# 2. Ensure token has WRITE permissions
# 3. Create empty history.json file in repo root
```

**Q: "Chroma deprecation warning"**
```bash
# Solution: Already fixed! Using langchain-chroma>=1.1.0
```

**Q: "RAG returns generic answers"**
```
# This is intentional! Conditional RAG feature:
# - If topic not in docs → Generic LLM (by design)
# - If docs uploaded → Checks relevance first
# - Always provides useful answer
```

---

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details

---

## 👤 Author

**Gianmario Iamoni**
- Portfolio Project demonstrating:
  - LangChain LCEL best practices
  - Production-ready RAG implementation
  - Clean architecture principles
  - Real-time streaming UX
  - Enterprise-grade error handling

---

## 🌟 Acknowledgments

- [LangChain](https://langchain.com/) for the amazing framework
- [OpenAI](https://openai.com/) for GPT-4o-mini
- [Hugging Face](https://huggingface.co/) for hosting and Hub storage
- [Gradio](https://gradio.app/) for the intuitive UI framework

---

## 📈 Roadmap

- [ ] Multi-language support (translations)
- [ ] Custom prompt templates via UI
- [ ] Support for more document formats (HTML, Markdown files)
- [ ] Advanced RAG: Re-ranking, hybrid search
- [ ] User authentication & personalized history
- [ ] API rate limiting & usage analytics
- [ ] Voice input/output support
- [ ] Dark mode UI theme

---

**⭐ If you find this project useful, please consider starring it on GitHub!**
