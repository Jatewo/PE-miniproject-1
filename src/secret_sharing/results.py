"""Module for storing the result of a simulation."""
from dataclasses import dataclass
from .graph import Graph
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .simulation import Algorithm

@dataclass
class StepResult:
    """Class for storing the result of a single step in a simulation."""

    iteration: int
    values: dict[int, float]
    error: float
    active_pair: tuple[int, int] | None = None

@dataclass
class SimulationResult:
    """Class for storing the result of a simulation."""
    name: str
    algorithm: "Algorithm"
    graph: Graph
    history: list[StepResult]
    total_iterations: int
    final_avg: float
