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
            save_path=f"figures/topology_comparison/synchronous_{graph.topology.name}.png",
            show=False,
        )

        log.info(f"Animating convergence for {graph.topology.name} topology...")

    visualizer.plot_convergence(
        results,
        save_path="figures/topology_comparison/synchronous_convergence.png",
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
            f"figures/topology_comparison/synchronous_{graph.topology.name}.gif",
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
    
    log.info("--- Experiment: Additive Secret Sharing vs. Differential Privacy ---")
    
    log.info("Testing additive secret sharing...")

    graph.set_initial_values(range_start=0, range_end=100)
    graph.apply_shares(random_range=100.0)
    res = simulator.run_simulation(graph, config, name="ASS")
    results.append(res)

    dp_scales = [0.1, 1.0, 5.0]
    
    log.info("Testing differential privacy...")

    for dp_scale in dp_scales:
        config = SimulationConfig(
            max_iterations=100,
            epsilon=0.0,
            algorithm=Algorithm.SYNCHRONOUS,
            noise_scale=dp_scale,
            noise_distribution=NoiseDistribution.LAPLACE,
        )
        graph.set_initial_values(range_start=0, range_end=100)
        res = simulator.run_simulation(graph, config, name=f"DP {dp_scale}")
        results.append(res)

    visualizer.plot_convergence(
        results,
        save_path="figures/ass_dp_comparison/convergence.png",
        show=False,
    )
    
def dp_noise_distributions() -> None:
    """Compare different noise distributions for differential privacy.

    Runs a simulation of differential privacy (DP) for different noise distributions.

    Returns:
        None

    """
    graph = Graph(num_nodes=50, topology=Topology.MESH)
    simulator = Simulation()
    visualizer = Visualizer()

    results = []
    
    dp_scales = [0.1, 1.0, 5.0]
    
    log.info("--- Experiment: Differential Privacy Noise Distributions ---")
    for dp_scale in dp_scales:
        log.info(f"Testing different noise distributions for {dp_scale}...")
        for noise_distribution in NoiseDistribution:
            config = SimulationConfig(
                max_iterations=100,
                epsilon=0.0,
                algorithm=Algorithm.SYNCHRONOUS,
                noise_scale=dp_scale,
                noise_distribution=noise_distribution,
            )
            graph.set_initial_values(range_start=0, range_end=100)
            res = simulator.run_simulation(graph, config, name=f"DP {dp_scale} {noise_distribution.name}")
            results.append(res)

    visualizer.plot_convergence(
        results,
        save_path="figures/dp_noise_comparison/convergence.png",
        show=False,
    )
    
def experiment_scalability() -> None:
    """Compare how different topologies scale with network size.
    
    Generates one plot per topology, showing convergence curves
    for N = 10, 30, 50, 100.
    """
    node_counts = [10, 30, 50, 100]
    
    simulator = Simulation()
    visualizer = Visualizer()
    
    def get_max_iterations(topology: Topology) -> int:
        if topology == Topology.RING:
            return 10000
        elif topology in [Topology.TREE, Topology.STAR]:
            return 5000
        else:
            return 100
    
    log.info("--- Experiment: Scalability Analysis ---")

    for topology in Topology:
        log.info(f"Testing scalability for {topology.name}...")
        results = []
        
        for n in node_counts:
            graph = Graph(num_nodes=n, topology=topology)
            graph.set_initial_values(0, 100)
            graph.apply_shares(100.0)
            
            
            max_iters = get_max_iterations(topology)
            
            config = SimulationConfig(
                max_iterations=max_iters,
                epsilon=1e-6,
                algorithm=Algorithm.SYNCHRONOUS
            )
            
            res = simulator.run_simulation(graph, config, name=f"Topology {topology.name.capitalize()} ({n} Nodes)")
            
            results.append(res)
            
        visualizer.plot_convergence(
            results,
            save_path=f"figures/experiment_2/scalability_{topology.name}.png",
            show=False,
            y_min=1e-6
        )
        
        
def experiment_random_range() -> None:
    """Compare convergence for different random number ranges in ASS.
    
    The expectation is that the convergence RATE (slope) remains the same,
    but the initial error (starting Y-value) will be higher.
    """
    ranges = [10, 1000, 100000, 10000000]
    fixed_nodes = 50
    fixed_topology = Topology.MESH
    
    simulator = Simulation()
    visualizer = Visualizer()
    results = []
    graph = Graph(num_nodes=fixed_nodes, topology=fixed_topology)
    
    log.info(f"--- Experiment: Random Range Impact ---")

    for r in ranges:
        graph.set_initial_values(range_start=0, range_end=100)
        
        graph.apply_shares(random_range=float(r)) 
        
        config = SimulationConfig(
            max_iterations=200,
            epsilon=1e-6,
            algorithm=Algorithm.SYNCHRONOUS
        )
        
        log.info(f"Simulating Range +/- {r}...")
        res = simulator.run_simulation(graph, config, name="Range +/- " + str(r))
        
        results.append(res)
        
    visualizer.plot_convergence(
        results,
        save_path="figures/experiment_random_range/range_comparison.png",
        show=False,
        y_min=1e-6
    )


if __name__ == "__main__":
    ass_vs_dp()
    dp_noise_distributions()
    experiment_scalability()
    experiment_random_range()
