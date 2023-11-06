color = {
    0: "red",
    1: "orange",
    2: "blue",
    3: "white",
    4: "green",
    5: "yellow"
}

def render(cube_env_inst):
    with open("cube_env/render/color_cube.js", "w") as f:
        for cell_id in range(54):
            f.write(f"document.getElementById(\"cell{cell_id}\").style.backgroundColor = \"{color[cube_env_inst._state[cell_id // 9][cell_id % 9]]}\";\n")
            if(cell_id == 53):
                f.write("exit();")