from dataclasses import dataclass, field
from uuid import uuid4


@dataclass
class ToolResult:
    name: str
    output: str
    success: bool = True
    id: str = field(default_factory=lambda: str(uuid4()))
