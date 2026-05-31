import numpy as np
from dataclasses import dataclass, field
from datetime import datetime, timezone

X, Y, Z = 0, 1, 2


@dataclass
class Cubie:
    pos: np.ndarray
    colors: dict = field(default_factory=dict)


class RubikCube3D:
    _move_count: int = 0
    _start_solve = None
    _competing = False

    def reset_moves_count(self):
        self._move_count = 0
        self._competing = False

    def competitor_start(self):
        self._move_count = 0
        self._competing = True
        self._start_solve = datetime.now(timezone.utc).isoformat()
    

    def __init__(self):
        self.reset()

    def reset(self):
        self.reset_moves_count()
        self._start_solve = None
        self._competing = False
        self.cubies = self._init_cubies()

    def _init_cubies(self):
        cubies = []

        for x in [-1, 0, 1]:
            for y in [-1, 0, 1]:
                for z in [-1, 0, 1]:

                    if x == y == z == 0:
                        continue

                    colors = {}

                    if y == 1:  colors["U"] = 0
                    if y == -1: colors["D"] = 2
                    if z == 1:  colors["F"] = 1
                    if z == -1: colors["B"] = 4
                    if x == -1: colors["L"] = 3
                    if x == 1:  colors["R"] = 5

                    cubies.append(Cubie(np.array([x, y, z]), colors))

        return cubies

    def select(self, axis, value):
        return [c for c in self.cubies if c.pos[axis] == value]

    # -------------------------
    # ROTATION HELPERS
    # Verified by tracking face normals through rotation matrices:
    #
    # X-axis CW (viewed from +X): y->-z, z->+y
    #   Face cycle CW: U->F, F->D, D->B, B->U   (R,L stay)
    #
    # Y-axis CW (viewed from +Y): x->+z, z->-x
    #   Face cycle CW: F->R, R->B, B->L, L->F   (U,D stay)
    #
    # Z-axis CW (viewed from +Z): x->-y, y->+x
    #   Face cycle CW: R->U, U->L, L->D, D->R   (F,B stay)
    # -------------------------

    _X_COLOR_CW  = {"U": "F", "F": "D", "D": "B", "B": "U"}
    _X_COLOR_CCW = {v: k for k, v in _X_COLOR_CW.items()}

    _Y_COLOR_CW  = {"F": "R", "R": "B", "B": "L", "L": "F"}
    _Y_COLOR_CCW = {v: k for k, v in _Y_COLOR_CW.items()}

    _Z_COLOR_CW  = {"R": "U", "U": "L", "L": "D", "D": "R"}
    _Z_COLOR_CCW = {v: k for k, v in _Z_COLOR_CW.items()}

    def _rotate_colors(self, cubie, mapping):
        cubie.colors = {mapping.get(face, face): val for face, val in cubie.colors.items()}

    def rot_x(self, cubie, dir=1):
        x, y, z = cubie.pos
        if dir == 1:
            cubie.pos = np.array([x, -z, y])
            self._rotate_colors(cubie, self._X_COLOR_CW)
        else:
            cubie.pos = np.array([x, z, -y])
            self._rotate_colors(cubie, self._X_COLOR_CCW)

    def rot_y(self, cubie, dir=1):
        x, y, z = cubie.pos
        if dir == 1:
            cubie.pos = np.array([z, y, -x])
            self._rotate_colors(cubie, self._Y_COLOR_CW)
        else:
            cubie.pos = np.array([-z, y, x])
            self._rotate_colors(cubie, self._Y_COLOR_CCW)

    def rot_z(self, cubie, dir=1):
        x, y, z = cubie.pos
        if dir == 1:
            cubie.pos = np.array([-y, x, z])
            self._rotate_colors(cubie, self._Z_COLOR_CW)
        else:
            cubie.pos = np.array([y, -x, z])
            self._rotate_colors(cubie, self._Z_COLOR_CCW)

    def U(self, dir=1):
        for c in self.select(Y, 1):
            self.rot_y(c, dir)

    def D(self, dir=1):
        for c in self.select(Y, -1):
            self.rot_y(c, -dir)

    def F(self, dir=1):
        for c in self.select(Z, 1):
            self.rot_z(c, dir)

    def B(self, dir=1):
        for c in self.select(Z, -1):
            self.rot_z(c, -dir)

    def L(self, dir=1):
        for c in self.select(X, -1):
            self.rot_x(c, -dir)

    def R(self, dir=1):
        for c in self.select(X, 1):
            self.rot_x(c, dir)

    def apply_action(self, action: int):
        moves = [
            lambda: self.U(1),
            lambda: self.U(-1),
            lambda: self.D(1),
            lambda: self.D(-1),
            lambda: self.F(1),
            lambda: self.F(-1),
            lambda: self.B(1),
            lambda: self.B(-1),
            lambda: self.L(1),
            lambda: self.L(-1),
            lambda: self.R(1),
            lambda: self.R(-1),
        ]
        if not (0 <= action <= 11):
            raise ValueError("action must be 0–11")
        self._move_count += 1
        moves[action]()

    def export(self):
        return [
            {
                "x": int(c.pos[0]),
                "y": int(c.pos[1]),
                "z": int(c.pos[2]),
                "colors": c.colors
            }
            for c in self.cubies
        ]

    def export_as_kociemba_string(self):
        """
        Translates the 26-piece 3D cubie structure into a 54-character Kociemba string.
        Expected order of faces: Up -> Right -> Front -> Down -> Left -> Back.
        Each face grid is collected from top-left to bottom-right relative to standard tracking viewpoints.
        """
        cubies = self.export()

        color_map = {0: 'U', 1: 'F', 2: 'D', 3: 'L', 4: 'B', 5: 'R'}

        face_definitions = {
            'U': {
                'filter_lambda': lambda c: c['y'] == 1,
                'sort_key': lambda c: (c['z'], c['x'])
            },
            'R': {
                'filter_lambda': lambda c: c['x'] == 1,
                'sort_key': lambda c: (-c['y'], -c['z'])
            },
            'F': {
                'filter_lambda': lambda c: c['z'] == 1,
                'sort_key': lambda c: (-c['y'], c['x'])
            },
            'D': {
                'filter_lambda': lambda c: c['y'] == -1,
                'sort_key': lambda c: (-c['z'], c['x'])
            },
            'L': {
                'filter_lambda': lambda c: c['x'] == -1,
                'sort_key': lambda c: (-c['y'], c['z'])
            },
            'B': {
                'filter_lambda': lambda c: c['z'] == -1,
                'sort_key': lambda c: (-c['y'], -c['x'])
            }
        }
        
        kociemba_string = ""

        for face_name in ['U', 'R', 'F', 'D', 'L', 'B']:
            face_config = face_definitions[face_name]

            face_cubies = [c for c in cubies if face_config['filter_lambda'](c)]

            face_cubies.sort(key=face_config['sort_key'])

            for cubie in face_cubies:
                color_int = cubie['colors'][face_name]
                kociemba_string += color_map[color_int]
        return kociemba_string
    
    def is_solved(self):
        return self.export_as_kociemba_string() == "UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB"
    
    def status(self):
            return {
                "solved": self.is_solved(),
                "real_moves_count": self._move_count,
                "solve_time": datetime.now(timezone.utc).isoformat(),
                "start_time": self._start_solve,
                "is_competing": self._competing
            }

    def is_competing(self):
        return self._competing and self._start_solve != None