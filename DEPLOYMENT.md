# Deployment to Hugging Face Spaces

This document explains how to deploy the Tech Explanation Service to Hugging Face Spaces.

## Files for Deployment

### `spaces_app.py`
Main entrypoint for Hugging Face Spaces. This file:
- Imports the Gradio `demo` object from `ui/gradio_app.py`
- Exposes it for Hugging Face Spaces to discover
- Was renamed from `app.py` to avoid circular import conflicts with the `app/` package directory

### Why not `app.py`?

The file was originally named `app.py`, but this caused a **circular import error** because Python would find `app.py` (the file) before `app/` (the directory) when resolving imports like `from app.services import ...`.

Renaming to `spaces_app.py` resolves this conflict while maintaining clarity about its purpose.

## Deployment Steps

### 1. Create a new Space on Hugging Face

Visit https://huggingface.co/spaces and create a new Gradio Space.

### 2. Configure the Space

In your Space settings, you'll need to:

1. Set the SDK to **Gradio**
2. Set Python version to **3.11+**

### 3. Add Environment Variables

In the Space settings, add:
- `OPENAI_API_KEY` = Your OpenAI API key

### 4. Push the code

```bash
git remote add hf https://huggingface.co/spaces/YOUR_USERNAME/tech-explanation-service
git push hf main
```

### 5. Hugging Face will automatically:

- Install dependencies from `pyproject.toml`
- Discover and launch `spaces_app.py` (if it finds `demo` variable)
- Start the Gradio app

## Alternative: Manual Launch

If Hugging Face doesn't auto-discover, you can create an `app.py` file that just imports from `spaces_app.py`:

```python
from spaces_app import demo

if __name__ == "__main__":
    demo.launch()
```

But this is usually not necessary.

## File Structure for Deployment

```
tech-explanation-service-langchain/
├── spaces_app.py          # HF Spaces entrypoint
├── pyproject.toml         # Dependencies
├── .env.example           # Template for environment variables
├── app/                   # Core application package
│   ├── services/
│   ├── prompts/
│   └── ...
├── ui/                    # Gradio UI
│   └── gradio_app.py
└── README.md
```

## Testing Locally

Before deploying, test locally:

```bash
conda activate tech-explain
python spaces_app.py
```

Then visit http://127.0.0.1:7860

## Notes

- The `.env` file is NOT pushed to Hugging Face (it's in `.gitignore`)
- Set environment variables in the Space settings instead
- The app/ directory structure is preserved and works correctly
- All imports resolve properly without circular dependencies

