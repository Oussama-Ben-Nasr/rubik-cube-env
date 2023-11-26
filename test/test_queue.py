
from cube_env.helpers.priority_queue import PriorityQueue


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
