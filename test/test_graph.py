
from cube_env.helpers.graph import Graph


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

    assert g.get_shortest_path(1, 4) == "1 -> 3 -> 4"
