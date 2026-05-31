from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from src.main.core.cube import RubikCube3D
from collections import deque
from random import randint, seed
import logging
from src.main.core.solver import solution
from src.main.core.consts import actions_to_codes

logging.basicConfig(level=logging.INFO, format="%(levelname)s:     %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI()

cube = RubikCube3D()
historical_moves = deque()


app.mount(
    "/static",
    StaticFiles(directory="src/main/ui"),
    name="static"
)

@app.get("/")
def home():
    logger.info("The root endpoint was successfully hit!")
    return FileResponse("src/main/ui/index.html")


@app.post("/move/{action}")
def move(action: int):
    cube.apply_action(action)
    historical_moves.append(actions_to_codes[action])
    return {"status": "ok"}

@app.post("/scramble")
def scramble():
    seed(12345)
    scrambling_sequence = ""
    for _ in range(20):
        action = randint(0, 11)
        cube.apply_action(action)
        scrambling_sequence += f"{actions_to_codes[action]} "
    logger.info(scrambling_sequence)
    return {"status": "ok"}

@app.post("/solve")
def solve_cube():
    try:
        return solution(cube)

    except Exception as e:
        logger.error(f"Official solver pipeline exception crashed: {str(e)}")
        raise HTTPException(
            status_code=400, 
            detail=f"Error evaluating cube layout matrix states: {str(e)}"
        )

@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return FileResponse("src/main/ui/favicon.ico")

@app.post("/reset")
def reset():
    cube.reset()
    return {"status": "ok"}


@app.get("/cube")
def get_cube():
    return cube.export()