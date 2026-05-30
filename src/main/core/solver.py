from magiccube import Cube, BasicSolver

cube = Cube(3)

scramble = "R U R' U' F2 D L2"
cube.rotate(scramble)

print("Scramble:", scramble)

solver = BasicSolver(cube)
print("Moves:")
print(solver.solve())
