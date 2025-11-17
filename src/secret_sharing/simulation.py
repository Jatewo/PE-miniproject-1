"""Module for simulating a graph."""
from .graph import Graph
import random
import copy
from .results import SimulationResult, StepResult
from enum import Enum


class Algorithm(Enum):
    """Enumeration of algorithms."""

    SYNCHRONOUS = 0
    ASYNCHRONOUS = 1


class Simulation:
    """Class for simulating a graph."""

    def __init__(self) -> None:
        """Initialize a simulation."""
        pass

    def run_simulation(
        self,
        base_graph: Graph,
        algorithm: Algorithm,
        max_iterations: int = 1000,
        epsilon: float = 1e-6,
    ) -> SimulationResult:
        """Run a simulation of additive secret sharing (ASS) using specified algorithm.

        Args:
            base_graph (Graph): The base graph to use for the simulation
            algorithm (Algorithm): The algorithm to use for the simulation
            max_iterations (int, optional): The maximum number of iterations to run.
                Defaults to 100.
            epsilon (float, optional): The epsilon value for convergence. Defaults to
                1e-6 (0.000001).

        Returns:
            SimulationResult: The result of the simulation

        """
        graph = copy.deepcopy(base_graph)
        history = []
        iterations = 0

        if algorithm == Algorithm.SYNCHRONOUS:
            max_degree = max(len(node.neighbors) for node in graph.nodes)
            alpha = 1.0 / (max_degree + 1)

        for _ in range(max_iterations):
            iterations += 1
            max_change = 0.0
            active_pair = None

            if algorithm == Algorithm.SYNCHRONOUS:
                max_change = self._perform_sync_update(graph, alpha)  # type: ignore
            elif algorithm == Algorithm.ASYNCHRONOUS:
                active_pair =self._perform_async_update(graph)

            error = graph.get_max_error()
            history.append(
                StepResult(
                    iteration=iterations,
                    values={node.id: node.value for node in graph.nodes},
                    error=error,
                    active_pair=active_pair,
                ),
            )

            if self._check_consensus(graph, epsilon, max_change, algorithm):
                break

        return SimulationResult(
            algorithm=algorithm.name,
            history=history,
            total_iterations=iterations,
            final_avg=graph.avg,
        )

    def _perform_sync_update(self, graph: Graph, alpha: float) -> float:
        """Perform an synchronous update on the graph.

        This method updates the values of the graph nodes
        using the additive secret sharing (ASS) algorithm.

        Args:
            graph (Graph): The graph to update
            alpha (float): The self-weight

        Returns:
            None

        """
        next_values = {}
        max_change = 0.0

        for node in graph.nodes:
            degree = len(node.neighbors)

            self_weight = 1.0 - (degree * alpha)
            weighted_sum = self_weight * node.value

            for neighbor in node.neighbors:
                weighted_sum += alpha * neighbor.value

            next_values[node.id] = weighted_sum

        for node in graph.nodes:
            change = abs(node.value - next_values[node.id])
            max_change = max(max_change, change)
            node.value = next_values[node.id]

        return max_change

    def _perform_async_update(self, graph: Graph) -> tuple[int, int] | None:
        """Perform an asynchronous update on the graph.

        This method randomly selects two nodes and updates their values
        to be the average of their neighbors.
        """
        node_a = random.choice(graph.nodes)
        if not node_a.neighbors:
            return None
        node_b = random.choice(list(node_a.neighbors))

        local_avg = (node_a.value + node_b.value) / 2.0
        node_a.value = local_avg
        node_b.value = local_avg
        return (node_a.id, node_b.id)

    def _check_consensus(
        self, graph: Graph, epsilon: float, max_change: float, algorithm: Algorithm,
    ) -> bool:
        """Check if the graph has converged.

        Args:
            graph (Graph): The graph to check
            epsilon (float): The epsilon value for convergence
            max_change (float): The maximum change in the graph
            algorithm (Algorithm): The algorithm used to simulate the graph

        Returns:
            bool: True if the graph has converged, False otherwise

        """
        # This assumes at least 1 node, handled by the main function

        if algorithm == Algorithm.SYNCHRONOUS:
            return max_change < epsilon
        elif algorithm == Algorithm.ASYNCHRONOUS:
            values = [node.value for node in graph.nodes]
            return (max(values) - min(values)) < epsilon
