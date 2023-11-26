from abc import ABC, abstractmethod
from cube_env.helpers.priority_queue import AbstractPriorityQueue, PriorityQueue
from typing import List, DefaultDict
from collections import defaultdict

class AbstractGraph(ABC):
    @abstractmethod
    def add_node(self, id) -> None:
        pass
    
    @abstractmethod
    def add_edge(self, from_node, to_node, weight) -> None:
        pass
    
    @abstractmethod
    def get_weight(self, from_node, to_node) -> float:
        pass
    
    @abstractmethod
    def get_shortest_path(self, source, target, pq: AbstractPriorityQueue) -> str:
        pass

class Graph(AbstractGraph):
    adj:DefaultDict[int, List[int]] = defaultdict(list)
    weights:DefaultDict[str, float] = defaultdict(float)

    @property
    def nodes(self):
        return self.adj.keys()

    def add_node(self, index: int) -> None:
        if not index in self.adj.keys():
            self.adj[index] = []

    def add_edge(self, from_index: int, to_index: int, weight: int) -> None:
        self.adj[from_index].append(to_index)
        self.adj[to_index].append(from_index)
        key = [from_index, to_index]
        key.sort()
        self.weights[str(key)] = weight

    def get_weight(self, from_index, to_index) -> float:
        key = [from_index, to_index]
        key.sort()
        if str(key) in self.weights.keys():
            return self.weights[str(key)]
        raise Exception(f"No edge found from {from_index} to {to_index}.")
    
    def get_shortest_path(self, source, target, pq = PriorityQueue()) -> str:
        # Dijkistra with PQ
        dist:List[float] = (len(self.nodes)+1) * [0.0]
        prev:List[int] = (len(self.nodes)+1) * [-1]

        for node in self.nodes:
            prev[node] = -1
            dist[node] = float('inf')
            pq.add_with_priority(node, float('inf'))

        dist[source] = 0
        while not pq.empty:
            node = pq.extract_min()
            for neighbour in self.adj[node]:
                distance = dist[node] + self.get_weight(node, neighbour)
                if dist[neighbour] > distance:
                    dist[neighbour] = distance
                    prev[neighbour] = node
                    pq.update_priority(neighbour, distance)
        shortest_path = [target]
        while prev[target] != -1:
            shortest_path.append(prev[target])
            target = prev[target]
        return (
            " -> "
                .join(
                    map(
                        str, reversed(shortest_path)
                    )
                )
            )
