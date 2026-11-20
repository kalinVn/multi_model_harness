from dataclasses import dataclass, field


@dataclass
class Agent:
    name: str
    description: str
    instructions: str
    allowed_tools: tuple[str, ...] = field(default_factory=tuple)
    allowed_skills: tuple[str, ...] = field(default_factory=tuple)
    max_steps: int = 10
