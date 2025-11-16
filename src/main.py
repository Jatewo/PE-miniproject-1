from classes import Graph, Topology
from utils.logging import get_colored_logger

log = get_colored_logger(__name__)

# 1. Create the graph
graph = Graph(num_nodes=10, topology=Topology.RING)

graph.set_initial_values(range_start=10, range_end=100)

# 3. Run the one-time secret sharing setup
graph.apply_shares(random_range=100)

secret_avg = sum(n.value for n in graph.nodes) / 10.0

# --- Verification (Optional) ---
# The sum of secret values should equal the sum of initial values.

print(f"True Average: {graph.true_avg}")
print(f"Secret Average: {secret_avg}") # These should be identical!
