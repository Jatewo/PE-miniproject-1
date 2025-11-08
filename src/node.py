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
		self.neighbors = set()

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
