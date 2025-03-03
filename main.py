from constants import N, SIMULATION_TIME, EPOCH_TIME, RELAYER_ONLY, SLOW_PEERS
from network import finalise_network, get_server_data, inter_city_latency, filter_out_city
from contract import Contract
from peer import Peer
from helper import find_longest_shortest_path
import vrf

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
    # p1 = Peer.network[0]
    # x = p1.sortition()
    # print(x)
    # y = sc.verify_sortition(x[0],x[1], p1.pub_key)
    # y = vrf.verify_vrf_proof(p1.pub_key, sc.randao, x[0], x[1])
    # print(y)

    # return
    for peer in Peer.network:
        # if(i%2):
        if(not peer.relayer_only):
            env.process(peer.generate_mssg())
        peer.is_gen_mssg = True
        if(Peer.contract.sortition or peer.id == Peer.contract.primary):
            env.process(peer.run())
        
    env.process(Peer.contract.get_primary_agg())

    env.run(until=SIMULATION_TIME)

    data = list()
    # header = ["Bandwidth", "Final balance", "Reward Earned", "Reward Cost", "Gas Cost"]
    header = ["SLOW?", "Relayer Only?", "Reward Earned", "Reward Cost", "Gas Cost", "Total Neighbours", "Slow Neighbours"]
    data.append(header)
    for i in range(len(sc.balances)):
        slow_neigh = 0
        total_neigh = len(Peer.network[i].neighbours)
        for neigh in Peer.network[i].neighbours:
            slow_neigh += Peer.network[neigh].is_slow
        # row = [Peer.network[i].bandwidth, sc.balances[i], sc.reward_earned[i], sc.reward_cost[i], sc.gas_cost[i]]
        row = [int(Peer.network[i].is_slow), int(Peer.network[i].relayer_only), sc.reward_earned[i], sc.reward_cost[i], sc.gas_cost[i], total_neigh, slow_neigh/total_neigh]
        data.append(row)

    current_time = datetime.now()
    # file_path = f"./output/{str(SLOW_PEERS)}/{str(current_time.strftime("%d_%m_%Y_%H_%M_%S"))}.csv"
    file_path = "./output/" + str(SLOW_PEERS) + "/" + str(current_time.strftime("%d_%m_%Y_%H_%M_%S")) + ".csv"
    with open(file_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(data)

def simulate_itr(itr):
    peer_id = 0
    flag = True
    slow_count = 0

    # slow to fast
    while(not Peer.network[peer_id].is_slow or flag):
        flag = True
        peer_id = random.choice(list(range(N)))
        slow_count = 0
        for neigh in Peer.network[peer_id].neighbours:
            if not Peer.network[neigh].is_slow:
                flag = False
            else:
                slow_count+=1

    #fast to slow
    # while(Peer.network[peer_id].is_slow or flag):
    #     flag = True
    #     peer_id = random.choice(list(range(N)))
    #     slow_count = 0
    #     for neigh in Peer.network[peer_id].neighbours:
    #         if not Peer.network[neigh].is_slow:
    #             flag = False
    #         else:
    #             slow_count+=1

    current_time = datetime.now()
    file_path = "./output/" + str(SLOW_PEERS) + "/" + str(current_time.strftime("%d_%m_%Y_%H_%M_%S")) + ".csv"
 
    data = list()
    header = ["Reward Earned", "Reward Cost", "Gas Cost", "Total Neighbours", "Slow Neighbours"]
    data.append(header)
    for j in range(itr):
        env = simpy.Environment()
        Peer.contract.reset(env)
        sc = Peer.contract
        if j==1:
            # Peer.network[peer_id].is_slow = False
            Peer.network[peer_id].is_slow = True

        reset_peers(Peer.network, env)
        for peer in Peer.network:
            env.process(peer.generate_mssg())
            peer.is_gen_mssg = True
            env.process(peer.run())

        env.process(Peer.contract.get_primary_agg())

        env.run(until=SIMULATION_TIME)

        row = [sc.reward_earned[peer_id], sc.reward_cost[peer_id], sc.gas_cost[peer_id], len(Peer.network[peer_id].neighbours), slow_count/len(Peer.network[peer_id].neighbours)]
        data.append(row)

    with open(file_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(data)

def main():
    env = simpy.Environment()
    sc = Contract(env)
    # server_file = './data/servers.csv'
    # servers = get_server_data(server_file)

    latency_file = './data/pings.csv' #source: https://wp-public.s3.amazonaws.com/pings/pings-2020-07-19-2020-07-20.csv.gz
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

    # simulate_once(env)
    simulate_itr(2)

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