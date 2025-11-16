from secret_sharing import Graph, Topology, Simulation, Visualizer
from utils.logging import get_colored_logger

log = get_colored_logger(__name__)

graph = Graph(num_nodes=10, topology=Topology.RING)
graph.set_initial_values(range_start=10, range_end=100)
graph.apply_shares(random_range=100)

simulator = Simulation()
visualizer = Visualizer()
error_list_sync, iterations_sync, avg_sync = simulator.run_ass_synchronous(graph)
error_list_async, iterations_async, avg_async = simulator.run_ass_asynchronous(graph)

log.info(f"Synchronous Iterations: {iterations_sync}")
log.info(f"Asynchronous Iterations: {iterations_async}")
log.info(f"Synchronous Average: {avg_sync}")
log.info(f"Asynchronous Average: {avg_async}")
log.info(f"True Average: {graph.true_avg}")

