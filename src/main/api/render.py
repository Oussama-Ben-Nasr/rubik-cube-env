from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from src.main.core.cube import RubikCube3D
from collections import deque
from random import randint, seed
import logging
from src.main.core.solver import solution
from src.main.core.consts import actions_to_codes
from fastapi import Body
from src.main.api.db import get_conn
import os
from dotenv import load_dotenv
from datetime import datetime, timezone
load_dotenv()

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

@app.post("/finished")
def finished():
    cube._competing = False
    return {"status": "ok"}

@app.post("/scramble")
def scramble():
    is_dev = os.environ.get("RUBIK_CUBE_DEV", "").lower() == "true"
    if is_dev:
        cube.apply_action(0)
        cube.apply_action(0)
        cube.competitor_start()
        return {"status": "ok"}
    
    scrambling_sequence = ""
    for _ in range(20):
        action = randint(0, 11)
        cube.apply_action(action)
        scrambling_sequence += f"{actions_to_codes[action]} "
    logger.info(scrambling_sequence)
    cube.competitor_start()
    return {"status": "ok"}

@app.post("/solution")
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

@app.get("/cube-export")
def get_cube():
    return cube.export_as_kociemba_string()

@app.post("/solve")
def save_solve(payload: dict = Body(...)):
    conn = get_conn()

    with conn.cursor() as cur:
        cur.execute(
            """
            insert into solves (
                nickname,
                solve_time_ms,
                moves
            )
            values (%s, %s, %s)
            """,
            (
                payload.get("nickname"),
                payload["solve_time_ms"],
                payload["moves"],
            ),
        )

    conn.commit()

    return {"success": True}

@app.get("/status")
def status():
    return cube.status()


@app.get("/leaderboard")
def leaderboard():
    conn = get_conn()

    with conn.cursor() as cur:
        cur.execute(
            """
            select
                nickname,
                solve_time_ms,
                moves,
                created_at
            from solves
            where id > 12
            order by solve_time_ms asc
            limit 20
            """
        )

        rows = cur.fetchall()

    return [
        {
            "nickname": row[0],
            "solve_time_ms": row[1],
            "moves": row[2],
            "created_at": row[3],
        }
        for row in rows
    ]