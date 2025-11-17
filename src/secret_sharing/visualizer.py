"""Module for visualizing a graph and plotting results."""

import networkx as nx
import matplotlib.pyplot as plt
from .graph import Graph
import os
from .results import SimulationResult
from matplotlib.animation import FuncAnimation
from utils.logging import get_colored_logger
import numpy as np
from matplotlib.collections import PathCollection
from matplotlib.figure import Figure
from matplotlib.artist import Artist
from collections.abc import Iterable

log = get_colored_logger(__name__)


class Visualizer:
    """Class for visualizing a graph and plotting results."""

    def __init__(self) -> None:
        """Initialize a visualizer."""
        pass

    def draw_graph(
        self,
        graph: Graph,
        *,
        title: str = "Graph Topology",
        save_path: str | None = None,
        show: bool = False,
    ) -> None:
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
        g = nx.Graph()
        for node in graph.nodes:
            g.add_node(node.id)
            for neighbor in node.neighbors:
                g.add_edge(node.id, neighbor.id)

        # 2. Draw the graph
        plt.figure(figsize=(10, 8))
        pos = nx.spring_layout(g)  # Or nx.circular_layout(G), etc.
        nx.draw(
            g,
            pos,
            with_labels=True,
            node_color="lightblue",
            edge_color="gray",
            node_size=500,
            font_weight="bold",
        )
        plt.title(title)

        if save_path:
            self._save_figure(plt.gcf(), save_path, "png")

        if show:
            plt.show()

    def _save_figure(self, fig: Figure, save_path: str, file_format: str) -> None:
        """Save a figure to a file.

        Args:
            fig (Figure): The figure to save
            save_path (str): The path to save the figure to - if None, it will not be
                saved
            file_format (str): The file format to save the figure as

        """
        if save_path:
            if not save_path.endswith(".png"):
                save_path += ".png"

            path = save_path.split("/")
            if not os.path.exists(os.path.join(*path[:-1])):
                os.makedirs(os.path.join(*path[:-1]))
            fig.savefig(save_path)

    def plot_convergence(
        self,
        results: list[SimulationResult],
        *,
        title: str = "Convergence",
        show: bool = False,
        save_path: str | None = None,
    ) -> None:
        """Plot error histories.

        Args:
            results (list[SimulationResult]): A list of tuples: (values, label,
                step_size)
                - values: The list of errors
                - label: Legend label
                - step_size: The interval at which data was recorded (e.g., 1 or 10)
            title (str, optional): The title of the plot. Defaults to "Convergence".
            show (bool, optional): Whether to show the plot. Defaults to False.
            save_path (str | None, optional): The path to save the plot to. Defaults to
                None.

        """
        plt.figure(figsize=(12, 7))

        for res in results:
            iterations = [step.iteration for step in res.history]
            errors = [step.error for step in res.history]

            label = f"{res.algorithm.capitalize()} ({res.total_iterations} iters)"

            plt.plot(
                iterations,
                errors,
                label=label,
                marker="o",
                markersize=1,
                alpha=0.7,
            )

        plt.yscale("log")
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

    def animate_convergence(
        self,
        graph: Graph,
        result: SimulationResult,
        filename: str,
        interval: int = 50,  # Faster interval since processing is lighter
    ) -> None:
        """High-performance animation using object updates instead of redrawing."""
        fig, ax = plt.subplots(figsize=(8, 8))

        g = nx.Graph()
        for node in graph.nodes:
            g.add_node(node.id)
            for neighbor in node.neighbors:
                g.add_edge(node.id, neighbor.id)

        pos = nx.spring_layout(g, seed=42)

        nx.draw_networkx_edges(g, pos, ax=ax, alpha=0.2, edge_color="gray")

        node_collection = nx.draw_networkx_nodes(
            g, pos, node_size=600, ax=ax, cmap="coolwarm", node_color=[0] * len(g),
        )

        text_items = nx.draw_networkx_labels(
            g, pos, font_size=10, font_weight="bold", ax=ax,
        )

        highlight_nodes = nx.draw_networkx_nodes(
            g,
            pos,
            node_size=800,
            ax=ax,
            node_color="none",
            edgecolors="lime",
            linewidths=3,
        )
        highlight_nodes.set_offsets(np.empty((0, 2)))

        ax.axis("off")

        # Color Normalization
        all_values = []
        for step in result.history:
            all_values.extend(step.values.values())

        vmin, vmax = self._color_normalize(all_values)

        node_collection.set_clim(vmin, vmax)

        def update(frame_idx: int) -> Iterable[Artist]:
            step_data = result.history[frame_idx]
            current_values = step_data.values

            # Update Node Colors
            new_colors = [current_values[n] for n in g.nodes()]
            node_collection.set_array(new_colors)

            # Update Text Labels
            for node_id, text_obj in text_items.items():
                text_obj.set_text(f"{current_values[node_id]:.2f}")

            # Update Highlighter
            self._update_highlighter(highlight_nodes, step_data.active_pair, pos)

            ax.set_title(f"Iteration: {step_data.iteration}")

            return [node_collection, highlight_nodes] + list(text_items.values())

        filtered_history = list(filter(lambda n: n.error > 0.01, result.history))
        log.debug(f"Rendering {len(filtered_history)} frames to {filename}...")

        anim = FuncAnimation(
            fig,
            update,
            frames=len(list(filter(lambda n: n.error > 0.01, result.history))),
            interval=interval,
            blit=False,
        )

        try:
            anim.save(filename, writer="ffmpeg", fps=15)
            log.debug("Done!")
        except Exception as e:
            log.error(f"Error: {e}")
        finally:
            plt.close(fig)

    def _color_normalize(
        self,
        values: list[float],
        contrast: float = 7.0,
    ) -> tuple[float, float]:
        """Normalize the color scale for a list of values.

        Args:
            values (list[float]): The list of values to normalize
            contrast (float): The contrast of the color scale

        Returns:
            tuple[float, float]: The normalized min and max values

        """
        global_mean = sum(values) / len(values)
        max_deviation = max(abs(global_mean - v) for v in values)
        scaled_dev = max_deviation / contrast
        vmin, vmax = global_mean - scaled_dev, global_mean + scaled_dev
        return vmin, vmax

    def _update_highlighter(
        self,
        highlight_nodes: PathCollection,
        active_pair: tuple[int, int] | None,
        pos: dict[int, np.ndarray],
    ) -> None:
        """Update the highlighter to highlight the active pair of nodes.

        Args:
            highlight_nodes (PathCollection): The node collection to update
            active_pair (tuple[int, int] | None): The active pair of nodes
            pos (dict[int, tuple[float, float]]): The node positions

        Returns:
            None

        """
        if active_pair:
            u, v = active_pair
            coords = [pos[u], pos[v]]
            highlight_nodes.set_offsets(coords)
        else:
            highlight_nodes.set_offsets(np.empty((0, 2)))
