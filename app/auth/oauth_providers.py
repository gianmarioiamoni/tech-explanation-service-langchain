# app/auth/oauth_providers.py
#
# OAuth 2.0 provider configurations for Google, GitHub, and Hugging Face
#
# This module configures multiple OAuth providers using Authlib.
# Each provider requires client credentials that should be stored as environment variables.

import os
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config

# Load OAuth credentials from environment variables
# These should be set in HF Spaces Secrets or .env for local development
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")

HF_CLIENT_ID = os.getenv("HF_CLIENT_ID")
HF_CLIENT_SECRET = os.getenv("HF_CLIENT_SECRET")

# Session secret for secure cookies
SESSION_SECRET = os.getenv("SESSION_SECRET", "change-this-in-production-to-a-random-string")

# OAuth configuration
config_data = {}
if GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET:
    config_data['GOOGLE_CLIENT_ID'] = GOOGLE_CLIENT_ID
    config_data['GOOGLE_CLIENT_SECRET'] = GOOGLE_CLIENT_SECRET

if GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET:
    config_data['GITHUB_CLIENT_ID'] = GITHUB_CLIENT_ID
    config_data['GITHUB_CLIENT_SECRET'] = GITHUB_CLIENT_SECRET

if HF_CLIENT_ID and HF_CLIENT_SECRET:
    config_data['HF_CLIENT_ID'] = HF_CLIENT_ID
    config_data['HF_CLIENT_SECRET'] = HF_CLIENT_SECRET

starlette_config = Config(environ=config_data)
oauth = OAuth(starlette_config)

# Register OAuth providers
if GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET:
    oauth.register(
        name='google',
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={
            'scope': 'openid email profile',
        },
    )
    print("✅ Google OAuth configured")

if GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET:
    oauth.register(
        name='github',
        access_token_url='https://github.com/login/oauth/access_token',
        authorize_url='https://github.com/login/oauth/authorize',
        api_base_url='https://api.github.com/',
        client_kwargs={
            'scope': 'read:user user:email',
        },
    )
    print("✅ GitHub OAuth configured")

if HF_CLIENT_ID and HF_CLIENT_SECRET:
    oauth.register(
        name='huggingface',
        access_token_url='https://huggingface.co/oauth/token',
        authorize_url='https://huggingface.co/oauth/authorize',
        api_base_url='https://huggingface.co/api/',
        client_kwargs={
            'scope': 'openid profile email',
        },
    )
    print("✅ Hugging Face OAuth configured")

# Check if at least one provider is configured
def has_oauth_configured() -> bool:
    # Check if at least one OAuth provider is configured
    return bool(GOOGLE_CLIENT_ID or GITHUB_CLIENT_ID or HF_CLIENT_ID)

def get_configured_providers() -> list[str]:
    # Get list of configured OAuth providers
    providers = []
    if GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET:
        providers.append('google')
    if GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET:
        providers.append('github')
    if HF_CLIENT_ID and HF_CLIENT_SECRET:
        providers.append('huggingface')
    return providers

