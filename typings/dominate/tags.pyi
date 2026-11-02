# Treat dominate as untyped, like mypy does (ignore_missing_imports).
from typing import Any

def __getattr__(name: str) -> Any: ...
