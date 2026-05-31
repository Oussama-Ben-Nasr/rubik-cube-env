import logging
import twophase.solver as sv
from src.main.core.cube import RubikCube3D
from src.main.core.consts import code_to_actions

logging.basicConfig(level=logging.INFO, format="%(levelname)s:     %(message)s")
logger = logging.getLogger(__name__)


def solution(cube: RubikCube3D):
    cube_string_state = cube.export_as_kociemba_string() 
    logger.info(f"Targeting matrix layout string: {cube_string_state}")
    solution_output = sv.solve(cube_string_state, 19, 2)

    logger.info(f"Official Kociemba raw response string: {solution_output}")

    if not solution_output or "Error" in solution_output:
        return {"status": "already_solved_or_invalid", "moves_applied": []}

    raw_moves = solution_output.strip().split(" ")
    executable_actions = []
    solution = []

    for move in raw_moves:
        if not move:
            continue
            
        face = move[0]
        modifier = move[1]

        if modifier == '1':
            executable_actions.append(f"{face}'") 
        elif modifier == '3':
            executable_actions.append(face) 
        elif modifier == '2':
            executable_actions.append(face)
            executable_actions.append(face)

    logger.info(f"Executing inverted physical pathway onto 3D engine: {executable_actions}")

    for move_code in executable_actions:
        if move_code in code_to_actions:
            action_id = code_to_actions[move_code]
            solution += [f"Apply action: {action_id}, corresponding to thee move {move_code}."]

            
    return {
        "status": "solved",
        "raw_kociemba_notation": raw_moves,
        "actions_to_be_executed": solution
    }