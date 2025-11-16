import networkx as nx
import matplotlib.pyplot as plt
from .graph import Graph

class Visualizer:
    """Class for visualizing a graph and plotting results."""
 
    def __init__(self) -> None:
        """Initialize a visualizer."""
        pass

    def draw_graph(self, graph: Graph, title: str = "Graph Topology"):
        """
        Draws the graph's topology using NetworkX and Matplotlib.
        """
        # 1. Convert your Graph object into a NetworkX graph
        G = nx.Graph()
        for node in graph.nodes:
            G.add_node(node.id)
            for neighbor in node.neighbors:
                G.add_edge(node.id, neighbor.id)

        # 2. Draw the graph
        plt.figure(figsize=(10, 8))
        pos = nx.spring_layout(G)  # Or nx.circular_layout(G), etc.
        nx.draw(G, pos, with_labels=True, node_color='lightblue', 
                edge_color='gray', node_size=500, font_weight='bold')
        plt.title(title)
        plt.show()