---
title: Tech Explanation Service
emoji: 🤖
sdk: gradio
sdk_version: 4.31.0
app_file: spaces_app.py
pinned: false
---

# Tech Explanation Service  
### Structured Prompting and Few-Shot Chat Patterns with LangChain

A **production-oriented Python service** that demonstrates how to design, structure, and operationalize **chat-based prompting** and **few-shot techniques** using LangChain and OpenAI models.

This project represents an interactive AI-powered service that explains complex 
technical topics using structured prompting, Few-Shot learning, and LangChain.

Built as a portfolio-ready project to demonstrate:
- Prompt engineering best practices
- Service-oriented LLM design
- Interactive Gradio-based UI

## Why this project

This project demonstrates how to design an LLM-based application
with clean separation of concerns, reusable prompt templates,
and a production-ready deployment model.

It is intentionally built as a service rather than a notebook
to reflect real-world usage.

---

## Overview

The Tech Explanation Service generates **clear, consistent, and high-quality technical explanations** for a given topic by leveraging:

- Chat-native large language models
- Structured prompt composition
- Few-shot prompting for style and format control
- A clean separation between prompt logic, business logic, and infrastructure

The repository showcases **how GenAI components should be engineered in real-world systems**, with an emphasis on maintainability, extensibility, and clarity of design.

Typical use cases include:
- Technical documentation assistants
- Developer support tools
- AI-powered knowledge services
- GenAI backend components for SaaS platforms

---

## Key Features

- Chat-native prompting via `ChatPromptTemplate`
- Explicit separation of `System`, `Human`, and `AI` messages
- Few-shot chat prompting using `FewShotChatMessagePromptTemplate`
- Prompt logic treated as **first-class, versionable code**
- Service-layer abstraction decoupled from prompt construction
- Ready for extension to RAG, tool calling, and dynamic example selection

---

## Architecture

The project follows a layered and modular architecture:

- **Application Layer**
  - `main.py`  
    FastAPI entrypoint exposing the service via HTTP.

- **Service Layer**
  - `services/tech_explanation_service.py`  
    Encapsulates business logic and LLM invocation.
  - `services/llm_factory.py`  
    Centralized configuration and instantiation of the LLM.

- **Prompt Layer**
  - `prompts/tech_explanation_prompt.py`  
    Defines the structured chat prompt, including system rules and few-shot examples.

- **Schema Layer**
  - `schemas/explanation.py`  
    Defines request and response models using Pydantic.

- **Exploration Layer**
  - `notebooks/`  
    Used only for prompt experimentation and tuning (non-production).


### Design Principles

- Prompts are treated as **code**, not static strings
- Prompt construction is isolated from application logic
- The service layer is **LLM-agnostic**
- Notebooks are used only for exploration and prompt tuning
- The structure supports prompt iteration without impacting consumers

---

## Prompting Strategy

The prompt is composed of three clearly separated layers:

1. **System Message**
   - Defines the role, tone, and global behavioral constraints of the model

2. **Few-Shot Examples**
   - Curated Human → AI message pairs that demonstrate the desired explanation style and structure

3. **Human Message**
   - The actual user input, injected dynamically at runtime

This approach provides:
- Improved response consistency
- Better control over output structure
- Easier long-term maintenance and prompt evolution

---

## Tech Stack

- Python 3.11
- LangChain
- OpenAI Chat Models
- FastAPI
- Pydantic
- Anaconda (environment management)
- Jupyter (exploration only)

---

## Environment Setup (local development)

### 1. Create a Conda Environment

```bash
conda create -n tech-explain python=3.11
conda activate tech-explain
```

### 2. Install dependences and run the app
```bash
pip install -r requirements.txt
python spaces_app.py
```



