import networkx as nx
import matplotlib.pyplot as plt
from .graph import Graph
import os

class Visualizer:
    """Class for visualizing a graph and plotting results."""

    def __init__(self) -> None:
        """Initialize a visualizer."""
        pass

    def draw_graph(self, graph: Graph, *, title: str = "Graph Topology", save_path: str | None = None, show: bool = False) -> None:
        """Draw the graph's topology using NetworkX and Matplotlib.

        Args:
            graph: The graph to draw
            save_path: The path to save the image to - if None, it will not be saved
            title: The title of the graph
            show: Whether to show the graph

        Returns:
            None

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
        
        if save_path:
            self._save_figure(plt.gcf(), save_path, "png")

        if show:
            plt.show()
            
    def _save_figure(self, fig, save_path: str, file_format: str) -> None:
        """Save a figure to a file.

        Args:
            fig: The figure to save
            save_path: The path to save the figure to - if None, it will not be saved
        """
        if save_path:
            if not save_path.endswith(".png"):
                save_path += ".png"

            path = save_path.split("/")
            if not os.path.exists(os.path.join(*path[:-1])):
                os.makedirs(os.path.join(*path[:-1]))
            fig.savefig(save_path)
        

    def plot_convergence(self, results: list, *, title: str = "Convergence", show: bool = False, save_path: str | None = None) -> None:
        """
        Plots error histories.

        Args:
            results: A list of tuples: (y_values, label, step_size)
                     - y_values: The list of errors
                     - label: Legend label
                     - step_size: The interval at which data was recorded (e.g., 1 or 10)
        """
        plt.figure(figsize=(12, 7))

        for y_values, label, step_size in results:
            # FIX: Auto-generate X to match the exact length of Y
            x_axis = [i * step_size for i in range(len(y_values))]

            plt.plot(x_axis, y_values, label=label, marker='o',
                     markersize=2, alpha=0.7)

        plt.yscale('log')
        plt.xlabel("Iterations")
        plt.ylabel("Maximum Error (Log Scale)")
        plt.title(title)
        plt.legend()
        plt.grid(True, which="both", ls=":")
        plt.tight_layout()
        
        if save_path:
            self._save_figure(plt.gcf(), save_path, "png")

        if show:
            plt.show()
