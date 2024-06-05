import random
import numpy as np

class Node:
    def __init__(self, id, bandwidth):
        self.id = id
        self.bandwidth = bandwidth
        self.neighbours = {}  # Dictionary to store neighbours and their latencies

def calculate_latency(ρij, message_length, cij, dij):
    return ρij + (message_length / cij) + dij

def create_network(network, next_elms, que, adv_neighbors):
    visited = [False for _ in range(len(network))]
    n = len(network)
    while que:
        links = random.randint(4, 8)
        next_elms = random.sample(next_elms, len(next_elms))
        u = que.pop(0)
        visited[u] = True
        if u == 0:
            links = int((n-1) * adv_neighbors)
        next_elms.remove(u)
        size = links - len(network[u].neighbours)
        start = len(network[u].neighbours)

        i = 0
        while i < len(next_elms) and size > 0:
            v = next_elms[i]
            if len(network[v].neighbours) < links and len(network[u].neighbours) < links:
                ρij = random.uniform(0.01, 0.5)
                cij = 100 * 10**6 if network[u].bandwidth == 'fast' and network[v].bandwidth == 'fast' else 5 * 10**6
                dij = np.random.exponential(scale=(96 * 10**3) / cij)
                network[u].neighbours[v] = (ρij, cij, dij)
                network[v].neighbours[u] = (ρij, cij, dij)
                size -= 1
            i += 1

        for i in range(start, len(network[u].neighbours)):
            neighbor_id = list(network[u].neighbours.keys())[i]
            if not visited[neighbor_id]:
                que.append(neighbor_id)
                visited[neighbor_id] = True
        print(f"Node {u} connections: {len(network[u].neighbours)}")

def dfs(u, network, visited):
    visited[u] = True
    for elm in network[u].neighbours:
        if not visited[elm]:
            dfs(elm, network, visited)

def is_connected(network):
    visited = [False for _ in range(len(network))]
    dfs(0, network, visited)
    connected = all(visited)
    print(f"Network connected: {connected}")
    return connected

def reset_network(network):
    for i in range(len(network)):
        network[i].neighbours.clear()

def check_links(network):
    for i in range(1, len(network)):
        if len(network[i].neighbours) < 4:
            print(f"Node {i} has less than 4 connections")
            return False
    print("All nodes have at least 4 connections")
    return True

def print_network(network):
    for node in network:
        print(f"Node {node.id} ({node.bandwidth}):")
        for neigh, (ρij, cij, dij) in node.neighbours.items():
            print(f"  -> Node {neigh} with latency (ρij={ρij:.3f}s, cij={cij/1e6:.1f}Mbps, dij={dij:.3f}s)")

def initialize_minimum_connections(network):
    n = len(network)
    for i in range(1, n):
        u = i
        v = random.choice(range(i))  # Connect to any previous node to ensure connectivity
        ρij = random.uniform(0.01, 0.5)
        cij = 100 * 10**6 if network[u].bandwidth == 'fast' and network[v].bandwidth == 'fast' else 5 * 10**6
        dij = np.random.exponential(scale=(96 * 10**3) / cij)
        network[u].neighbours[v] = (ρij, cij, dij)
        network[v].neighbours[u] = (ρij, cij, dij)
    print("Minimum connections initialized")

def finalise_network(n, network, adversary_neighbors):
    attempt = 0
    while attempt < 100:
        attempt += 1
        print(f"Attempt {attempt}: Creating network")
        reset_network(network)
        initialize_minimum_connections(network)  # Ensure minimum connections
        create_network(network, list(range(n)), [0], adversary_neighbors)
        if is_connected(network) and check_links(network):
            print_network(network)
            return
    print("Failed to create a connected network after 100 attempts")

# Example usage
n = 10
bandwidths = ['fast', 'slow']
network = [Node(i, random.choice(bandwidths)) for i in range(n)]
finalise_network(n, network, adversary_neighbors=0.1)
