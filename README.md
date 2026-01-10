
### Design Principles

- Prompts are treated as **first-class code**
- Prompt logic is **isolated and testable**
- The service layer is **LLM-agnostic**
- Notebook usage is limited to exploration and tuning

---

## Prompting Strategy

The prompt is composed of three distinct layers:

1. **System Message**
   - Defines the role, tone, and global rules
2. **Few-Shot Examples**
   - Provides curated Human → AI examples to guide style and structure
3. **Human Message**
   - Accepts the real user input dynamically

This structure ensures:
- Higher response consistency
- Better format control
- Easier maintenance and iteration

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

## Environment Setup

### 1. Create a Conda Environment

```bash
conda create -n tech-explain python=3.11
conda activate tech-explain
