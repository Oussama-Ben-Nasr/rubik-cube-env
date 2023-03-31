import numpy as  np
def swap_blocks(array: np.ndarray, x1: int, y1: int, x2: int, y2: int) -> None:
    st_value = array[x1, y1]
    nd_value = array[x2, y2]
    array.flat[[range(9 * x1 + y1, 9 * x1 + y1 + 3)]] = nd_value
    array.flat[[range(9 * x2 + y2, 9 * x2 + y2 + 3)]] = st_value