from cube_env.helpers.heap import MaxHeap, MinHeap, MaxHeapStrategy, MinHeapStrategy

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
