import random

def create_network(network, next_elms, que):
    visited = [False for _ in range(len(network))]
    
    while que:
        links = random.randint(4, 8)
        next_elms = random.sample(next_elms, len(next_elms))
        u = que.pop(0)
        visited[u] = True
        next_elms.remove(u)
        size = links - len(network[u].neighbours)
        start = len(network[u].neighbours)

        i = 0
        while next_elms:
            if i >= len(next_elms):
                break

            v = next_elms[i]
            if (len(network[v].neighbours) < links and len(network[u].neighbours) < links):
                network[v].neighbours.append(u)
                network[u].neighbours.append(v)
                i += 1
            elif len(network[v].neighbours) < links:
                break
            elif len(network[u].neighbours) < links:
                i += 1
            else:
                break

        for i in range(start, len(network[u].neighbours)):
            neighbor_id = network[u].neighbours[i]
            if not visited[neighbor_id]:
                que.append(neighbor_id)
                visited[neighbor_id] = True
        # print(f"peer {u} connections: {len(network[u].neighbours)}")

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
            print(f"peer {i} has less than 4 connections")
            return False
    print("All peers have at least 4 connections")
    return True

def print_network(network):
    for peer in network:
        print(f"peer {peer.id} ({peer.bandwidth:.2f} Mbps): {peer.neighbours}")

def finalise_network(n, network):
    attempt = 0
    while attempt < 100:
        attempt += 1
        print(f"Attempt {attempt}: Creating network")
        reset_network(network)
        create_network(network, list(range(n)), [0])
        if is_connected(network) and check_links(network):
            print_network(network)
            return
    print("Failed to create a connected network after 100 attempts")
