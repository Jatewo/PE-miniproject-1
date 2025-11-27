"""Module for running experiments for bonus question 1."""

from secret_sharing import Graph, Topology, Simulation, Visualizer
from secret_sharing.simulation import Algorithm, SimulationConfig, NoiseDistribution
from utils.logging import get_colored_logger

log = get_colored_logger(__name__)


def compare_tolopologies() -> None:
    """Compare topologies for additive secret sharing.

    Runs a simulation for each topology and saves convergence plots for comparison.

    Returns:
        None

    """
    graphs = [Graph(num_nodes=50, topology=topology) for topology in Topology]
    simulator = Simulation()
    visualizer = Visualizer()

    results = []

    config = SimulationConfig(
        max_iterations=5000,
        epsilon=1e-6,
        algorithm=Algorithm.SYNCHRONOUS,
    )

    for graph in graphs:
        graph.set_initial_values(range_start=0, range_end=100)
        graph.apply_shares(random_range=100.0)
        log.info(f"Running experiment for {graph.topology.name} topology...")
        res = simulator.run_simulation(graph, config, name=f"ASS {graph.topology.name.capitalize()}")

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
        res = simulator.run_simulation(graph, config, name=f"ASS {graph.topology.name.capitalize()}")
        results.append(res)

        visualizer.animate_convergence(
            graph,
            res,
            f"figures/experiment_1/synchronous_{graph.topology.name}.gif",
        )


def ass_vs_dp() -> None:
    """Compare additive secret sharing with differential privacy.

    Runs a simulation of additive secret sharing (ASS) using synchronous iteration
    and differential privacy (DP) for different values of epsilon.

    Returns:
        None

    """
    graph = Graph(num_nodes=50, topology=Topology.MESH)
    simulator = Simulation()
    visualizer = Visualizer()

    results = []

    config = SimulationConfig(
        max_iterations=5000,
        epsilon=1e-6,
        algorithm=Algorithm.SYNCHRONOUS,
    )

    graph.set_initial_values(range_start=0, range_end=100)
    graph.apply_shares(random_range=100.0)
    res = simulator.run_simulation(graph, config, name="ASS")
    results.append(res)

    dp_scales = [0.1, 1.0, 5.0]

    for dp_scale in dp_scales:
        config = SimulationConfig(
            max_iterations=200,
            epsilon=0.0,
            algorithm=Algorithm.SYNCHRONOUS,
            noise_scale=dp_scale,
            noise_distribution=NoiseDistribution.LAPLACE,
        )
        graph.set_initial_values(range_start=0, range_end=100)
        graph.apply_shares(random_range=100.0)
        res = simulator.run_simulation(graph, config, name=f"DP {dp_scale}")
        results.append(res)

    visualizer.plot_convergence(
        results,
        save_path="figures/experiment_2/convergence.png",
        show=False,
    )


if __name__ == "__main__":
    ass_vs_dp()
