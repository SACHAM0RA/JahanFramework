import math
from typing import Dict
from jahan.AreaClasses import *
from random import random

from jahan.VectorArithmetic import Canvas2D, Vector2D


def manhattanDistance(a: Vector2D, b: Vector2D) -> float:
    d = a - b
    return math.fabs(d.X) + math.fabs(d.Y)


def euclideanDistance(a: Vector2D, b: Vector2D) -> float:
    return (a - b).length


def infinityNormDistance(a: Vector2D, b: Vector2D) -> float:
    d = a - b
    return max(math.fabs(d.X), math.fabs(d.Y))


def squareGridCanvasGenerator(width: int, height: int) -> Canvas2D:
    points = []
    dx: float = 1 / width
    dy: float = 1 / height

    for i in range(width):
        for j in range(height):
            p = Vector2D(dx * (i + 0.5), dy * (j + 0.5))
            points.append(p)

    return Canvas2D(points)


def randomCanvasGenerator(pointNumber: int) -> Canvas2D:
    points = []
    for i in range(pointNumber):
        x = random()
        y = random()
        points.append(Vector2D(x, y))

    return Canvas2D(points)


def defaultPlanarEmbedding(layout: AreaLayout, padding: float) -> Dict:
    import networkx as nx
    G = layout.networkxGraph

    if not nx.check_planarity(G):
        raise Exception("Given 'layout' is not planar.")
    else:
        pos = nx.planar_layout(G)
        points = list(pos.values())
        max_X = max(map(lambda p: p[0], points)) + padding
        max_Y = max(map(lambda p: p[1], points)) + padding
        min_X = min(map(lambda p: p[0], points)) - padding
        min_Y = min(map(lambda p: p[1], points)) - padding

        positions: Dict[string, Vector2D] = {}
        for area in layout.areas:
            p = Vector2D(pos[area][0], pos[area][1])
            p.X = (p.X - min_X) / (max_X - min_X)
            p.Y = (p.Y - min_Y) / (max_Y - min_Y)
            positions[area] = p
        return positions


def generateAreaSkeletonsFromHalfEdges(layout: AreaLayout, embedding) -> List[AreaSkeleton]:
    skeletons: List[AreaSkeleton] = []
    for area in layout.areas:
        segments: List[Segment2D] = []
        for neighbour in layout.getNeighbours(area):
            a = embedding[area]
            b = (embedding[area] + embedding[neighbour]) * 0.5
            segments.append(Segment2D(a, b))
        skeletons.append(AreaSkeleton(area, embedding[area], segments))
    return skeletons


def partitionCanvasByAreaSkeletons(canvas: Canvas2D,
                                   skeletons: List[AreaSkeleton],
                                   distanceFunction: FunctionType) -> Dict[str, AreaPartition]:
    partitions: Dict[str, AreaPartition] = {}
    for s in skeletons:
        partitions[s.areaName] = AreaPartition(s.areaName)

    points = canvas.points
    for p in points:
        distances = list(map(lambda skeleton: skeleton.findDistanceToPoint(p, distanceFunction), skeletons))
        skeleton_index = distances.index(min(distances))
        areaName = skeletons[skeleton_index].areaName
        partitions[areaName].addPoint(p)

    return partitions
