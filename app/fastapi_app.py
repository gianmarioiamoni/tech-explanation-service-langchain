# app/fastapi_app.py
#
# FastAPI application with OAuth authentication and Gradio integration
#
# This app provides:
# - Multiple OAuth providers (Google, GitHub, Hugging Face)
# - Session management
# - Gradio app mounted with auth_dependency
# - Login/logout routes

from fastapi import FastAPI, Request, Depends
from fastapi.responses import RedirectResponse, HTMLResponse
from starlette.middleware.sessions import SessionMiddleware
from authlib.integrations.starlette_client import OAuthError
import gradio as gr
import logging

from app.auth.oauth_providers import oauth, SESSION_SECRET, has_oauth_configured, get_configured_providers

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Tech Explanation Service",
    description="AI-powered technical explanations with quota management",
    version="1.0.0"
)

# Add session middleware for OAuth
app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET)

# ============================================================================
# Authentication Dependency
# ============================================================================

def get_current_user(request: Request) -> str | None:
    # Extract username from session (set after OAuth login)
    # This function is used as auth_dependency for Gradio
    #
    # Args:
    #     request: FastAPI/Starlette Request object
    #
    # Returns:
    #     Username string if authenticated, None otherwise
    
    user = request.session.get('user')
    if user:
        username = user.get('username') or user.get('name') or user.get('login')
        if username:
            logger.debug(f"Authenticated user: {username}")
            return username
    
    logger.debug("No authenticated user found in session")
    return None

# ============================================================================
# OAuth Routes
# ============================================================================

@app.get('/')
def root(request: Request):
    # Root route - redirect to /gradio if authenticated, otherwise show login page
    user = get_current_user(request)
    if user:
        return RedirectResponse(url='/gradio')
    else:
        return RedirectResponse(url='/login-page')

@app.get('/login-page')
def login_page(request: Request):
    # Display login page with available OAuth providers
    
    if not has_oauth_configured():
        return HTMLResponse("""
            <html>
                <head>
                    <title>OAuth Not Configured</title>
                    <style>
                        body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
                        .warning { background-color: #fff3cd; border: 1px solid #ffc107; padding: 20px; border-radius: 5px; }
                    </style>
                </head>
                <body>
                    <div class="warning">
                        <h1>⚠️ OAuth Not Configured</h1>
                        <p>No OAuth providers are configured. Please set environment variables:</p>
                        <ul>
                            <li><code>GOOGLE_CLIENT_ID</code> and <code>GOOGLE_CLIENT_SECRET</code></li>
                            <li><code>GITHUB_CLIENT_ID</code> and <code>GITHUB_CLIENT_SECRET</code></li>
                            <li><code>HF_CLIENT_ID</code> and <code>HF_CLIENT_SECRET</code></li>
                        </ul>
                        <p>Falling back to Basic Auth mode...</p>
                        <a href="/gradio">Continue with Basic Auth</a>
                    </div>
                </body>
            </html>
        """)
    
    providers = get_configured_providers()
    provider_buttons = ""
    for provider in providers:
        emoji = {"google": "🔵", "github": "⚫", "huggingface": "🤗"}.get(provider, "🔐")
        name = {"google": "Google", "github": "GitHub", "huggingface": "Hugging Face"}.get(provider, provider)
        provider_buttons += f'<a href="/login/{provider}" class="btn btn-{provider}">{emoji} Login with {name}</a>'
    
    return HTMLResponse(f"""
        <html>
            <head>
                <title>Login - Tech Explanation Service</title>
                <style>
                    body {{
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        max-width: 500px;
                        margin: 100px auto;
                        padding: 20px;
                        text-align: center;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        min-height: 100vh;
                    }}
                    .container {{
                        background: white;
                        padding: 40px;
                        border-radius: 10px;
                        box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                    }}
                    h1 {{ color: #333; margin-bottom: 10px; }}
                    p {{ color: #666; margin-bottom: 30px; }}
                    .btn {{
                        display: block;
                        padding: 15px 30px;
                        margin: 15px 0;
                        text-decoration: none;
                        border-radius: 5px;
                        font-weight: bold;
                        font-size: 16px;
                        transition: transform 0.2s, box-shadow 0.2s;
                    }}
                    .btn:hover {{
                        transform: translateY(-2px);
                        box-shadow: 0 5px 15px rgba(0,0,0,0.3);
                    }}
                    .btn-google {{ background: #4285f4; color: white; }}
                    .btn-github {{ background: #333; color: white; }}
                    .btn-huggingface {{ background: #ff9d00; color: white; }}
                    .info {{ background: #e7f3ff; padding: 15px; border-radius: 5px; margin-top: 20px; font-size: 14px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🎓 Tech Explanation Service</h1>
                    <p>AI-powered technical explanations with smart quota management</p>
                    {provider_buttons}
                    <div class="info">
                        <strong>📊 Daily Quota:</strong> 20 requests, 10,000 tokens<br>
                        <strong>🔐 Secure:</strong> Your data is never stored
                    </div>
                </div>
            </body>
        </html>
    """)

@app.route('/login/{provider}')
async def login(request: Request):
    # Initiate OAuth flow for the specified provider
    provider = request.path_params['provider']
    
    if provider not in get_configured_providers():
        return HTMLResponse(f"<h1>Provider '{provider}' not configured</h1>", status_code=400)
    
    redirect_uri = request.url_for('auth_callback', provider=provider)
    
    # Ensure redirect_uri uses https in production
    if request.url.scheme == 'https':
        from urllib.parse import urlparse, urlunparse
        redirect_uri = urlunparse(urlparse(str(redirect_uri))._replace(scheme='https'))
    
    return await getattr(oauth, provider).authorize_redirect(request, redirect_uri)

@app.route('/auth/{provider}')
async def auth_callback(request: Request):
    # OAuth callback - handle provider response and create session
    provider = request.path_params['provider']
    
    try:
        token = await getattr(oauth, provider).authorize_access_token(request)
    except OAuthError as e:
        logger.error(f"OAuth error for {provider}: {e}")
        return RedirectResponse(url='/login-page?error=oauth_failed')
    
    # Extract user info from token
    if provider == 'google':
        userinfo = token.get('userinfo')
        if userinfo:
            request.session['user'] = {
                'username': userinfo.get('email'),
                'name': userinfo.get('name'),
                'provider': 'google'
            }
    elif provider == 'github':
        # Fetch user info from GitHub API
        resp = await getattr(oauth, provider).get('user', token=token)
        userinfo = resp.json()
        request.session['user'] = {
            'username': userinfo.get('login'),
            'name': userinfo.get('name'),
            'provider': 'github'
        }
    elif provider == 'huggingface':
        userinfo = token.get('userinfo')
        if userinfo:
            request.session['user'] = {
                'username': userinfo.get('preferred_username'),
                'name': userinfo.get('name'),
                'provider': 'huggingface'
            }
    
    logger.info(f"User logged in via {provider}: {request.session['user'].get('username')}")
    return RedirectResponse(url='/gradio')

@app.route('/logout')
async def logout(request: Request):
    # Logout - clear session
    request.session.pop('user', None)
    logger.info("User logged out")
    return RedirectResponse(url='/login-page')

# ============================================================================
# Health Check
# ============================================================================

@app.get('/health')
def health():
    # Health check endpoint
    return {
        "status": "healthy",
        "oauth_configured": has_oauth_configured(),
        "providers": get_configured_providers()
    }

