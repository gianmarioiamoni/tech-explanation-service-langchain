# app/chains/tech_explanation_chain.py
#
# LCEL core chain for the Tech Explanation use case.
#
# This module defines a pure LCEL pipeline that transforms
# a technical topic into a structured explanation using an LLM.
#
# The chain is:
# Input dict -> Prompt -> LLM -> Output parsing
#

from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda

# Load environment variables (e.g. OPENAI_API_KEY)
load_dotenv()


# ------------------------------------------------------------------
# LLM configuration
# ------------------------------------------------------------------
# ChatOpenAI is itself a Runnable and can be piped in LCEL.
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.2,
)


# ------------------------------------------------------------------
# Prompt definition
# ------------------------------------------------------------------
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


# ------------------------------------------------------------------
# Output parser
# ------------------------------------------------------------------
# The LLM returns an AIMessage object.
# This RunnableLambda extracts the plain text content.
output_parser = RunnableLambda(lambda message: message.content)


# ------------------------------------------------------------------
# LCEL chain composition
# ------------------------------------------------------------------
# This is a RunnableSequence created via the pipe operator.
tech_explanation_chain = prompt | llm | output_parser

