import math
from types import FunctionType


class Vector2D:
    X: float = 0
    Y: float = 0

    def __init__(self, x, y):
        self.X = x
        self.Y = y

    def __str__(self):
        return "[{X},{Y}]".format(X=self.X, Y=self.Y)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if other.isinstance(Vector2D):
            return self.X == other.X and self.Y == other.Y
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.X) + hash(self.Y)

    def __copy__(self):
        return Vector2D(self.X, self.Y)

    def __deepcopy__(self):
        return self.__copy__()

    def __add__(self, other):
        return Vector2D(self.X + other.X, self.Y + other.Y)

    def __sub__(self, other):
        return Vector2D(self.X - other.X, self.Y - other.Y)

    def __mul__(self, other):
        return Vector2D(self.X * other, self.Y * other)

    def dot(self, other) -> float:
        return self.X * other.X + self.Y * other.Y

    @property
    def lengthSquared(self):
        return self.X * self.X + self.Y * self.Y

    @property
    def length(self):
        return math.sqrt(self.lengthSquared)

    @property
    def normal(self):
        return self * (1 / self.length)


# =======================================================================================================================

class Grid2D:
    points: list = []

    def __init__(self, pointList):
        self.points = pointList

    def findNearestPoint(self, v: Vector2D, distanceFunction: FunctionType) -> Vector2D:
        distances = list(map(distanceFunction, [v] * self.size, self.points))
        min_index = distances.index(min(distances))
        return self.points[min_index]

    @property
    def isEmpty(self) -> bool:
        return len(self.points) == 0

    @property
    def size(self) -> int:
        return len(self.points)
