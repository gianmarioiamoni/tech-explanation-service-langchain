# app/chains/tech_explanation_chain.py
#
# LCEL core chain for the Tech Explanation use case.
# This module defines a pure LCEL pipeline that transforms
# a technical topic into a structured explanation using an LLM.

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda

# Load environment variables (including OPENAI_API_KEY)
load_dotenv()


# --- LLM configuration ---
# The LLM itself is a Runnable and can be composed in LCEL pipelines.
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.2,
)


# --- Prompt definition ---
# ChatPromptTemplate is also a Runnable.
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a senior software engineer and technical educator. "
            "Explain technical topics clearly, precisely, and concisely."
        ),
        (
            "human",
            "Explain the following topic in a structured way:\n\n{topic}"
        ),
    ]
)


# --- Post-processing step ---
# RunnableLambda adapts a simple Python function into a Runnable.
# Here we normalize the LLM output to a plain string.
post_process = RunnableLambda(
    lambda message: message.content.strip()
)


# --- LCEL pipeline ---
# The pipe operator creates a RunnableSequence:
# Prompt -> LLM -> Post-processing
tech_explanation_chain = prompt | llm | post_process
