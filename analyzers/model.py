from dataclasses import dataclass
from typing import List, Optional
import json
from pathlib import Path


@dataclass
class CodeViolation:
    """Represents a single code violation in a standardized format."""
    file_path: str
    line_start: int
    line_end: int
    column_start: int
    column_end: int
    rule: str
    category: str
    description: str
    severity: str
    url: Optional[str] = None

@dataclass
class AnalysisResult:
    """Contains the complete analysis results."""
    tool_name: str
    tool_version: str
    timestamp: str
    violations: List[CodeViolation]
    errors: List[str]
