# app/services/llm_factory.py
#
# This file is used to create a centralized LLM factory for the application.
# It avoids hard-coding the LLM configuration in the application code.

from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

# Load the environment variables from the .env file
# This makes the behavior consistent between local, notebook and runtime
load_dotenv()


def get_chat_llm() -> ChatOpenAI:
    """
    Centralized LLM factory for the application.

    Responsibilities:
    - Instantiate the OpenAI chat model
    - Apply standard configurations (model, temperature, etc.)
    - Hide the configuration details from the rest of the application
    """

    # Explicit validation
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError(
            "OPENAI_API_KEY not found. "
            "Make sure it is defined in your environment or .env file."
        )

    return ChatOpenAI(
        model="gpt-4o",
        temperature=0.2,
    )
