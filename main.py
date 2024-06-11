from constants import N, SIMULATION_TIME, EPOCH_TIME
from network import finalise_network, get_server_data, inter_city_latency, filter_out_city
from contract import Contract
from peer import Peer
from helper import find_longest_shortest_path

import simpy
from pprint import pprint
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import csv
from datetime import datetime
import random

def initialize_peers(env):
    network = list()

    for _ in range(N):
        peer = Peer(env)
        peer.gen_key_pair()
        peer.register()
        network.append(peer)

    return network

def reset_peers(network, env):
    for peer in network:
        peer.reset(env)

def simulate_once(env):
    sc = Peer.contract
    for peer in Peer.network:
        # if(i%2):
        env.process(peer.generate_mssg())
        peer.is_gen_mssg = True
        env.process(peer.run())
        
    env.process(Peer.contract.get_primary_agg())

    env.run(until=SIMULATION_TIME)

    data = list()
    # header = ["Bandwidth", "Final balance", "Reward Earned", "Reward Cost", "Gas Cost"]
    header = ["SLOW?", "Final balance", "Reward Earned", "Reward Cost", "Gas Cost", "Total Neighbours", "Slow Neighbours"]
    data.append(header)
    for i in range(len(sc.balances)):
        slow_neigh = 0
        total_neigh = len(Peer.network[i].neighbours)
        for neigh in Peer.network[i].neighbours:
            slow_neigh += Peer.network[neigh].is_slow
        # row = [Peer.network[i].bandwidth, sc.balances[i], sc.reward_earned[i], sc.reward_cost[i], sc.gas_cost[i]]
        row = [Peer.network[i].is_slow, sc.balances[i], sc.reward_earned[i], sc.reward_cost[i], sc.gas_cost[i], total_neigh, slow_neigh/total_neigh]
        data.append(row)

    current_time = datetime.now()
    file_path = "./output/"+str(current_time.strftime("%d_%m_%Y_%H_%M_%S"))+".csv"
    with open(file_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(data)

def simulate_itr(itr, peer_id):
    band = Peer.network[0].bandwidth
    current_time = datetime.now()
    file_path = "./output/"+str(current_time.strftime("%d_%m_%Y_%H_%M_%S"))+".csv"
    
    data = list()
    header = ["Bandwidth", "Reward Earned"]
    data.append(header)
    for j in range(1, itr+1):
        env = simpy.Environment()
        Peer.contract.reset(env)
        sc = Peer.contract
        Peer.network[peer_id].bandwidth = band*j
        reset_peers(Peer.network, env)
        for peer in Peer.network:
            env.process(peer.generate_mssg())
            peer.is_gen_mssg = True
            env.process(peer.run())

        env.process(Peer.contract.get_primary_agg())

        env.run(until=SIMULATION_TIME)

        row = [Peer.network[peer_id].bandwidth, sc.reward_cost[peer_id]]
        data.append(row)

    with open(file_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(data)

def main():
    env = simpy.Environment()
    sc = Contract(env)
    # server_file = './data/servers.csv'
    # servers = get_server_data(server_file)

    latency_file = './data/pings-2020-07-19-2020-07-20.csv'
    city_latency = inter_city_latency(latency_file)
    Peer.city_latency = city_latency

    Peer.contract = sc
    Peer.network = initialize_peers(env)
    finalise_network(N, Peer.network, Peer.city_latency)

    adjacency_list = dict()
    for peer in Peer.network:
        adjacency_list[peer.id] = []
        for nei in peer.neighbours:
            adjacency_list[peer.id].append(nei)
    print("Longest Shortest Distance: ", find_longest_shortest_path(adjacency_list))

    simulate_once(env)

#     # Define node positions manually
#     np.random.seed(42)  # For reproducibility
#     positions = {node: np.random.rand(2) for node in adjacency_list.keys()}

#     fig, ax = plt.subplots(figsize=(8, 6))
#     for node, neighbors in adjacency_list.items():
#         for neighbor in neighbors:
#             node_pos = positions[node]
#             neighbor_pos = positions[neighbor]
#             ax.plot([node_pos[0], neighbor_pos[0]], [node_pos[1], neighbor_pos[1]], 'gray')

# # Draw nodes
#     for node, pos in positions.items():
#         ax.add_patch(patches.Circle(pos, radius=0.03, color='skyblue'))
#         ax.text(pos[0], pos[1], node, fontsize=12, ha='center', va='center', color='black')

#     # Set limits and title
#     ax.set_xlim(0, 1)
#     ax.set_ylim(0, 1)
#     ax.set_aspect('equal')
#     ax.set_title("Network Graph Visualization from Adjacency List")
#     ax.axis('off')  # Turn off the axis

#     plt.show()

    # peer_id = int(random.random() * (N+1))
    # print(peer_id)
    # simulate_itr(10, peer_id)
    


if __name__ == "__main__":
    main()