import heapq
import sys

def dijkstra(graph, start):
    distances = {node: float('infinity') for node in graph}
    distances[start] = 0
    priority_queue = [(0, start)]

    while priority_queue:
        current_distance, current_node = heapq.heappop(priority_queue)

        if current_distance > distances[current_node]:
            continue

        for neighbor in graph[current_node]:
            distance = current_distance + 1

            if distance < distances[neighbor]:
                distances[neighbor] = distance
                heapq.heappush(priority_queue, (distance, neighbor))

    return distances

def find_longest_shortest_path(graph):
    longest_shortest_path = 0

    for node in graph:
        shortest_paths = dijkstra(graph, node)
        max_distance = max(shortest_paths.values())
        if max_distance < float('infinity'):
            longest_shortest_path = max(longest_shortest_path, max_distance)

    return longest_shortest_path

