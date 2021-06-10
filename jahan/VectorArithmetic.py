import math


class Vector2D:

    def __init__(self, x, y):
        self.X: float = x
        self.Y: float = y

    def __key(self):
        return self.X, self.Y

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
        if isinstance(other, Vector2D):
            return Vector2D(self.X + other.X, self.Y + other.Y)

    def __sub__(self, other):
        return Vector2D(self.X - other.X, self.Y - other.Y)

    def __mul__(self, other):
        if isinstance(other, Vector2D):
            return Vector2D(self.X * other.X, self.Y * other.Y)
        else:
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
        return Vector2D(self.X * (1 / self.length), self.Y * (1 / self.length))

    @property
    def asList(self):
        return [self.X, self.Y]


def Vector2D_fromList(values):
    return Vector2D(values[0], values[1])


# ======================================================================================================================

class Segment2D:
    start: Vector2D
    end: Vector2D

    def __init__(self, a: Vector2D, b: Vector2D):
        self.start = a
        self.end = b

    def __key(self):
        return self.start, self.end

    def __eq__(self, other):
        if isinstance(other, Segment2D):
            return (self.start == other.start and self.end == other.end) or \
                   (self.start == other.end and self.end == other.start)
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
    def normal(self) -> Vector2D:
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

    def getDistanceToPoint(self, v: Vector2D, distanceFunction) -> float:
        p = self.getProjectedPoint(v)
        if self.isPointOn(p):
            return distanceFunction(v, p)
        else:
            return min(distanceFunction(v, self.start), distanceFunction(v, self.end))

    def continues(self, other) -> bool:
        return self.start == other.end

    def meets(self, other) -> bool:
        return self.end == other.end

    def reverse(self):
        self.start, self.end = self.end, self.start

    def doesIntersect(self, other):
        self_min_x = min(self.start.X, self.end.X)
        self_max_x = max(self.start.X, self.end.X)
        self_min_y = min(self.start.Y, self.end.Y)
        self_max_y = max(self.start.Y, self.end.Y)

        other_min_x = min(other.start.X, other.end.X)
        other_max_x = max(other.start.X, other.end.X)
        other_min_y = min(other.start.Y, other.end.Y)
        other_max_y = max(other.start.Y, other.end.Y)

        x_check = other_min_x < self_max_x < other_max_x or \
                  self_min_x < other_max_x < self_max_x

        y_check = other_min_y < self_max_y < other_max_y or \
                  self_min_y < other_max_y < self_max_y

        return x_check and y_check

    @property
    def asList(self):
        return [self.start.asList, self.end.asList]


def Segment2D_fromLists(a: list, b: list):
    start = Vector2D_fromList(a)
    end = Vector2D_fromList(b)
    return Segment2D(start, end)

# ======================================================================================================================
