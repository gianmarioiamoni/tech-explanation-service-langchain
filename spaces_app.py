# spaces_app.py
#
# Hugging Face Spaces entrypoint with FastAPI + OAuth or Basic Auth fallback.
# This file can run in two modes:
# 1. OAuth mode: If OAuth providers are configured, uses FastAPI with OAuth
# 2. Basic Auth mode: Falls back to simple Gradio Basic Auth if no OAuth configured
#
# The actual UI logic lives in ui/gradio_app.py.
# This file acts as a thin adapter layer.

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from ui.gradio_app import demo
from app.auth.oauth_providers import has_oauth_configured

# Check if OAuth is configured
if has_oauth_configured():
    # ============================================================================
    # MODE 1: FastAPI + OAuth (Production with Google/GitHub/HF OAuth)
    # ============================================================================
    print("\n" + "="*60)
    print("🔐 OAuth Mode: Using FastAPI with OAuth providers")
    print("="*60 + "\n")
    
    import uvicorn
    import gradio as gr
    from app.fastapi_app import app, get_current_user
    
    # Mount Gradio app with OAuth authentication dependency
    app = gr.mount_gradio_app(
        app, 
        demo, 
        path="/gradio",
        auth_dependency=get_current_user
    )
    
    # Expose app for HF Spaces
    # HF Spaces will automatically run this with uvicorn
    if __name__ == "__main__":
        # Local development
        uvicorn.run(app, host="0.0.0.0", port=7860)
else:
    # ============================================================================
    # MODE 2: Basic Auth Fallback (Demo/Portfolio without OAuth setup)
    # ============================================================================
    print("\n" + "="*60)
    print("⚠️  Basic Auth Mode: No OAuth providers configured")
    print("📝 Set GOOGLE_CLIENT_ID, GITHUB_CLIENT_ID, or HF_CLIENT_ID to enable OAuth")
    print("🔐 Using simple Basic Auth: demo / portfolio2026")
    print("="*60 + "\n")
    
    # Queue is already enabled in ui/gradio_app.py after event definitions
    # Hugging Face Spaces expects a variable named "demo"
    if __name__ == "__main__":
        # Basic Authentication for demo/portfolio
        demo.launch(
            auth=("demo", "portfolio2026"),
            auth_message="🔐 Demo Access - Use username: demo, password: portfolio2026"
        )
