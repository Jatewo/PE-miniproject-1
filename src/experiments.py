"""Module for running experiments for bonus question 1."""

from secret_sharing import Graph, Topology, Simulation, Visualizer
from secret_sharing.simulation import Algorithm
from utils.logging import get_colored_logger

log = get_colored_logger(__name__)


def experiment_1() -> None:
    """Compare topologies for additive secret sharing.

    Runs a simulation for each topology and saves convergence plots for comparison.

    Returns:
        None

    """
    graphs = [Graph(num_nodes=50, topology=topology) for topology in Topology]
    simulator = Simulation()
    visualizer = Visualizer()

    results = []

    for graph in graphs:
        graph.set_initial_values(range_start=0, range_end=100)
        graph.apply_shares(random_range=100.0)
        log.info(f"Running experiment for {graph.topology.name} topology...")
        res = simulator.run_simulation(
            graph, Algorithm.SYNCHRONOUS, max_iterations=5000
        )

        results.append(res)

        log.info(f"Plotting convergence for {graph.topology.name} topology...")
        visualizer.plot_convergence(
            [res],
            save_path=f"figures/experiment_1/synchronous_{graph.topology.name}.png",
            show=False,
        )

        log.info(f"Animating convergence for {graph.topology.name} topology...")

    visualizer.plot_convergence(
        results,
        save_path="figures/experiment_1/synchronous_convergence.png",
        show=False,
        y_min=1e-6,
    )

    graphs = [Graph(num_nodes=10, topology=topology) for topology in Topology]

    results = []

    for graph in graphs:
        graph.set_initial_values(range_start=0, range_end=100)
        graph.apply_shares(random_range=100.0)
        res = simulator.run_simulation(graph, Algorithm.SYNCHRONOUS)
        results.append(res)

        visualizer.animate_convergence(
            graph,
            res,
            f"figures/experiment_1/synchronous_{graph.topology.name}.gif",
        )


if __name__ == "__main__":
    experiment_1()
