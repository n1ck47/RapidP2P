import random
import csv

from constants import MIN_LINKS, MAX_LINKS

def filter_out_city(adjacency_list):
    to_del = []
    for source, _ in adjacency_list.items():
        if source not in adjacency_list[source]:
            to_del.append(source)
    
    for id in to_del:
        del adjacency_list[id]

def inter_city_latency(file_path):
    adjacency_list = {}

    with open(file_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            source = row['source']
            destination = row['destination']
            avg_latency = float(row['avg'])
            
            if source not in adjacency_list:
                adjacency_list[source] = {}
            
            adjacency_list[source][destination] = avg_latency
    
    return adjacency_list

def get_server_data(file_path):
    servers = {}

    with open(file_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            id = row['id']
            city = row['location']
            
            servers[id] = city
    
    return servers

def create_network(network, next_elms, que, city_latency):
    visited = [False for _ in range(len(network))]
    
    while que:
        links = random.randint(MIN_LINKS, MAX_LINKS)
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
            u_city_id = network[u].city_id
            v_city_id = network[v].city_id

            if (v_city_id not in city_latency[u_city_id]) and (u_city_id not in city_latency[v_city_id]):
                i+=1
                continue
            
            if (v_city_id not in city_latency[u_city_id]):
                city_latency[u_city_id][v_city_id] = city_latency[v_city_id][u_city_id] 
            elif (u_city_id not in city_latency[v_city_id]):
                city_latency[v_city_id][u_city_id] = city_latency[u_city_id][v_city_id]

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
        if len(network[i].neighbours) < MIN_LINKS:
            print(f"peer {i} has less than {MIN_LINKS} connections")
            return False
    print(f"All peers have at least {MIN_LINKS} connections")
    return True

def print_network(network):
    for peer in network:
        print(f"peer {peer.id} (Slow={peer.is_slow}): {peer.neighbours}")
        # print(f"peer {peer.id} ({peer.bandwidth:.2f} Mbps): {peer.neighbours}")

def finalise_network(n, network, city_latency):
    attempt = 0
    while attempt < 100:
        attempt += 1
        print(f"Attempt {attempt}: Creating network")
        reset_network(network)
        create_network(network, list(range(n)), [0], city_latency)
        if is_connected(network) and check_links(network):
            print_network(network)
            return
    print("Failed to create a connected network after 100 attempts")
