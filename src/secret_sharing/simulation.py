"""Module for simulating a graph."""

from .graph import Graph
import random
import copy
from .results import SimulationResult, StepResult
from enum import Enum
from dataclasses import dataclass
import numpy as np


class Algorithm(Enum):
    """Enumeration of algorithms."""

    SYNCHRONOUS = 0
    ASYNCHRONOUS = 1


class NoiseDistribution(Enum):
    """Enumeration of noise distributions."""

    UNIFORM = 0
    GAUSSIAN = 1
    LAPLACE = 2


@dataclass
class SimulationConfig:
    """Class for storing the configuration for a simulation run."""

    algorithm: Algorithm = Algorithm.SYNCHRONOUS
    max_iterations: int = 1000
    epsilon: float = 1e-6
    noise_scale: float = 0.0
    noise_distribution: NoiseDistribution | None = None


class Simulation:
    """Class for simulating a graph."""

    def __init__(self) -> None:
        """Initialize a simulation."""
        pass

    def run_simulation(
        self,
        base_graph: Graph,
        config: SimulationConfig,
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
        alpha = 0.0

        algorithm = config.algorithm
        max_iterations = config.max_iterations
        epsilon = config.epsilon

        history.append(
            StepResult(
                iteration=0,
                values={node.id: node.value for node in graph.nodes},
                error=graph.get_max_error(),
            ),
        )

        if algorithm == Algorithm.SYNCHRONOUS:
            max_degree = max(len(node.neighbors) for node in graph.nodes)
            alpha = 1.0 / (max_degree + 1)

        for _ in range(max_iterations):
            iterations += 1
            active_pair = None

            max_change, active_pair = self._perform_update(graph, alpha, config)

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
            algorithm=algorithm,
            graph=graph,
            history=history,
            total_iterations=iterations,
            final_avg=graph.avg,
        )

    def _get_noise(
        self, noise_distribution: NoiseDistribution | None, noise_scale: float
    ) -> float:
        """Get a noise value based on the noise distribution and scale.

        Args:
            noise_distribution (NoiseDistribution): The noise distribution to use
            noise_scale (float): The scale of the noise

        Returns:
            float: The noise value

        """
        match noise_distribution:
            case NoiseDistribution.UNIFORM:
                return np.random.uniform(-noise_scale, noise_scale)
            case NoiseDistribution.GAUSSIAN:
                return np.random.normal(0, noise_scale)
            case NoiseDistribution.LAPLACE:
                return np.random.laplace(0, noise_scale)
            case _:
                return 0.0

    def _perform_update(
        self,
        graph: Graph,
        alpha: float,
        config: SimulationConfig,
    ) -> tuple[float, tuple[int, int] | None]:
        """Perform an update on the graph.

        Args:
            graph (Graph): The graph to update
            algorithm (Algorithm): The algorithm to use for the update
            alpha (float): A self-weight constant

        Returns:
            None

        """
        max_change, active_pair = 0.0, None
        if config.algorithm == Algorithm.SYNCHRONOUS:
            max_change = self._perform_sync_update(graph, alpha, config)
        elif config.algorithm == Algorithm.ASYNCHRONOUS:
            active_pair = self._perform_async_update(graph, config)

        return max_change, active_pair

    def _perform_sync_update(
        self, graph: Graph, alpha: float, config: SimulationConfig
    ) -> float:
        """Perform an synchronous update on the graph.

        This method updates the values of the graph nodes
        using the additive secret sharing (ASS) algorithm.

        Args:
            graph (Graph): The graph to update
            alpha (float): A self-weight constant
            config (SimulationConfig): The simulation configuration

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
                noise = self._get_noise(config.noise_distribution, config.noise_scale)
                received_value = neighbor.value + noise
                weighted_sum += alpha * received_value

            next_values[node.id] = weighted_sum

        for node in graph.nodes:
            change = abs(node.value - next_values[node.id])
            max_change = max(max_change, change)
            node.value = next_values[node.id]

        return max_change

    def _perform_async_update(self, graph: Graph, config: SimulationConfig) -> tuple[int, int] | None:
        """Perform an asynchronous update on the graph.

        This method randomly selects two nodes and updates their values
        to be the average of their neighbors.
        """
        node_a = random.choice(graph.nodes)
        if not node_a.neighbors:
            return None
        node_b = random.choice(list(node_a.neighbors))
        
        noise_a = self._get_noise(config.noise_distribution, config.noise_scale)
        noise_b = self._get_noise(config.noise_distribution, config.noise_scale)
        
        val_a_noisy = node_a.value + noise_a
        val_b_noisy = node_b.value + noise_b

        new_a = (node_a.value + val_b_noisy) / 2.0
        new_b = (node_b.value + val_a_noisy) / 2.0
        
        node_a.value = new_a
        node_b.value = new_b
        return (node_a.id, node_b.id)

    def _check_consensus(
        self,
        graph: Graph,
        epsilon: float,
        max_change: float,
        algorithm: Algorithm,
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
