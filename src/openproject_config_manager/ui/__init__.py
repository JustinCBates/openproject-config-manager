"""UI package for console interfaces."""

# Legacy Rich-based UI temporarily disabled during Questionary migration
# from .console import ConsoleUI
from .questionary_ui import QuestionaryUI

__all__ = ["QuestionaryUI"]
