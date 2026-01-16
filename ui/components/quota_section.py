# ui/components/quota_section.py
#
# UI components for displaying quota status.
# Shows remaining requests, tokens, and usage warnings.
#

import gradio as gr
from typing import Tuple


def create_quota_section() -> Tuple[gr.Markdown, gr.State]:
    # Create the quota status display UI section.
    #
    # Returns:
    #     Tuple of (quota_display, user_session_state)
    
    with gr.Accordion("📊 Quota Status", open=False):
        quota_display = gr.Markdown(
            value=_get_initial_quota_message(),
            label="Current Usage"
        )
    
    # User session state (stores user_id, username, quota_status)
    user_session_state = gr.State(None)
    
    return quota_display, user_session_state


def _get_initial_quota_message() -> str:
    # Get initial quota message for unauthenticated users
    #
    # Returns:
    #     Initial quota display message
    
    return """
### 🔐 Authentication Required

Please log in with your Hugging Face account to use this service.

**Daily Quota Limits:**
- 20 requests per day
- 10,000 tokens per day
- 300 tokens max per request input
- 500 tokens max per request output

💡 Your quota resets daily at midnight UTC.
"""


def format_quota_status(
    requests_used: int,
    requests_limit: int,
    tokens_used: int,
    tokens_limit: int,
    is_warning: bool = False,
    is_exhausted: bool = False,
    reset_at: str = "00:00 UTC"
) -> str:
    # Format quota status for display
    #
    # Args:
    #     requests_used: Number of requests used
    #     requests_limit: Total requests allowed
    #     tokens_used: Number of tokens used
    #     tokens_limit: Total tokens allowed
    #     is_warning: Whether usage is at warning level (>80%)
    #     is_exhausted: Whether quota is exhausted
    #     reset_at: When quota resets
    #
    # Returns:
    #     Formatted markdown string
    
    requests_remaining = requests_limit - requests_used
    tokens_remaining = tokens_limit - tokens_used
    
    requests_percent = (requests_used / requests_limit * 100) if requests_limit > 0 else 0
    tokens_percent = (tokens_used / tokens_limit * 100) if tokens_limit > 0 else 0
    
    # Choose emoji based on status
    if is_exhausted:
        status_emoji = "🚫"
        status_text = "**QUOTA EXHAUSTED**"
        status_color = "🔴"
    elif is_warning:
        status_emoji = "⚠️"
        status_text = "**Warning: High Usage**"
        status_color = "🟡"
    else:
        status_emoji = "✅"
        status_text = "**Quota Available**"
        status_color = "🟢"
    
    # Build progress bars using Unicode blocks
    def make_progress_bar(percent: float, width: int = 20) -> str:
        filled = int(percent / 100 * width)
        empty = width - filled
        
        if percent >= 90:
            bar_char = "🔴"
        elif percent >= 80:
            bar_char = "🟡"
        else:
            bar_char = "🟢"
        
        return bar_char * filled + "⬜" * empty
    
    requests_bar = make_progress_bar(requests_percent)
    tokens_bar = make_progress_bar(tokens_percent)
    
    message = f"""
### {status_emoji} {status_text}

**Requests:** {requests_used} / {requests_limit} ({requests_remaining} remaining)  
{requests_bar} {requests_percent:.1f}%

**Tokens:** {tokens_used:,} / {tokens_limit:,} ({tokens_remaining:,} remaining)  
{tokens_bar} {tokens_percent:.1f}%

{status_color} Resets at: **{reset_at}**
"""
    
    if is_exhausted:
        message += "\n\n🚫 **Daily quota exhausted.** Please wait for reset or upgrade your account."
    elif is_warning:
        message += "\n\n⚠️ **Warning:** You're approaching your daily limit. Use carefully!"
    
    return message

