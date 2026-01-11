# Gradio UI for Tech Explanation Service

This directory contains the Gradio-based web interface for the Tech Explanation Service.

## Features

- **Simple Interface**: Clean, user-friendly interface built with Gradio
- **Real-time Explanations**: Generate technical explanations on-demand
- **Responsive Design**: Works on desktop and mobile devices

## Running the UI

### From the project root:

```bash
# Activate the environment
conda activate tech-explain

# Run the Gradio app
python ui/gradio_app.py
```

The app will be available at: **http://127.0.0.1:7860**

### Stopping the app:

Press `Ctrl+C` in the terminal where the app is running.

## Architecture

The Gradio UI follows clean architecture principles:

- **Thin Presentation Layer**: UI only handles user input/output
- **Service Delegation**: All business logic is delegated to `TechExplanationService`
- **No LLM Logic**: No direct LLM or prompt construction in the UI layer

## File Structure

```
ui/
├── gradio_app.py    # Main Gradio application
└── README.md        # This file
```

## Dependencies

- `gradio>=6.0` - Web UI framework
- All other dependencies from the main project

## Usage

1. Enter a technical topic in the text box (e.g., "Few-Shot Prompting in LangChain")
2. Click the "Explain" button
3. Wait for the AI-generated explanation to appear
4. The explanation is generated using GPT-4o with few-shot prompting

## Environment Variables

The app requires the same environment variables as the main service:

- `OPENAI_API_KEY` - Your OpenAI API key (set in `.env` file)

## Future Enhancements

Potential improvements:
- Add history of explanations
- Export explanations to markdown/PDF
- Add model selection dropdown
- Add temperature control slider
- Add streaming response support

