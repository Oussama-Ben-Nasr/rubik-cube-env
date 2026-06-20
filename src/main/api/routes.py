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
from typing import Literal
from time import time

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(levelname)s:     %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI()

cubes: dict[str, RubikCube3D] = {}
snapshots: dict[str, dict[str, list]] = {}
historical_moves = deque()
SOLVES_TABLE = "solves_dev" if os.getenv("RUBIK_CUBE_DEV", "").lower() == "true" else "solves"

def _session_id(request: Request, response: Response) -> str:
    """Return existing session cookie or mint a new one."""
    sid = request.cookies.get("session_id")
    if not sid:
        sid = str(uuid4())
        response.set_cookie(
            "session_id",
            sid,
            max_age=60 * 60 * 24 * 30,
            samesite="lax",
        )
    return sid

def get_cube(request: Request, response: Response) -> RubikCube3D:
    sid = _session_id(request, response)
    if sid not in cubes:
        cubes[sid] = RubikCube3D()
    return cubes[sid]
 
 
def get_snapshots(request: Request, response: Response) -> dict[str, list]:
    sid = _session_id(request, response)
    if sid not in snapshots:
        snapshots[sid] = {}
    return snapshots[sid]

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

@app.get("/leaderboard")
def leaderboard(period: Literal["today", "all"] = "all"):
    start = time()

    logger.info(
        f"Leaderboard request started period={period}"
    )

    try:

        # existing code
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


        logger.info(
            f"Leaderboard request finished "
            f"in {(time()-start):.3f}s"
        )

        return [
            {
                "nickname": row[0],
                "solve_time_ms": row[1],
                "moves": row[2],
                "created_at": row[3],
            }
            for row in rows
        ]

    except Exception:

        logger.exception(
            "Leaderboard request failed"
        )

        raise

    finally:

        logger.info(
            f"Leaderboard request cleanup "
            f"in {(time()-start):.3f}s"
        )


@app.post("/snapshot/save")
def save_snapshot(body: dict, request: Request, response: Response):
    """
    Body: { "snapshot_id": "<uuid>" }
    Saves the current cube state under that id for this session.
    """
    snapshot_id = body.get("snapshot_id")
    if not snapshot_id:
        return {"status": "error", "detail": "snapshot_id required"}, 400
 
    cube  = get_cube(request, response)
    store = get_snapshots(request, response)
    store[snapshot_id] = cube.get_state()
 
    logger.info(f"Snapshot saved id={snapshot_id}")
    return {"status": "ok", "snapshot_id": snapshot_id}


@app.post("/snapshot/load")
def load_snapshot(body: dict, request: Request, response: Response):
    """
    Body: { "snapshot_id": "<uuid>" }
    Restores the cube to the state stored under that id.
    """
    snapshot_id = body.get("snapshot_id")
    if not snapshot_id:
        return {"status": "error", "detail": "snapshot_id required"}, 400
 
    store = get_snapshots(request, response)
 
    # FIX: was doing snapshots["cubeState"] — wrong key, wrong dict
    if snapshot_id not in store:
        return {"status": "error", "detail": "snapshot not found"}, 404
 
    cube = get_cube(request, response)
    cube.load_state(store[snapshot_id])
 
    logger.info(f"Snapshot loaded id={snapshot_id}")
    return {"status": "ok"}

 
@app.get("/snapshot/list")
def list_snapshots(request: Request, response: Response):
    """Return all snapshot ids for this session."""
    store = get_snapshots(request, response)
    return {"snapshot_ids": list(store.keys())}