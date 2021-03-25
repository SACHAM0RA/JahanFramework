import itertools
import math
from collections import defaultdict
from types import FunctionType
from scipy.spatial import Delaunay, Voronoi, voronoi_plot_2d
import numpy as np


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
        return (self.start, self.end)

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


def Segment2D_fromLists(a: list, b: list):
    start = Vector2D_fromList(a)
    end = Vector2D_fromList(b)
    return Segment2D(start, end)


# ======================================================================================================================

def voronoi_finite_polygons_2d(vor, radius=None):
    """
    Reconstruct infinite voronoi regions in a 2D diagram to finite
    regions.

    Parameters
    ----------
    vor : Voronoi
        Input diagram
    radius : float, optional
        Distance to 'points at infinity'.

    Returns
    -------
    regions : list of tuples
        Indices of vertices in each revised Voronoi regions.
    vertices : list of tuples
        Coordinates for revised Voronoi vertices. Same as coordinates
        of input vertices, with 'points at infinity' appended to the
        end.

    """

    if vor.points.shape[1] != 2:
        raise ValueError("Requires 2D input")

    new_regions = []
    new_vertices = vor.vertices.tolist()

    center = vor.points.mean(axis=0)
    if radius is None:
        radius = vor.points.ptp().max()

    # Construct a map containing all ridges for a given point
    all_ridges = {}
    for (p1, p2), (v1, v2) in zip(vor.ridge_points, vor.ridge_vertices):
        all_ridges.setdefault(p1, []).append((p2, v1, v2))
        all_ridges.setdefault(p2, []).append((p1, v1, v2))

    # Reconstruct infinite regions
    for p1, region in enumerate(vor.point_region):
        vertices = vor.regions[region]

        if all(v >= 0 for v in vertices):
            # finite region
            new_regions.append(vertices)
            continue

        # reconstruct a non-finite region
        ridges = all_ridges[p1]
        new_region = [v for v in vertices if v >= 0]

        for p2, v1, v2 in ridges:
            if v2 < 0:
                v1, v2 = v2, v1
            if v1 >= 0:
                # finite ridge: already in the region
                continue

            # Compute the missing endpoint of an infinite ridge

            t = vor.points[p2] - vor.points[p1]  # tangent
            t /= np.linalg.norm(t)
            n = np.array([-t[1], t[0]])  # normal

            midpoint = vor.points[[p1, p2]].mean(axis=0)
            direction = np.sign(np.dot(midpoint - center, n)) * n
            far_point = vor.vertices[v2] + direction * radius

            new_region.append(len(new_vertices))
            new_vertices.append(far_point.tolist())

        # sort region counterclockwise
        vs = np.asarray([new_vertices[v] for v in new_region])
        c = vs.mean(axis=0)
        angles = np.arctan2(vs[:, 1] - c[1], vs[:, 0] - c[0])
        new_region = np.array(new_region)[np.argsort(angles)]

        # finish
        new_regions.append(new_region.tolist())

    return new_regions, np.asarray(new_vertices)


class Canvas2D:
    __seeds: list = []
    __neighbours: dict = {}
    __voronoi_vertices = None
    __voronoi_regions = None

    def __init__(self, pointList):
        self.__seeds = pointList

        pointsAsList = list(map(lambda p: p.asList, self.__seeds))

        self.__neighbours = defaultdict(set)
        tri = Delaunay(pointsAsList, qhull_options="Qw Qt Qj")
        for p in tri.vertices:
            for i, j in itertools.combinations(p, 2):
                self.__neighbours[i].add(j)
                self.__neighbours[j].add(i)

        regions, vertices = voronoi_finite_polygons_2d(Voronoi(pointsAsList))
        self.__voronoi_regions = regions
        self.__voronoi_vertices = vertices

    def __len__(self):
        return len(self.__seeds)

    def findNearestPoint(self, v: Vector2D, distanceFunction: FunctionType) -> Vector2D:
        distances = list(map(distanceFunction, [v] * self.size, self.__seeds))
        min_index = distances.index(min(distances))
        return self.__seeds[min_index]

    @property
    def isEmpty(self) -> bool:
        return len(self.__seeds) == 0

    @property
    def size(self) -> int:
        return len(self)

    @property
    def Seeds(self):
        return self.__seeds.copy()

    @property
    def pointsAsList(self):
        return list(map(lambda p: p.asList, self.__seeds))

    @property
    def voronoiPolygons(self) -> list:
        polygons = []
        for region in self.__voronoi_regions:
            polygon = self.__voronoi_vertices[region]
            convertedPoly = list(map(lambda p: Vector2D_fromList(p), polygon))
            polygons.append(convertedPoly)
        return polygons

    @property
    def voronoiSegments(self) -> list:
        segments = []

        polygons = self.voronoiPolygons
        for poly in polygons:
            polyLength = len(poly)
            for i in range(polyLength + 1):
                segment = Segment2D(poly[i % polyLength],
                                    poly[(i + 1) % polyLength])
                segments.append(segment)
        return segments

    def getPolygonOfSeed(self, seed: Vector2D) -> list:
        index = self.__seeds.index(seed)
        return self.voronoiPolygons[index]

    def getNeighboursOfSeed(self, v: Vector2D) -> list:
        index = self.__seeds.index(v)
        ret_indices = self.__neighbours[index]
        return list(map(lambda i: self.__seeds[i], ret_indices))

    def getNeighboursOfSeedIndex(self, seedIndex) -> list:
        return list(self.__neighbours[seedIndex])
