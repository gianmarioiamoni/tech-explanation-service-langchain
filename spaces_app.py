# spaces_app.py
#
# Hugging Face Spaces entrypoint.
# This file exposes the Gradio application so that it can be
# automatically discovered and launched by Hugging Face Spaces.
#
# The actual UI logic lives in ui/gradio_app.py.
# This file acts as a thin adapter layer.

import base64
from pathlib import Path

from ui.gradio_app import demo

# Read logo for favicon
project_root = Path(__file__).parent
with open(project_root / "assets" / "logo.svg", "rb") as f:
    logo_base64 = base64.b64encode(f.read()).decode("utf-8")
favicon_data_uri = f"data:image/svg+xml;base64,{logo_base64}"

# Queue is already enabled in ui/gradio_app.py after event definitions

# Hugging Face Spaces expects a variable named "demo"
# or a call to demo.launch()
if __name__ == "__main__":
    # Launch without authentication - shared demo mode with usage limits
    demo.launch(
        favicon_path=str(project_root / "assets" / "logo.png")
    )
