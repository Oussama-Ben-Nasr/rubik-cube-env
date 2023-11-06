from typing import Tuple


color = {
    0: "red",
    1: "orange",
    2: "blue",
    3: "white",
    4: "green",
    5: "yellow"
}

def cell_id_to_state_x_y(x: int) -> Tuple[int, int]:
    q: int = x//9
    r: int = x%9
    _x: int = r//3 + 3*(q//3)
    _y: int = r%3 + 3*(q%3)
    return (_x, _y)

def render(cube_env_inst):
    with open("cube_env/render/color_cube.js", "w") as f:
        for cell_id in range(54):
            f.write(f"document.getElementById(\"cell{cell_id}\").style.backgroundColor = \"{color[cube_env_inst._state[cell_id_to_state_x_y(cell_id)[0]][cell_id_to_state_x_y(cell_id)[1]]]}\";\n")
            if(cell_id == 53):
                f.write("exit();")