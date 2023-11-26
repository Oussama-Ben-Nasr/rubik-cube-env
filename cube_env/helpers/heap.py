from abc import ABC, abstractmethod
from typing import List

class HeapStrategy(ABC):
    @abstractmethod
    def heap_sift_down_order(self, first, second) -> bool:
        pass
    
    @abstractmethod
    def heap_sift_up_order(self, first, second) -> bool:
        pass

class MaxHeapStrategy(HeapStrategy):
    def heap_sift_down_order(self, first, second) -> bool:
        return first.__ge__(second)
    
    def heap_sift_up_order(self, first, second) -> bool:
        return first.__lt__(second)

class MinHeapStrategy(HeapStrategy):
    def heap_sift_down_order(self, first, second) -> bool:
        return first.__le__(second)
    
    def heap_sift_up_order(self, first: int, second: int) -> bool:
        return first.__gt__(second)

class Heap(ABC):
    """Heap commun implementation."""
    mem: List
    def __init__(self) -> None:
        self.mem = list()

    def peek(self):
        if self.empty:
            raise Exception("Peek on empty heap.")
        return self.mem[0]
    
    @property
    def size(self) -> int:
        """return the number of items in the heap."""
        return len(self.mem)
    
    @property
    def empty(self) -> bool:
        return 0 == len(self.mem)
    

    def valid_index(self, index: int) -> bool:
        return index >= 0 and index < self.size
    

    def has_parent(self, index: int) -> bool:
        return self.parent_index(index) >= 0
    
    def insert(self, key, order: HeapStrategy) -> None:
        self.mem.append(key)
        self.sift_up(self.size-1, order)
    
    def parent_index(self, index: int) -> int:
        """Return the parent index for a given node."""
        if self.size <= index:
            raise Exception(f"Index {index} greater than the size of the heap {self.size}")
        return (index - 1) // 2
    
    def right_child_index(self, index: int) -> int:
        """Return the right child index for a given node."""
        if self.size <= index:
            raise Exception(f"Index {index} greater than the size of the heap {self.size}")
        return 2*index + 2
    
    def left_child_index(self, index: int) -> int:
        """Return the left child index for a given node."""
        if self.size <= index:
            raise Exception(f"Index {index} greater than the size of the heap {self.size}")
        return 2*index + 1
    
    def swap_index(self, index: int, other: int) -> None:
        """Swap two nodes given their indexes."""
        self.mem[index], self.mem[other] = self.mem[other], self.mem[index]

    def sift_up(self, index: int, order: HeapStrategy) -> None:
        """
        Move a node up in the tree, as long as needed; used to restore heap condition after insertion. 
        Called "sift" because node moves up the tree until it reaches the correct level, as in a sieve.
            1. if I have a parent smaller than me swap and go up
        """
        val = self.mem[index]
        while self.has_parent(index) and order.heap_sift_up_order(self.mem[self.parent_index(index)], val):
            self.swap_index(index, self.parent_index(index))
            index = self.parent_index(index)

    def sift_down(self, index: int, order: HeapStrategy) -> None:
        """
        Move a node down in the tree, similar to sift-up; used to restore heap condition after deletion or replacement.
            1. if has no chilren then return
            2. has left child only then swap if this child id greater than me
            3. has left and right children then swap with the biggest child
        """
        if self.empty:
            return
        val = self.mem[index]
        while self.valid_index(self.left_child_index(index)) or self.valid_index(self.right_child_index(index)):
            if self.valid_index(self.left_child_index(index)) and self.valid_index(self.right_child_index(index)):
                if order.heap_sift_down_order(val, self.mem[self.left_child_index(index)]) and order.heap_sift_down_order(val,  self.mem[self.right_child_index(index)]):
                    return
                left_val = self.mem[self.left_child_index(index)]
                right_val = self.mem[self.right_child_index(index)]
                if order.heap_sift_down_order(left_val, right_val):
                    self.swap_index(index, self.left_child_index(index))
                    index = self.left_child_index(index)
                else:
                    self.swap_index(index, self.right_child_index(index))
                    index = self.right_child_index(index)
            else:
                if order.heap_sift_down_order(val, self.mem[self.left_child_index(index)]):
                    return
                self.swap_index(index, self.left_child_index(index))
                index = self.left_child_index(index)
    
    def increment_at_index(self, index: int, delta: int, order: HeapStrategy) -> None:
        self.mem[index] += delta
        self.sift_up(index, order)
        self.sift_down(index, order)

class MaxHeap(Heap):
    def __init__(self, container: list = []) -> None:
        super().__init__()
        for key in container:
            self.insert(key)
        
    def insert(self, key: int, order: HeapStrategy= MaxHeapStrategy()) -> None:
        return super().insert(key, order)

    def extract_max(self) -> int:
        self.swap_index(0, self.size-1)
        max = self.mem.pop()
        self.sift_down(0, MaxHeapStrategy())
        return max
    
    def delete_max(self) -> None:
        self.swap_index(0, self.size-1)
        self.mem.pop()
        self.sift_down(0, MaxHeapStrategy())
    
    def increment_at_index(self, index: int, delta: int, order: HeapStrategy= MaxHeapStrategy()) -> None:
        return super().increment_at_index(index, delta, order)

class MinHeap(Heap):
    def __init__(self, container: list = []) -> None:
        super().__init__()
        for key in container:
            self.insert(key)
    
    def insert(self, key: int, order: HeapStrategy= MinHeapStrategy()) -> None:
        return super().insert(key, order)


    def extract_min(self) -> int:
        self.swap_index(0, self.size-1)
        min = self.mem.pop()
        self.sift_down(0, MinHeapStrategy())
        return min
    
    def delete_min(self) -> None:
        self.swap_index(0, self.size-1)
        self.mem.pop()
        self.sift_down(0, MinHeapStrategy())
    
    def increment_at_index(self, index: int, delta: int, order: HeapStrategy= MinHeapStrategy()) -> None:
        return super().increment_at_index(index, delta, order)
