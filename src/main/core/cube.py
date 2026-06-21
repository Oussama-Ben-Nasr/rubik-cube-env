import numpy as np
from dataclasses import dataclass, field
from datetime import datetime, timezone
import twophase.face as kc_face
import twophase.cubie as kc_cubie

X, Y, Z = 0, 1, 2


@dataclass
class Cubie:
    pos: np.ndarray
    colors: dict = field(default_factory=dict)


class RubikCube3D:
    _move_count: int = 0
    _start_solve = None
    _competing = False
    _facelet_state = ""

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

    def get_state(self) -> list[dict]:
        """Return a serialisable snapshot of all cubies."""
        return [
            {
                "pos": c.pos.tolist(),
                "colors": dict(c.colors),
            }
            for c in self.cubies
        ]
 
    def load_state(self, state: list[dict]) -> None:
        """Restore cubies from a snapshot produced by get_state()."""
        self.cubies = [
            Cubie(
                pos=np.array(entry["pos"], dtype=int),
                colors=dict(entry["colors"]),
            )
            for entry in state
        ]

    def load_facelets(self, faces):
            """
            Validates manually configured 2D face inputs and maps them into 
            the internal 3D Cubie vector coordinate simulation state space.
            """
            required_faces = ["U", "D", "F", "B", "L", "R"]
            if not all(face in faces for face in required_faces):
                return {"status": "error", "reason": "Missing configuration parameters for certain faces."}

            all_stickers = []
            for face in required_faces:
                if len(faces[face]) != 9:
                    return {"status": "error", "reason": f"Face '{face}' does not contain exactly 9 elements."}
                all_stickers.extend(faces[face])

            if len(all_stickers) != 54:
                return {"status": "error", "reason": f"Expected 54 stickers total, received {len(all_stickers)}."}

            char_to_int_map = {
                "W": 0,  # White (U)
                "G": 1,  # Green (F)
                "Y": 2,  # Yellow (D)
                "O": 3,  # Orange (L)
                "B": 4,  # Blue (B)
                "R": 5   # Red (R)
            }
            
            counts = {}
            for sticker in all_stickers:
                if sticker not in char_to_int_map:
                    return {"status": "error", "reason": f"Invalid sticker character detected: '{sticker}'"}
                counts[sticker] = counts.get(sticker, 0) + 1

            for char, count in counts.items():
                if count != 9:
                    return {
                        "status": "error", 
                        "reason": f"Color count anomaly: Found {count} '{char}' stickers instead of exactly 9."
                    }

            new_cubies = self._init_cubies()

            face_index_maps = {
                'U': [(-1, 1, -1), (0, 1, -1), (1, 1, -1),
                    (-1, 1,  0), (0, 1,  0), (1, 1,  0),
                    (-1, 1,  1), (0, 1,  1), (1, 1,  1)],
                'D': [(-1, -1, 1), (0, -1, 1), (1, -1, 1),
                    (-1, -1, 0), (0, -1, 0), (1, -1, 0),
                    (-1, -1, -1), (0, -1, -1), (1, -1, -1)],
                'F': [(-1, 1, 1), (0, 1, 1), (1, 1, 1),
                    (-1, 0, 1), (0, 0, 1), (1, 0, 1),
                    (-1, -1, 1), (0, -1, 1), (1, -1, 1)],
                'B': [(1, 1, -1), (0, 1, -1), (-1, 1, -1),
                    (1, 0, -1), (0, 0, -1), (-1, 0, -1),
                    (1, -1, -1), (0, -1, -1), (-1, -1, -1)],
                'L': [(-1, 1, -1), (-1, 1, 0), (-1, 1, 1),
                    (-1, 0, -1), (-1, 0, 0), (-1, 0, 1),
                    (-1, -1, -1), (-1, -1, 0), (-1, -1, 1)],
                'R': [(1, 1, 1), (1, 1, 0), (1, 1, -1),
                    (1, 0, 1), (1, 0, 0), (1, 0, -1),
                    (1, -1, 1), (1, -1, 0), (1, -1, -1)]
            }

            for cubie in new_cubies:
                cubie.colors = {}

            for face_name in required_faces:
                pos_list = face_index_maps[face_name]
                sticker_list = faces[face_name]

                for idx, pos_coord in enumerate(pos_list):
                    target_char = sticker_list[idx]
                    target_int_code = char_to_int_map[target_char]

                    for cubie in new_cubies:
                        if int(cubie.pos[0]) == pos_coord[0] and int(cubie.pos[1]) == pos_coord[1] and int(cubie.pos[2]) == pos_coord[2]:
                            cubie.colors[face_name] = target_int_code
                            break

            try:
                color_map = {0: 'U', 1: 'F', 2: 'D', 3: 'L', 4: 'B', 5: 'R'}

                test_cube = RubikCube3D()
                test_cube.cubies = new_cubies
                kociemba_string = test_cube.export_as_kociemba_string()
                kc_fc = kc_face.FaceCube()
                kc_s = kc_fc.from_string(kociemba_string)
                if kc_s != kc_cubie.CUBE_OK:
                    raise ValueError(kc_s)
                cc = kc_fc.to_cubie_cube()
                kc_s = cc.verify()
                if kc_s != kc_cubie.CUBE_OK:
                    raise ValueError(kc_s)
                
            except ImportError:
                print("[CUBE ENGINE] Warning: 'kociemba' library missing. Skipping deep math parity checks.")
            except ValueError as e:
                error_msg = str(e)
                if "Cannot be solved" in error_msg or "twist" in error_msg.lower() or "flip" in error_msg.lower():
                    return {
                        "status": "error", 
                        "reason": f"Mathematically Unsolvable State ({error_msg}). Check for twisted corners/flipped edges or incorrect orientation mapping."
                    }
                return {"status": "error", "reason": f"Permutation Error: {error_msg}"}

            self.cubies = new_cubies
            self._facelet_state = faces
            self.reset_moves_count()
            
            print("[CUBE ENGINE] 2D Facelets successfully mapped and written to 3D matrix.")
            return {"status": "ok"}

    def is_competing(self):
        return self._competing and self._start_solve != None