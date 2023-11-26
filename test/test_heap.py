from abc import ABC, abstractmethod
from cube_env.helpers.heap import MaxHeap, MinHeap, MaxHeapStrategy, MinHeapStrategy, HeapStrategy, Heap
from typing import List, DefaultDict
from collections import defaultdict

def test_create_max_heap() -> None:
    l = [5, 17, 10, 1, 2, 5, 19]
    max_heap = MaxHeap(l)
    assert max_heap.size == len(l)


def test_insert_max_heap() -> None:
    l = [5, 17, 10, 1, 2, 5, 19]
    max_heap = MaxHeap()
    for elem in l:
        max_heap.insert(elem)
    assert max_heap.size == len(l)


def test_stif_down_max_heap() -> None:
    l = [5, 17, 10, 1, 2, 5, 19]
    max_heap = MaxHeap(l)
    while max_heap.size > 2:
        max_heap.extract_max()
    max_heap.sift_down(0, MaxHeapStrategy())
    assert max_heap.mem == [2, 1]


def test_delete_max_in_max_heap_in_right_order() -> None:
    l = [5, 17, 10, 1, 2, 5, 19]
    initial_size, deleted_elems = len(l), 0
    max_heap = MaxHeap(l)
    while not max_heap.empty:
        assert max_heap.peek() == list(reversed(sorted(l)))[deleted_elems]
        max_heap.delete_max()
        deleted_elems += 1
        assert max_heap.size == initial_size-deleted_elems
    assert max_heap.mem == []


def test_max_heap_can_extract_max_in_sorted_order() -> None:
    l = [5, 17, 10, 1, 2, 5, 19]
    max_heap = MaxHeap(l)
    for elem in reversed(sorted(l)):
        assert elem == max_heap.extract_max()


def test_create_min_heap() -> None:
    l = [5, 17, 10, 1, 2, 5, 19]
    min_heap = MinHeap(l)
    assert min_heap.size == len(l)


def test_insert_min_heap() -> None:
    l = [5, 17, 10, 1, 2, 5, 19]
    min_heap = MinHeap()
    for elem in l:
        min_heap.insert(elem)
    assert min_heap.size == len(l)


def test_stif_down_min_heap() -> None:
    l = [5, 17, 10, 1, 2, 5, 19]
    min_heap = MinHeap(l)
    while min_heap.size > 2:
        min_heap.extract_min()
    min_heap.sift_down(0, MinHeapStrategy())
    assert min_heap.mem == [17, 19]


def test_delete_min_in_min_heap_in_right_order() -> None:
    l = [5, 17, 10, 1, 2, 5, 19]
    initial_size, deleted_elems = len(l), 0
    min_heap = MinHeap(l)
    while not min_heap.empty:
        assert min_heap.peek() == list(sorted(l))[deleted_elems]
        min_heap.delete_min()
        deleted_elems += 1
        assert min_heap.size == initial_size-deleted_elems
    assert min_heap.mem == []


def test_min_heap_can_extract_max_in_sorted_order() -> None:
    l = [5, 17, 10, 1, 2, 5, 19]
    min_heap = MinHeap(l)
    for elem in sorted(l):
        assert elem == min_heap.extract_min()


def test_min_heap_can_increment_at_index() -> None:
    l = [5, 17, 10, 1, 2, 5, 19]
    min_heap = MinHeap(l)
    pre_increment = min_heap.mem[3]
    min_heap.increment_at_index(3, -69)
    assert min_heap.peek() == pre_increment-69

class Graph:
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

class PriorityQueueStrategy(HeapStrategy):
    def heap_sift_down_order(self, first: List, second: List) -> bool:
        return first[0] <= second[0]
    
    def heap_sift_up_order(self, first: List, second: List) -> bool:
        return first[0] > second[0]

class AbstractPriorityQueue(Heap):
    @abstractmethod
    def add_with_priority(self, elem, priority) -> None:
        pass
    
    @abstractmethod
    def update_priority(self, elem, priority, order = PriorityQueueStrategy()) -> None:
        pass
    
    @abstractmethod
    def extract_min(self, order = PriorityQueueStrategy()):
        pass

class PriorityQueue(AbstractPriorityQueue):
    def add_with_priority(self, elem, priority) -> None:
        super().insert([priority, elem], PriorityQueueStrategy())

    def update_priority(self, elem, priority, order = PriorityQueueStrategy()) -> None:
        # TODO Oussama-Ben-Nasr: optimize this by adding reverse index 
        # get index in mem
        index: int
        for i, stored in enumerate(self.mem):
            if elem == stored[1]:
                index = i
        if index == None:
            raise Exception(f"There is no {elem} in the Queue.")
        # increase the priority
        self.mem[index][0] = priority
        self.sift_up(index, order)
        self.sift_down(index, order)

    def extract_min(self, order = PriorityQueueStrategy()):
        self.swap_index(0, self.size-1)
        min = self.mem.pop()
        self.sift_down(0, order)
        return min[1]


def test_priority_queue_from_heap() -> None:
    pq = PriorityQueue()
    for i in range(69):
        pq.add_with_priority(f"A complex element with priority {i+1}", i+1)
    for i in range(69):
        assert pq.extract_min().__contains__(f"{i+1}")


def test_update_priority_in_priority_queue_from_heap() -> None:
    pq = PriorityQueue()
    pq.add_with_priority("19", 19)
    pq.update_priority("19", 13)
    assert pq.extract_min().__contains__(f"{19}")
    pq.add_with_priority("19", 19)
    pq.add_with_priority("18", 18)
    pq.peek() == "18"
    pq.update_priority("19", 13)
    assert pq.extract_min().__contains__(f"{19}")    

def test_shortest_path_with_heap() -> None:
    g = Graph()

    g.add_edge(1, 2, 7)
    g.add_edge(1, 3, 9)
    g.add_edge(1, 6, 14)
    g.add_edge(2, 3, 10)
    g.add_edge(2, 4, 15)
    g.add_edge(3, 4, 11)
    g.add_edge(3, 6, 2)
    g.add_edge(5, 6, 9)
    g.add_edge(4, 5, 6)

    dist:List[float] = 7 * [0.0]
    prev:List[int] = 7 * [-1]
    source = 1
    pq = PriorityQueue()
    for node in g.nodes:
        prev[node] = -1
        dist[node] = float('inf')
        pq.add_with_priority(node, float('inf'))

    dist[source] = 0
    while not pq.empty:
        node = pq.extract_min()
        for neighbour in g.adj[node]:
            distance = dist[node] + g.get_weight(node, neighbour)
            if dist[neighbour] > distance:
                dist[neighbour] = distance
                prev[neighbour] = node
                pq.update_priority(neighbour, distance)
    assert dist == [0, 0, 7, 9, 20, 20, 11]
    assert prev == [-1, -1, 1, 1, 3, 6, 3]
    # TODO Oussama-Ben-Nasr: Refactor out from the test file and add shortest path construction
