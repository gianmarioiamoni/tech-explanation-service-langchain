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

# Tech Explanation Service

A portfolio-ready LangChain service that generates clear, structured technical explanations using **few-shot prompting** and **GPT-4o**.

## Features

- 🎯 **Few-Shot Prompting**: Curated examples guide the model's response style
- 🏗️ **Clean Architecture**: Separation of concerns (prompts, services, UI)
- 🔧 **Production-Ready**: Error handling, validation, and type safety
- 📝 **Well-Documented**: Comprehensive inline documentation
- ✅ **Tested**: Full test suite included

## How to Use

1. Enter a technical topic in the text box (e.g., "REST API", "Few-Shot Prompting")
2. Click "Explain" or press Enter
3. Receive a clear, structured explanation powered by GPT-4o

## Technology Stack

- **LangChain**: Framework for LLM applications
- **OpenAI GPT-4o**: Language model
- **Gradio**: Web interface
- **FastAPI**: Backend API (available locally)
- **Python 3.11**: Programming language

## Architecture

```
app/
├── services/          # Business logic
│   ├── tech_explanation_service.py
│   └── llm_factory.py
├── prompts/           # Prompt templates
│   └── tech_explanation_prompt.py
└── main.py           # FastAPI app

ui/
└── gradio_app.py     # Gradio interface

spaces_app.py         # HF Spaces entrypoint
```

## Local Development

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/tech-explanation-service-langchain.git
cd tech-explanation-service-langchain

# Create conda environment
conda create -n tech-explain python=3.11
conda activate tech-explain

# Install dependencies
pip install -r requirements.txt

# Set your OpenAI API key
echo "OPENAI_API_KEY=your-key-here" > .env

# Run the app
python spaces_app.py
```

## Configuration

The service uses:
- **Model**: GPT-4o
- **Temperature**: 0.2 (for consistent, focused responses)
- **Prompting Strategy**: Few-shot with system message and examples

## License

MIT License

## Author

Built as a portfolio project demonstrating LangChain best practices and clean architecture principles.

