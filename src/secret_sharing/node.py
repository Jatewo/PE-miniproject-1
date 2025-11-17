"""Module for representing a node in a graph."""
import random
import copy

class Node:
    """Class for representing a node in a graph.

    Can store a float value and a set of neighbors.

    Attributes:
        id (int): ID of the node
        value (float): Value of the node
        starting_value (float): Starting value of the node
        neighbors (set[Node]): Set of nodes that are connected to the node

    """

    def __init__(self, id: int, value: float = 0.0) -> None:
        """Initialize a node with an ID and an optional value.

        Args:
            id (int): _description_
            value (float, optional): _description_. Defaults to 0.0.

        """
        self.id = id
        self.value = value
        self.starting_value = value
        self.neighbors: set[Node] = set()

    def generate_shares(self, random_range: float = 100.0) -> dict[int, float]:
        """Generate shares for the node.

        Generates one random share for each neighbor and subtracts their
        sum from this node's secret_value.

        Args:
            random_range (float, optional): The range of random numbers to generate.
                Defaults to 100.0.

        Returns:
            dict: A dictionary mapping each neighbor to a share value

        """
        shares_to_send = {}
        total_sent = 0.0

        for neighbor in self.neighbors:
            share = random.uniform(-random_range, random_range)
            shares_to_send[neighbor.id] = share
            total_sent += share

        self.value -= total_sent

        return shares_to_send

    def apply_received_shares(self, received_shares_list: list[float]) -> None:
        """Add all received shares to this node's secret_value.

        Args:
            received_shares_list (list): A list of received shares

        Returns:
            None

        """
        total_received = sum(received_shares_list)

        self.value += total_received


    def __str__(self) -> str:
        """Create string representation of node.

        Returns:
            str: String representation of the node

        """
        return f"Node {self.id}: {self.value}"

    def __eq__(self, other: object) -> bool:
        """Equality operator for nodes. Checks if two nodes have the same ID.

        Args:
            other (object): The object to compare with

        Returns:
            bool: True if the two objects are equal, False otherwise

        """
        if not isinstance(other, Node):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash function for node. Used for creating sets of nodes.

        Returns:
            int: Hash value of the node's ID

        """
        return hash(self.id)

    def __deepcopy__(self, memo: dict) -> "Node":
        """Deepcopy to handle circular references in the neighbors set.

        Args:
            memo (dict): The memo dictionary

        Returns:
            Node: A deepcopy of the node

        """
        if id(self) in memo:
            return memo[id(self)]

        new_node = self.__class__(self.id, self.value)
        new_node.starting_value = self.starting_value

        memo[id(self)] = new_node

        new_node.neighbors = copy.deepcopy(self.neighbors, memo)

        return new_node
