import math
from types import FunctionType


class Vector2D:
    X: float = 0
    Y: float = 0

    def __init__(self, x, y):
        self.X = x
        self.Y = y

    def __key(self):
        return (self.X, self.Y)

    def __str__(self):
        return "[{X},{Y}]".format(X=self.X, Y=self.Y)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if isinstance(other, Vector2D):
            return self.X == other.X and self.Y == other.Y
        return NotImplemented

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.__key())

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

    def perpDot(self, other) -> float:
        return self.X * other.Y - self.Y * other.X

    @property
    def lengthSquared(self):
        return self.X * self.X + self.Y * self.Y

    @property
    def length(self):
        return math.sqrt(self.lengthSquared)

    @property
    def normal(self):
        return self * (1 / self.length)


# ======================================================================================================================

class Segment2D:
    start: Vector2D
    end: Vector2D

    def __init__(self, a: Vector2D, b: Vector2D):
        self.start = a
        self.end = b

    def __key(self):
        return (self.start, self.end)

    def __eq__(self, other):
        if isinstance(other, Segment2D):
            return self.start == other.start and self.end == other.end
        else:
            return NotImplemented

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash(self.__key())

    @property
    def direction(self):
        return self.end - self.start

    @property
    def length(self):
        return self.direction.length

    @property
    def normal(self):
        return self.direction.normal

    @property
    def epsilon(self):
        epsilon = 0.001 * self.direction.lengthSquared
        return epsilon

    def isPointAligned(self, v: Vector2D):
        return math.fabs(self.direction.perpDot(v - self.start)) < self.epsilon

    def isPointOn(self, v: Vector2D):
        min_x = min(self.start.X, self.end.X)
        max_x = max(self.start.X, self.end.X)
        min_y = min(self.start.Y, self.end.Y)
        max_y = max(self.start.Y, self.end.Y)

        if min_x <= v.X <= max_x and min_y <= v.Y <= max_y:
            return self.isPointAligned(v)
        else:
            return False

    def getProjectedPoint(self, v: Vector2D) -> Vector2D:
        e = v - self.start
        return self.start + (self.normal * (self.direction.dot(e) / self.length))

    def getDistanceToPoint(self, v: Vector2D, distanceFunction: FunctionType) -> float:
        p = self.getProjectedPoint(v)
        if self.isPointOn(p):
            return distanceFunction(v, p)
        else:
            return min(distanceFunction(v, self.start), distanceFunction(v, self.end))


# ======================================================================================================================

class Canvas2D:
    points: list = []

    def __init__(self, pointList):
        self.points = pointList

    def __len__(self):
        return len(self.points)

    def findNearestPoint(self, v: Vector2D, distanceFunction: FunctionType) -> Vector2D:
        distances = list(map(distanceFunction, [v] * self.size, self.points))
        min_index = distances.index(min(distances))
        return self.points[min_index]

    @property
    def isEmpty(self) -> bool:
        return len(self.points) == 0

    @property
    def size(self) -> int:
        return len(self)
