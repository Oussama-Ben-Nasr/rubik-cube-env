from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from cube_env.cube import RubikCube3D

app = FastAPI()

cube = RubikCube3D()

app.mount(
    "/static",
    StaticFiles(directory="cube_env/render"),
    name="static"
)

@app.get("/")
def home():
    return FileResponse("cube_env/render/index.html")


@app.post("/move/{action}")
def move(action: int):
    cube.apply_action(action)
    return {"status": "ok"}


@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return FileResponse("cube_env/render/favicon.ico")

@app.post("/reset")
def reset():
    cube.reset()
    return {"status": "ok"}


@app.get("/cube")
def get_cube():
    return cube.export()