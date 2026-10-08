"""durparse: parse human duration strings into seconds."""
from .cli import parse_duration, format_human, main

__all__ = ["parse_duration", "format_human", "main"]
__version__ = "0.1.0"
