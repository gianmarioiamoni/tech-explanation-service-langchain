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
    Factory centralizzata per l'LLM chat.

    Responsabilità:
    - Istanziare il modello chat OpenAI
    - Applicare configurazioni standard (model, temperature, ecc.)
    - Nascondere i dettagli di configurazione al resto dell'applicazione

    Questo approccio rende il servizio:
    - più testabile
    - più manutenibile
    - più facile da estendere (retry, logging, fallback)
    """

    # Explicit validation: in production it is essential
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError(
            "OPENAI_API_KEY not found. "
            "Make sure it is defined in your environment or .env file."
        )

    return ChatOpenAI(
        model="gpt-4o",
        temperature=0.2,
    )
