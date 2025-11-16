from .graph import Graph
import random
import copy

class Simulation:
    """Class for simulating a graph."""

    def __init__(self) -> None:
        """Initialize a simulation."""
        pass
        

    def run_ass_synchronous(self, base_graph: Graph, max_iterations: int = 1000, epsilon: float = 1e-6) -> tuple[list[float], int, float]:
        """Simulate additive secret sharing (ASS) using synchronous iteration.

        Args:
            max_iterations (int, optional): The maximum number of iterations to run. Defaults to 100.
            epsilon (float, optional): The epsilon value for convergence. Defaults to 1e-6 (0.000001).

        Returns:
            list: A list of error values at each iteration

        """
        graph = copy.deepcopy(base_graph)
        error_history = []
        max_degree = max(len(node.neighbors) for node in graph.nodes)
        iterations = 0

        alpha = 1.0 / (max_degree + 1)

        for i in range(max_iterations):
            iterations += 1
            # Phase 1: Calculate next values
            next_values = {}
            max_change = 0.0

            for node in graph.nodes:
                degree = len(node.neighbors)

                self_weight = 1.0 - (degree * alpha)
                weighted_sum = self_weight * node.value

                for neighbor in node.neighbors:
                    weighted_sum += alpha * neighbor.value

                next_values[node.id] = weighted_sum

            # Phase 2: Update values
            for node in graph.nodes:
                change = abs(node.value - next_values[node.id])
                max_change = max(max_change, change)
                node.value = next_values[node.id]

            # Phase 3: Calculate error
            error = graph.get_max_error()
            error_history.append(error)

            if max_change < epsilon:
                break

        return error_history, iterations, graph.avg

    def run_ass_asynchronous(self, base_graph: Graph, max_iterations: int = 1000, epsilon: float = 1e-6) -> tuple[list[float], int, float]:
        """Simulate additive secret sharing (ASS) using asynchronous iteration.
        
        Args:
            max_iterations (int, optional): The maximum number of iterations to run. Defaults to 100.
            epsilon (float, optional): The epsilon value for convergence. Defaults to 1e-6 (0.000001).
        
        Returns:
            tuple: A tuple containing a list of error values at each iteration and the number of iterations
        """
        graph = copy.deepcopy(base_graph)
        error_history = []
        num_nodes = len(graph.nodes)
        iterations = 0
        if num_nodes == 0:
            return [], 0, 0.0

        for i in range(max_iterations):
            iterations += 1
            self._perform_async_update(graph)

            if i % num_nodes == 0:
                error = graph.get_max_error()
                error_history.append(error)

                if self._check_consensus(graph, epsilon):
                    break

        return error_history, iterations, graph.avg

    def _perform_async_update(self, graph: Graph) -> None:
        """Perform an asynchronous update on the graph.

        This method randomly selects two nodes and updates their values
        to be the average of their neighbors.
        """
        node_a = random.choice(graph.nodes)
        
        # The guard clause is perfectly fine inside the helper
        if not node_a.neighbors:
            return

        node_b = random.choice(list(node_a.neighbors))

        local_avg = (node_a.value + node_b.value) / 2.0
        node_a.value = local_avg
        node_b.value = local_avg

    def _check_consensus(self, graph: Graph, epsilon: float) -> bool:
        """Check if the graph has converged.

        Args:
            epsilon (float): The epsilon value for convergence

        Returns:
            bool: True if the graph has converged, False otherwise
        """
        # This assumes at least 1 node, handled by the main function
        values = [node.value for node in graph.nodes]
        return (max(values) - min(values)) < epsilon
