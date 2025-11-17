"""Module for storing the result of a simulation."""
from dataclasses import dataclass

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

    algorithm: str
    history: list[StepResult]
    total_iterations: int
    final_avg: float
