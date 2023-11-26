from abc import ABC, abstractmethod
from cube_env.helpers.heap import HeapStrategy, Heap
from typing import List, DefaultDict
from collections import defaultdict

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
        # update the priority
        self.mem[index][0] = priority
        self.sift_up(index, order)
        self.sift_down(index, order)

    def extract_min(self, order = PriorityQueueStrategy()):
        self.swap_index(0, self.size-1)
        min = self.mem.pop()
        self.sift_down(0, order)
        return min[1]
