# app/services/__init__.py
#
# Services package
#
# This package contains domain services organized by functionality:
# - explanation/: LLM explanation generation and output formatting
# - history/: Chat history persistence, querying, and formatting
#
# Domain-Driven Design architecture:
# Use specific services based on your needs instead of a monolithic service.

# Explanation domain
from app.services.explanation import ExplanationService, OutputFormatter

# History domain
from app.services.history import (
    HistoryRepository,
    HistoryQueryService,
    HistoryFormatter,
    HistoryLoader,
)

__all__ = [
    # Explanation domain
    "ExplanationService",
    "OutputFormatter",
    # History domain
    "HistoryRepository",
    "HistoryQueryService",
    "HistoryFormatter",
    "HistoryLoader",
]

