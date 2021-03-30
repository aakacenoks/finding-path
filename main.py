#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import csv
import re
import numpy


def get_dictionary_from_csv(file_path):
    """
    Get CSV file content as dictionary.

    :param file_path: Relative path to source file.
    :return: Dictionary containing CSV file content.
    """
    full_dictionary = []
    with open(file_path, mode='r') as file:
        reader = csv.DictReader(file, delimiter=',')
        for row in reader:
            full_dictionary.append(row)

    return full_dictionary


# Make dictionary easily usable
def create_graph():
    """
    Convert given dictionary to usable graph.

    :return: Dictionary containing usable graph structure. Example:
    {
        "A": {
            "B": { "distance": 10, "cost": 200 },
            "C": { "distance": 15, "cost": 350 }
        },
        "B": {
            "A": { "distance": 10, "cost": 200 },
        },
        "C": {
            "A": { "distance": 15, "cost": 350 },
        }
    }
    """
    dictionary = get_dictionary_from_csv('connections.csv')
    connections = {}
    for row in dictionary:
        for index, (ending_point, values) in enumerate(row.copy().items()):
            if index == 0:
                continue
            numbers = (numpy.array(re.findall("[0-9]+", values))).astype(int)
            if 0 in numbers:
                del row[ending_point]
            else:
                row[ending_point] = {"distance": numbers[0], "cost": numbers[0] * numbers[1]}
        starting_point = row["POINT"]
        row.pop("POINT")
        connections[starting_point] = row

    return connections


def calculate_shortest_paths(metric, graph, starting_vertex):
    """
    Calculate shortest paths for given graph by cost or distance starting from particular vertex.

    :param starting_vertex: Example: 'A'.
    :param graph: Graph structure as dictionary. For example see function create_graph().
    :param metric: Metric by which the path is considered best. Options: "cost" or "distance".
    :return: Dictionary with traveled distance, travel cost, nearest neighbour node starting given vertex. Example:
    {
        'A': { 'cost': 0,   'distance': 0, 'best_neighbour': None },
        'B': { 'cost': 200, 'distance': 10, 'best_neighbour': 'A' },
        'C': { 'cost': 350, 'distance': 15, 'best_neighbour': 'A' }
    }
    """
    nodes = {}
    unvisited_nodes = []

    for node in graph:
        nodes[node] = {}
        nodes[node]["cost"] = float("inf")
        nodes[node]["distance"] = float("inf")
        nodes[node]["best_neighbour"] = None
        unvisited_nodes.append(node)

    nodes[starting_vertex]["cost"] = 0
    nodes[starting_vertex]["distance"] = 0

    while unvisited_nodes:
        nearest_node = unvisited_nodes[0]
        minimum_value = nodes[nearest_node][metric]

        for unvisited_node in unvisited_nodes:
            if nodes[unvisited_node][metric] < minimum_value:
                nearest_node = unvisited_node
                minimum_value = nodes[nearest_node][metric]

        current_node = nearest_node
        unvisited_nodes.remove(current_node)
        recalculate_neighbour_position(graph, current_node, nodes, metric)

    return nodes


def recalculate_neighbour_position(graph, current_node, nodes, metric):
    """
    Iterate over neighbours of a node in graph to check if new shortest path is found.

    :param metric: "distance" or "cost.
    :param nodes: graph to be updated in case of valid recalculated distance/cost.
    :param current_node: node of which the neighbours with will be iterated/recalculated. Example: 'A'.
    :param graph: original graph.
    :return: Dictionary containing graph with possibly updated cost/distance.
    """
    for neighbour_node in graph[current_node]:
        alternate_distance = graph[current_node][neighbour_node]["distance"] + nodes[current_node]["distance"]
        alternate_cost = graph[current_node][neighbour_node]["cost"] + nodes[current_node]["cost"]

        if (metric == "distance" and nodes[neighbour_node]["distance"] > alternate_distance) or \
           (metric == "cost" and nodes[neighbour_node]["cost"] > alternate_cost):
            nodes[neighbour_node]["distance"] = int(alternate_distance)
            nodes[neighbour_node]["cost"] = int(alternate_cost)
            nodes[neighbour_node]["best_neighbour"] = current_node

    return nodes


def get_best_path(nodes, destination):
    """
    Get readable shortest path to destination node (starting node will have neighbour of None)

    :param nodes: graph containing result from calculate_shortest_paths
    :param destination: Destination node. Example: 'C'
    :return: String with shortest path. Example path from A to J: "A-G-C-J"
    """
    path = [destination]
    while True:
        destination = nodes[destination]["best_neighbour"]
        if destination is None:
            break
        else:
            path.append(destination)
    detailed_path = ''
    for node in path[::-1]:
        detailed_path += node + "-"

    return detailed_path[:-1]


def print_shortest_path(source, destination):
    """
    Print calculated best path based on distance (shortest) from source node to destination node.

    :param source: Source node. Example: "A".
    :param destination: Destination node. Example: "J".
    """
    nodes = calculate_shortest_paths("distance", create_graph(), source)
    print(f'Shortest path between {source} and {destination}:\n'
          f'Path: {get_best_path(nodes, destination)} \n'
          f'Distance: {nodes[destination]["distance"]}\n'
          f'Cost of travel: {nodes[destination]["cost"]}\n')


def print_cheapest_path(source, destination):
    """
    Print calculated best path based on travel cost (cheapest) from source node to destination node.

    :param source: Source node. Example: "A".
    :param destination: Destination node. Example: "J".
    """
    nodes = calculate_shortest_paths("cost", create_graph(), source)
    print(f'Cheapest path between {source} and {destination}:\n'
          f'Path: {get_best_path(nodes, destination)} \n'
          f'Distance: {nodes[destination]["distance"]}\n'
          f'Cost of travel: {nodes[destination]["cost"]}\n')


if __name__ == '__main__':
    """
    Take as input start and destination nodes. Example usage: "./main.py A J".
    """
    start = sys.argv[1]
    finish = sys.argv[2]
    print_shortest_path(start, finish)
    print_cheapest_path(start, finish)
