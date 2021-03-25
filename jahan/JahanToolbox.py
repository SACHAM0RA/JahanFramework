import math
from typing import Dict
from jahan.AreaClasses import *
from random import random, uniform

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


def looseSquareGridCanvasGenerator(width: int, height: int, loosness: float = 0.5) -> Canvas2D:
    points = []
    dx: float = 1 / width
    dy: float = 1 / height

    for i in range(width):
        for j in range(height):
            p = Vector2D(dx * (i + 0.5) + dx * uniform(-1 * loosness, loosness),
                         dy * (j + 0.5) + dy * uniform(-1 * loosness, loosness))
            points.append(p)

    return Canvas2D(points)


def hexagonGridCanvasGenerator(width: int, height: int) -> Canvas2D:
    points = []
    dx: float = 1 / width
    dy: float = 1 / height

    for i in range(width + 1):
        for j in range(height):
            offset = (j % 2) * 0.5
            p = Vector2D(dx * (i + offset), dy * (j + 0.5))
            points.append(p)

    return Canvas2D(points)


def circularCanvasGenerator(deltaR: float = 0.5, ringLength: int = 100) -> Canvas2D:
    points = []
    radius = deltaR
    radIndex = 0
    while radius <= math.sqrt(2) / 2:
        L = int(ringLength * radius)
        deltaA = 2 * math.pi / L
        for i in range(L):
            angel = i * deltaA
            x = radius * math.cos(angel) + 0.5
            y = radius * math.sin(angel) + 0.5
            points.append(Vector2D(x, y))
        radius = radius + deltaR
        radIndex = radIndex + 1
    return Canvas2D(points)


def randomCanvasGenerator(seedNumber: int) -> Canvas2D:
    points = []
    for i in range(seedNumber):
        x = random()
        y = random()
        points.append(Vector2D(x, y))

    return Canvas2D(points)


def defaultPlanarEmbedding(layout: AreaLayout,
                           padding: float = 0.1,
                           Iteration: int = 10000) -> Dict:
    import networkx as nx
    G = layout.networkxGraph

    if not nx.check_planarity(G):
        raise Exception("Given 'layout' is not planar.")
    else:
        pos = nx.planar_layout(G, scale=len(layout) * 3)
        pos = nx.spring_layout(G,pos=pos,iterations=Iteration)

        embedding: Dict[string, Vector2D] = {}
        for area in layout.areas:
            embedding[area] = Vector2D_fromList(pos[area])

        points = list(embedding.values())
        max_X = max(map(lambda p: p.X, points))
        max_Y = max(map(lambda p: p.Y, points))
        min_X = min(map(lambda p: p.X, points))
        min_Y = min(map(lambda p: p.Y, points))

        positions: Dict[string, Vector2D] = {}
        for area in layout.areas:
            p = embedding[area]
            p.X = (p.X - min_X) / (max_X - min_X)
            p.X = padding + p.X * (1 - 2 * padding)
            p.Y = (p.Y - min_Y) / (max_Y - min_Y)
            p.Y = padding + p.Y * (1 - 2 * padding)
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
                                   layout: AreaLayout,
                                   skeletons: List[AreaSkeleton],
                                   distanceFunction: FunctionType) -> Dict[str, AreaPartition]:
    partitions: Dict[str, AreaPartition] = {}
    for s in skeletons:
        partitions[s.areaName] = AreaPartition(s.areaName)

    seeds = canvas.Seeds
    for seed in seeds:
        distances = list(map(lambda skeleton: skeleton.findDistanceToPoint(seed, distanceFunction), skeletons))
        minDist = min(distances)
        if minDist < seed.X and minDist < seed.Y and minDist < 1 - seed.X and minDist < 1 - seed.Y:
            skeleton_index = distances.index(minDist)
            areaName = skeletons[skeleton_index].areaName
            partitions[areaName].addCell(seed, canvas.getPolygonOfSeed(seed))

    def isSeedInOtherPartitions(seedToCheck: Vector2D, areasToIgnore: list):
        for a in partitions.keys():
            if (not (a in areasToIgnore)) and (seedToCheck in partitions[a].seeds):
                return True
        return False

    postProcessedPartitions = partitions.copy()
    for area in partitions.keys():
        for seed in partitions[area].seeds:
            badCell = False
            neighbours = canvas.getNeighboursOfSeed(seed)
            for n in neighbours:
                ignoreList = layout.getNeighbours(area)
                ignoreList.append(area)
                if isSeedInOtherPartitions(n, ignoreList):
                    badCell = True

            if badCell:
                postProcessedPartitions[area].removeCell(seed)

    return postProcessedPartitions
