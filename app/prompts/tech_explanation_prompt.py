# app/prompts/tech_explanation_prompt.py
#
# This module defines the structured chat prompt used by the TechExplanationService.
# The prompt is composed of:
# - a system message defining global behavior
# - a few-shot section with curated examples
# - a human message representing the actual user input
#
# The prompt is intentionally isolated from business logic to allow
# independent iteration, testing, and versioning.

from langchain_core.prompts import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    AIMessagePromptTemplate,
    ChatPromptTemplate,
    FewShotChatMessagePromptTemplate,
)


def build_tech_explanation_prompt() -> ChatPromptTemplate:
    """
    Builds and returns the ChatPromptTemplate used to generate
    technical explanations.

    The resulting prompt follows a layered structure:
    1. System message: sets role and behavioral constraints
    2. Few-shot examples: demonstrate the expected explanation style
    3. Human message: injects the runtime topic to be explained
    """

    # --- System message ---
    # Defines the global role, tone, and constraints for the model
    system_prompt = SystemMessagePromptTemplate.from_template(
        """
        You are a senior technical assistant.
        Provide clear, structured, and concise technical explanations.
        Avoid marketing language and unnecessary verbosity.
        """
    )

    # --- Few-shot examples ---
    # Curated examples used to guide style and structure
    examples = [
        {
            "input": "What is LangChain?",
            "output": (
                "LangChain is a Python framework designed to simplify the development "
                "of applications powered by large language models, providing abstractions "
                "for prompt composition, chains, and agents."
            ),
        },
        {
            "input": "What is the purpose of few-shot prompting?",
            "output": (
                "Few-shot prompting guides a language model by providing example "
                "input-output pairs, improving consistency, structure, and response quality."
            ),
        },
    ]

    # Defines how each example is converted into chat messages
    example_prompt = ChatPromptTemplate.from_messages(
        [
            HumanMessagePromptTemplate.from_template(
                "Question: {input}"
            ),
            AIMessagePromptTemplate.from_template(
                "Answer: {output}"
            ),
        ]
    )

    # Automatically expands the examples into Human/AI message pairs
    few_shot_prompt = FewShotChatMessagePromptTemplate(
        examples=examples,
        example_prompt=example_prompt,
    )

    # --- Human message ---
    # Represents the real user input injected at runtime
    human_prompt = HumanMessagePromptTemplate.from_template(
        "Explain {topic}"
    )

    # Final prompt composition
    return ChatPromptTemplate.from_messages(
        [
            system_prompt,
            few_shot_prompt,
            human_prompt,
        ]
    )
