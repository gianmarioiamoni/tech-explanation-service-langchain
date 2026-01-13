# app/services/__init__.py
#
# Services package
#
# This package contains domain services organized by functionality:
# - explanation/: LLM explanation generation and output formatting
# - history/: Chat history persistence, querying, and formatting
#
# For backward compatibility, TechExplanationService facade is provided.
# For new code, prefer using domain services directly.

from app.services.tech_explanation_service_facade import TechExplanationService

# Domain services (for direct use in new code)
from app.services.explanation import ExplanationService, OutputFormatter
from app.services.history import (
    HistoryRepository,
    HistoryQueryService,
    HistoryFormatter,
    HistoryLoader,
)

__all__ = [
    # Facade (backward compatibility)
    "TechExplanationService",
    # Explanation domain
    "ExplanationService",
    "OutputFormatter",
    # History domain
    "HistoryRepository",
    "HistoryQueryService",
    "HistoryFormatter",
    "HistoryLoader",
]

