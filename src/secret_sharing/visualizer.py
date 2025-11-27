"""Module for visualizing a graph and plotting results."""

import networkx as nx
import matplotlib.pyplot as plt
from .graph import Graph
import os
from .results import SimulationResult, StepResult
from matplotlib.animation import FuncAnimation
from utils.logging import get_colored_logger
import numpy as np
from matplotlib.collections import PathCollection
from matplotlib.figure import Figure
from matplotlib.artist import Artist
from collections.abc import Iterable
from .graph import Topology
from .simulation import Algorithm

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
        show: bool = False,
        save_path: str | None = None,
        y_min: float | None = None,
    ) -> None:
        """Plot error histories.

        Args:
            results (list[SimulationResult]): A list of tuples: (values, label,
                step_size)
                - values: The list of errors
                - label: Legend label
                - step_size: The interval at which data was recorded (e.g., 1 or 10)
            show (bool, optional): Whether to show the plot. Defaults to False.
            save_path (str | None, optional): The path to save the plot to. Defaults to
                None.
            y_min (float | None, optional): Minimum value for the y-axis. Defaults to
                None.

        """
        plt.figure(figsize=(12, 7))

        labels = []

        for res in results:
            iterations = [step.iteration for step in res.history]
            errors = [step.error for step in res.history]

            label = (f"{res.name}")
            labels.append(label)

            plt.plot(
                iterations,
                errors,
                label=label,
                marker="o",
                markersize=1,
                alpha=0.7,
            )

        if y_min is not None:
            plt.ylim(bottom=y_min)

        title = self._get_title(results)

        plt.yscale("log")
        plt.xlabel("Iterations")
        plt.ylabel("Maximum Error (Log Scale)")
        plt.title(title)
        plt.legend(labels)
        plt.grid(True, which="both", ls=":")
        plt.tight_layout()

        if save_path:
            self._save_figure(plt.gcf(), save_path, "png")

        if show:
            plt.show()

    def _get_title(self, results: list[SimulationResult]) -> str:
        if len(results) > 1:
            title = "Convergence Plots"
        else:
            title = (f"Convergence Plot {results[0].graph.topology.name.capitalize()} "
            f"- {results[0].algorithm.name.capitalize()}")
        return title

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

        all_values = []
        for step in result.history:
            all_values.extend(step.values.values())

        vmin, vmax = self._color_normalize(all_values)

        node_collection.set_clim(vmin, vmax)

        def update(frame_idx: int) -> Iterable[Artist]:
            step_data = result.history[frame_idx]
            current_values = step_data.values

            new_colors = [current_values[n] for n in g.nodes()]
            node_collection.set_array(new_colors)

            for node_id, text_obj in text_items.items():
                text_obj.set_text(f"{current_values[node_id]:.2f}")

            self._update_highlighter(highlight_nodes, step_data.active_pair, pos)

            ax.set_title(f"Iteration: {step_data.iteration}")

            return [node_collection, highlight_nodes] + list(text_items.values())

        filtered_history = self._filter_history(result)
        log.debug(f"Rendering {len(filtered_history)} frames to {filename}...")

        anim = FuncAnimation(
            fig,
            update,
            frames=len(filtered_history),
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

    def _filter_history(self, result: SimulationResult) -> list[StepResult]:
        if not (
            result.graph.topology == Topology.FULL
            and result.algorithm == Algorithm.SYNCHRONOUS
        ):
            filtered_history = list(filter(lambda n: n.error > 0.001, result.history))
        else:
            filtered_history = result.history
        return filtered_history

    def _color_normalize(
        self,
        values: list[float],
        contrast: float = 15.0,
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
