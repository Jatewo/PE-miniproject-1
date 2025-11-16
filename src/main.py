from secret_sharing import Graph, Topology, Simulation, Visualizer
from utils.logging import get_colored_logger
from argparse import ArgumentParser

argparser = ArgumentParser()
argparser.add_argument(
    "-t",
    "--topology",
    type=str,
    default="RING",
    help="Topology of the graph. Possible values: RING, STAR, TREE, MESH, FULL",
)
argparser.add_argument(
    "-n", "--num_nodes", type=int, default=10, help="Number of nodes in the graph"
)
argparser.add_argument(
    "-l", "--lower_bound", type=int, default=10, help="Lower bound for initial values"
)
argparser.add_argument(
    "-u", "--upper_bound", type=int, default=100, help="Upper bound for initial values"
)
argparser.add_argument(
    "-r", "--random_range", type=int, default=100, help="Random range for shares"
)
argparser.add_argument(
    "-v", "--visualize", action="store_true", help="Visualize the graph"
)
argparser.add_argument(
    "-p", "--plot", action="store_true", help="Plot the error history"
)
args = argparser.parse_args()

log = get_colored_logger(__name__)

graph = Graph(num_nodes=args.num_nodes, topology=Topology[args.topology])
graph.set_initial_values(range_start=args.lower_bound, range_end=args.upper_bound)
graph.apply_shares(random_range=args.random_range)

simulator = Simulation()
visualizer = Visualizer()
error_list_sync, iterations_sync, avg_sync = simulator.run_ass_synchronous(graph)
error_list_async, iterations_async, avg_async = simulator.run_ass_asynchronous(graph)

log.info(f"Synchronous Iterations: {iterations_sync}")
log.info(f"Asynchronous Iterations: {iterations_async}")
log.info(f"Synchronous Average: {avg_sync}")
log.info(f"Asynchronous Average: {avg_async}")
log.info(f"True Average: {graph.true_avg}")


graph_drawing = visualizer.draw_graph(
    graph,
    title=f"Graph Topology: {args.topology}",
    save_path="figures/graph.png",
    show=args.visualize,
)

if args.plot:
    visualizer.plot_convergence(
        [
            (error_list_sync, "Synchronous", 1),
            (error_list_async, "Asynchronous", args.num_nodes),
        ],
        title="Convergence",
        save_path="figures/convergence.png",
        show=args.plot,
    )
