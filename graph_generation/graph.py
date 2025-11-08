"""Module for representing a graph consisting of nodes (Node objects)."""

from node import Node
import networkx as nx
import random
import math
from itertools import combinations

from enum import Enum


class Topology(Enum):
    """Enumeration of topologies."""

    RING = 1
    STAR = 2
    TREE = 3
    MESH = 4
    FULL = 5


class Graph:
    """Class for representing a graph consisting of nodes (Node objects).

    Attributes:
        nodes (list[Node]): List of nodes in the graph
        topology (Topology): Topology of the graph

    """

    def __init__(self, num_nodes: int, topology: Topology) -> None:
        """Initialize a graph with the given number of nodes and topology.

        Args:
            num_nodes (int): Number of nodes in the graph
            topology (Topology): Topology of the graph

        Returns:
            None

        """
        self.nodes = [Node(i) for i in range(num_nodes)]
        self.topology = topology
        self._initialize_connections()

    def _initialize_connections(self) -> None:
        match self.topology:
            case Topology.RING:
                self._initialize_ring()

            case Topology.STAR:
                self._initialize_star()

            case Topology.TREE:
                self._initialize_tree()

            case Topology.MESH:
                self._initialize_mesh()

            case Topology.FULL:
                self._initialize_full()

    def _initialize_ring(self) -> None:
        """Initialize ring topology in graph.

        Nodes are connected in a circular fashion. The first node
        is connected to the last node, and each node is connected
        to the next node.

        Returns:
            None

        """
        n = len(self.nodes)
        for i in range(n):
            self._connect(self.nodes[i], self.nodes[(i + 1) % len(self.nodes)])

    def _initialize_star(self) -> None:
        """Initialize star topology in graph.

        First node is chosen as the center node. Then, all other
        nodes are connected to the center node.

        Returns:
            None

        """
        center_node = self.nodes[0]
        for node in self.nodes[1:]:
            self._connect(center_node, node)

    def _initialize_tree(self) -> None:
        """Initialize tree topology in graph.

        Parent node is found using array indexing.

        Example:
        ```
        \u200e
            0	0 -> Parent node
           / \\	(1 - 1) // 2 = 0 -> Left child of 0
          1   2	(2 - 1) // 2 = 1 -> Right child of 0
         / \\ / \\	(3 - 1) // 2 = 1 -> Left child of 1
        3  4 5  6	(5 - 1) // 2 = 2 -> Right child of 2 ...
        ```

        Returns:
            None

        """
        for i in range(1, len(self.nodes)):
            parent_index = (i - 1) // 2
            self._connect(self.nodes[i], self.nodes[parent_index])

    def _initialize_mesh(self) -> None:
        """Initialize mesh topology in graph.

        Uses Erdos-Renyi model to generate random graph with
        the given number of nodes and the specified probability
        of connecting two nodes. The probability of connecting
        two nodes is inversely proportional to the log of the
        number of nodes. This is a good approximation for large
        graphs.

        If the graph is not connected, components are randomly
        bridged by connecting random nodes in each component.

        Returns:
            None

        """
        n = len(self.nodes)
        if n < 2:
            return

        p = min(0.8, max(0.02, 1 / math.log(n + 2)))
        for u, v in combinations(self.nodes, 2):
            if random.random() < p:  # noqa: S311
                self._connect(u, v)

        if self._is_connected():
            return

        nx_graph = nx.Graph()
        for node in self.nodes:
            nx_graph.add_edges_from((node.id, nbr.id) for nbr in node.neighbors)

        comps = list(nx.connected_components(nx_graph))

        for comp_a, comp_b in zip(comps, comps[1:], strict=True):
            u_idx = random.choice(list(comp_a))  # noqa: S311
            v_idx = random.choice(list(comp_b))  # noqa: S311
            self._connect(self.nodes[u_idx], self.nodes[v_idx])

    def _initialize_full(self) -> None:
        """Initialize fully connected topology in graph.

        All nodes are connected to each other.

        Returns:
            None

        """
        n = len(self.nodes)
        for i in range(n):
            for j in range(i + 1, n):
                self._connect(self.nodes[i], self.nodes[j])

    def _connect(self, node1: Node, node2: Node) -> None:
        """Connect two nodes in graph.

        Adds the two nodes to each other's neighbor sets.

        Args:
            node1 (Node): First node to connect
            node2 (Node): Second node to connect

        Returns:
            None

        """
        node1.neighbors.add(node2)
        node2.neighbors.add(node1)

    def _is_connected(self) -> bool:
        """Check if the graph is connected using BFS.

        Checks if all nodes in the graph are reachable from
        the first node in the graph using BFS.

        Returns:
            bool: True if the graph is connected, False otherwise

        """
        if not self.nodes:
            return True

        start_node = self.nodes[0]
        reached = {start_node}
        queue = [start_node]

        while queue:
            current = queue.pop(0)
            for neighbor in current.neighbors:
                if neighbor not in reached:
                    reached.add(neighbor)
                    queue.append(neighbor)

        return len(reached) == len(self.nodes)

    def __str__(self) -> str:
        """Create string representation of graph.

        Returns:
            str: String representation of the graph

        """
        return f"Graph with {len(self.nodes)} nodes and topology {self.topology}"
