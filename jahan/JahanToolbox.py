import math
from random import random

from jahan.VectorArithmetic import Grid2D, Vector2D


def manhattanDistance(a: Vector2D, b: Vector2D) -> float:
    d = a - b
    return math.fabs(d.X) + math.fabs(d.Y)


def euclideanDistance(a: Vector2D, b: Vector2D) -> float:
    return (a - b).length


def infinityNormDistance(a: Vector2D, b: Vector2D) -> float:
    d = a - b
    return max(math.fabs(d.X), math.fabs(d.Y))


def squareGridGenerator(width: int , height: int) -> Grid2D:
    points = []
    dx: float = 1/width
    dy: float = 1/height

    for i in range(width):
        for j in range(height):
            p = Vector2D(dx*(i + 0.5), dy*(j + 0.5))
            points.append(p)

    return Grid2D(points)


def randomGridGenerator(pointNumber: int) -> Grid2D:
    points = []
    for i in range(pointNumber):
        x = random()
        y = random()
        points.append(Vector2D(x,y))

    return Grid2D(points)
