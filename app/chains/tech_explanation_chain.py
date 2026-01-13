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
from langchain_core.output_parsers import StrOutputParser

# Load environment variables (e.g. OPENAI_API_KEY)
load_dotenv()


# ------------------------------------------------------------------
# LLM configuration
# ------------------------------------------------------------------
# ChatOpenAI is itself a Runnable and can be piped in LCEL.
# streaming=True enables progressive token generation for real-time output
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.2,
    streaming=True,
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
            "Explain technical topics clearly and professionally.\n\n"
            "Formatting rules (mandatory):\n"
            "- DO NOT use Markdown syntax of any kind.\n"
            "- DO NOT use '#', '##', '**', '*', '-', numbered lists, or code blocks.\n"
                "- DO NOT use headings or titles with special characters.\n"
            "Instead:\n"
            "- Use plain text only.\n"
            "- Use section titles as plain text followed by a colon.\n"
            "- Use short paragraphs.\n"
            "- Use simple bullet points starting with '•'.\n"
            "- Use semantic emojis (🔴 🟠 🟢) when appropriate. For example, when explaining a concept, use a 🔴 emoji to indicate a critical point, a 🟠 emoji to indicate a important point, a 🟢 emoji to indicate a positive point\n"
            "- Don't exceed in semantic emojis usage. Use them only when appropriate. If you don't have a semantic emoji to use, use a plain text instead.\n"
            "- Don't use more than 3 semantic emojis in a single explanation. If you need to use more than 3, use a plain text instead.\n"
            "- Try to use at least 1 semantic emoji in a single explanation. \n"
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
# StrOutputParser is optimized for streaming and extracts text content
# from AIMessage/AIMessageChunk objects efficiently
output_parser = StrOutputParser()


# ------------------------------------------------------------------
# LCEL chain composition
# ------------------------------------------------------------------
# This is a RunnableSequence created via the pipe operator.
tech_explanation_chain = prompt | llm | output_parser

