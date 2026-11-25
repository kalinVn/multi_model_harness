from dataclasses import dataclass, field


@dataclass(frozen=True)
class DependencyGraphNode:
    dependencies: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class UnresolvedDependency:
    source: str
    reference: str
    line: int
    column: int
    reason: str


@dataclass(frozen=True)
class DependencyGraph:
    roots: list[str]
    nodes: dict[str, DependencyGraphNode]
    files: list[str]
    cycles: list[list[str]]
    unresolved: list[UnresolvedDependency]
