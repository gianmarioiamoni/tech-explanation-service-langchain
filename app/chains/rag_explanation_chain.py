# app/chains/rag_explanation_chain.py
#
# LCEL chain for RAG-enhanced technical explanations
#
# This chain accepts both a topic AND retrieved context documents,
# using them together to generate more accurate, context-aware explanations.
#
# Input: {"topic": str, "context": str}
# Output: str (sanitized explanation)

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

# -------------------------------
# LLM configuration (same as base chain)
# -------------------------------
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.2,
    streaming=True,
)

# -------------------------------
# RAG-specific prompt
# -------------------------------
# This prompt includes a {context} variable for retrieved documents
rag_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a senior software engineer and technical educator. "
            "Explain technical topics clearly and professionally.\n\n"
            "You have access to relevant documentation and context below. "
            "Use this context to provide accurate, detailed explanations. "
            "If the context doesn't contain relevant information, explain the topic using your general knowledge.\n\n"
            "Formatting rules (mandatory):\n"
            "- DO NOT use Markdown syntax of any kind.\n"
            "- DO NOT use '#', '##', '**', '*', '-', numbered lists, or code blocks.\n"
            "- DO NOT use headings or titles with special characters.\n"
            "Instead:\n"
            "- Use plain text only.\n"
            "- Use section titles as plain text followed by a colon.\n"
            "- Use short paragraphs.\n"
            "- Use simple bullet points starting with '•'.\n"
        ),
        (
            "human",
            "Context from documentation:\n\n{context}\n\n"
            "---\n\n"
            "Topic to explain: {topic}\n\n"
            "Provide a structured explanation of this topic using the context above."
        ),
    ]
)

# -------------------------------
# LCEL chain composition
# -------------------------------
rag_explanation_chain = rag_prompt | llm | StrOutputParser()

