import random as rnd
import numpy as np
import math
import itertools
from jahan.VectorArithmetic import Vector2D, Segment2D, Vector2D_fromList
from collections import defaultdict
from scipy.spatial import Delaunay, Voronoi

# ======================================================================================================================
# Canvas Data Structures
# ======================================================================================================================

rnd.seed(10)


def generateFinite2DVoronoi(vor, radius=None):
    """
    Reconstruct infinite voronoi regions in a 2D diagram to finite regions.

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
        Coordinates for revised Voronoi vertices.

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

        pointsAsList = [p.asList for p in self.__seeds]

        self.__neighbours = defaultdict(set)
        tri = Delaunay(pointsAsList, qhull_options="Qw Qt Qj")
        for p in tri.vertices:
            for i, j in itertools.combinations(p, 2):
                self.__neighbours[i].add(j)
                self.__neighbours[j].add(i)

        regions, vertices = generateFinite2DVoronoi(Voronoi(pointsAsList))
        self.__voronoi_regions = regions
        self.__voronoi_vertices = vertices

    def __len__(self):
        return len(self.__seeds)

    def findNearestPoint(self, v: Vector2D, distanceFunction) -> Vector2D:
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
        return [p.asList for p in self.__seeds]

    @property
    def voronoiPolygons(self) -> list:
        polygons = []
        for region in self.__voronoi_regions:
            polygon = self.__voronoi_vertices[region]
            convertedPoly = [Vector2D_fromList(p) for p in polygon]
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
        neighbour_indices = list(self.__neighbours[index])
        return [self.__seeds[i] for i in neighbour_indices]

    def getNeighboursOfSeedIndex(self, seedIndex) -> list:
        return list(self.__neighbours[seedIndex])


# ======================================================================================================================
# Canvas generation
# ======================================================================================================================

class CanvasSeedGenerator:
    def generate(self) -> list:
        return []


class SquareCanvasSeedGenerator(CanvasSeedGenerator):
    def __init__(self, width: int, height: int):
        self.__w = width
        self.__h = height

    def generate(self) -> list:
        points = []
        dx: float = 1 / self.__w
        dy: float = 1 / self.__h

        for i in range(self.__w):
            for j in range(self.__h):
                p = Vector2D(dx * (i + 0.5), dy * (j + 0.5))
                points.append(p)

        return points


class LooseSquareCanvasSeedGenerator(CanvasSeedGenerator):
    def __init__(self, width: int, height: int, looseness: float = 0.5):
        self.__w = width
        self.__h = height
        self.__looseness = looseness

    def generate(self) -> list:
        points = []
        dx: float = 1 / self.__w
        dy: float = 1 / self.__h

        for i in range(self.__w):
            for j in range(self.__h):
                p = Vector2D(dx * (i + 0.5) + dx * rnd.uniform(-1 * self.__looseness, self.__looseness),
                             dy * (j + 0.5) + dy * rnd.uniform(-1 * self.__looseness, self.__looseness))
                points.append(p)

        return points


class HexagonCanvasSeedGenerator(CanvasSeedGenerator):
    def __init__(self, width: int, height: int):
        self.__w = width
        self.__h = height

    def generate(self) -> list:
        points = []
        dx: float = 1 / self.__w
        dy: float = 1 / self.__h

        for i in range(self.__w + 1):
            for j in range(self.__h):
                offset = (j % 2) * 0.5
                p = Vector2D(dx * (i + offset), dy * (j + 0.5))
                points.append(p)

        return points


class RadialCanvasSeedGenerator(CanvasSeedGenerator):
    def __init__(self, deltaRadius: float = 0.5, ringLength: int = 100):
        self.__deltaRadius = deltaRadius
        self.__ringLength = ringLength

    def generate(self) -> list:
        points = []
        radius = self.__deltaRadius
        radIndex = 0
        while radius <= math.sqrt(2) / 2:
            L = int(self.__ringLength * radius)
            deltaA = 2 * math.pi / L
            for i in range(L):
                angel = i * deltaA
                x = radius * math.cos(angel) + 0.5
                y = radius * math.sin(angel) + 0.5
                points.append(Vector2D(x, y))
            radius = radius + self.__deltaRadius
            radIndex = radIndex + 1

        return points


class UniformRandomCanvasSeedGenerator(CanvasSeedGenerator):
    def __init__(self, seedCount: int):
        self.__seedCount = seedCount

    def generate(self) -> list:
        points = []
        for i in range(self.__seedCount):
            x = rnd.random()
            y = rnd.random()
            points.append(Vector2D(x, y))

        return points
