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
from uuid import uuid4
from fastapi import Request, Response
from fastapi import Header
load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(levelname)s:     %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI()

cubes: dict[str, RubikCube3D] = {}
historical_moves = deque()
SOLVES_TABLE = "solves_dev" if os.getenv("RUBIK_CUBE_DEV", "").lower() == "true" else "solves"

def get_cube(request: Request, response: Response) -> RubikCube3D:
    session_id = request.cookies.get("session_id")

    if not session_id:
        session_id = str(uuid4())
        response.set_cookie(
            "session_id",
            session_id,
            max_age=60 * 60 * 24 * 30,
            samesite="lax",
        )

    if session_id not in cubes:
        cubes[session_id] = RubikCube3D()

    return cubes[session_id]

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
def move(
    action: int,
    request: Request,
    response: Response,
):
    cube = get_cube(request, response)

    cube.apply_action(action)
    historical_moves.append(actions_to_codes[action])

    return {"status": "ok"}

@app.post("/finished")
def finished(
    request: Request,
    response: Response,
):
    cube = get_cube(request, response)

    cube._competing = False

    return {"status": "ok"}

@app.post("/scramble")
def scramble(
    request: Request,
    response: Response,
):
    cube = get_cube(request, response)

    is_dev = os.environ.get(
        "RUBIK_CUBE_DEV",
        ""
    ).lower() == "true"

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
def solve_cube(
    request: Request,
    response: Response,
    x_admin_password: str | None = Header(None),
):
    if x_admin_password != os.environ.get("ADMIN_PASSWORD", ""):
        raise HTTPException(
            status_code=403,
            detail="Forbidden"
        )

    cube = get_cube(request, response)

    try:
        return solution(cube)

    except Exception as e:
        logger.error(
            f"Official solver pipeline exception crashed: {str(e)}"
        )

        raise HTTPException(
            status_code=400,
            detail=f"Error evaluating cube layout matrix states: {str(e)}"
        )
@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return FileResponse("src/main/ui/favicon.ico")

@app.post("/reset")
def reset(
    request: Request,
    response: Response,
):
    cube = get_cube(request, response)

    cube.reset()

    return {"status": "ok"}

@app.get("/cube")
def get_cube_state(
    request: Request,
    response: Response,
):
    cube = get_cube(request, response)

    return cube.export()

@app.get("/cube-export")
def cube_export(
    request: Request,
    response: Response,
):
    cube = get_cube(request, response)

    return cube.export_as_kociemba_string()

@app.post("/solve")
def save_solve(payload: dict = Body(...)):
    conn = get_conn()

    with conn.cursor() as cur:
        cur.execute(
            f"""
            insert into {SOLVES_TABLE} (
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
def status(
    request: Request,
    response: Response,
):
    cube = get_cube(request, response)

    return cube.status()

from datetime import datetime, timezone
from typing import Literal

@app.get("/leaderboard")
def leaderboard(period: Literal["today", "all"] = "all"):
    conn = get_conn()

    date_filter = "and created_at >= current_date" if period == "today" else ""

    with conn.cursor() as cur:
        sql = f"""
            select distinct on (nickname)
                nickname,
                solve_time_ms,
                moves,
                created_at
            from {SOLVES_TABLE}
            where id > 0
              {date_filter}
            order by nickname, solve_time_ms asc
            """
        cur.execute(
            sql,
        )
        rows = cur.fetchall()

    rows.sort(key=lambda r: r[1])
    rows = rows[:20]

    return [
        {
            "nickname": row[0],
            "solve_time_ms": row[1],
            "moves": row[2],
            "created_at": row[3],
        }
        for row in rows
    ]