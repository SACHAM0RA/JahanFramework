from typing import Dict
from jahan.AreaClasses import *
from random import random, uniform
from jahan.MapClasses import *
from jahan.VectorArithmetic import Canvas2D, Vector2D
import multiprocessing


def manhattanDistance(a: Vector2D, b: Vector2D) -> float:
    d = a - b
    return math.fabs(d.X) + math.fabs(d.Y)


def euclideanDistance(a: Vector2D, b: Vector2D) -> float:
    return (a - b).length


def infNormDistance(a: Vector2D, b: Vector2D) -> float:
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
        pos = nx.spring_layout(G, pos=pos, iterations=Iteration)

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
                                   distanceFunction: FunctionType) -> (Dict[str, AreaPartition], AreaPartition):
    partitions: Dict[str, AreaPartition] = {}
    emptyPartition: AreaPartition = AreaPartition("EMPTY")
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
        else:
            emptyPartition.addCell(seed, canvas.getPolygonOfSeed(seed))

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
                emptyPartition.addCell(seed, canvas.getPolygonOfSeed(seed))

    return postProcessedPartitions, emptyPartition


# ==== generateInfluenceMapFromAreaPartitions ==========================================================================

def findContainingAreaForPixel(pixelIndex: int, w: int, h: int, parts):
    container = "EMPTY"
    p = Vector2D(pixelIndex / w, pixelIndex % h)
    for areaName in parts.keys():
        if parts[areaName].containsPoint(p):
            container = areaName
            break
    return container


class callableFindContainingAreaForPixel(object):
    def __init__(self, w: int, h: int, parts):
        self.w = w
        self.h = h
        self.parts = parts

    def __call__(self, index):
        return findContainingAreaForPixel(index, self.w, self.h, self.parts)


# ===========================================
# Climate from climate assignments to areas
# ===========================================

def calculateClimateScoreForPixelFromAssignments(pixelIndex: int,
                                                 climateName: string,
                                                 w: int,
                                                 h: int,
                                                 partitions: dict,
                                                 areaOfPixels: list,
                                                 climates: dict,
                                                 climateAssignments: dict):
    areaOfPixel = areaOfPixels[pixelIndex]
    pixel = Vector2D(pixelIndex / w, pixelIndex % h)
    fadeRadius = climates[climateName].influenceFadeRadius * min(w, h)

    if areaOfPixel in partitions.keys():
        if climateAssignments[areaOfPixel] == climateName:
            return 1.0
        else:
            closestDist = math.inf
            for areaName in partitions.keys():
                dist = partitions[areaName].findDistanceToPoint(pixel)
                if climateAssignments[areaName] == climateName and dist < closestDist:
                    closestDist = dist
            return 1.0 - min(closestDist, fadeRadius) / fadeRadius
    else:
        return 0


class callableCalculateClimateScoreForPixelFromAssignments(object):
    def __init__(self,
                 climateName: string,
                 w: int, h: int,
                 parts, areaOfPixels,
                 climates: dict,
                 climateAssignments: Dict):
        self.climateName = climateName
        self.w = w
        self.h = h
        self.parts = parts
        self.areaOfPixels = areaOfPixels
        self.climates = climates
        self.climateAssignments = climateAssignments

    def __call__(self, index):
        return calculateClimateScoreForPixelFromAssignments(index,
                                                            self.climateName,
                                                            self.w, self.h,
                                                            self.parts,
                                                            self.areaOfPixels,
                                                            self.climates,
                                                            self.climateAssignments)


def generateClimateInfluenceMapsFromAreaPartitions(mapWidth: int,
                                                   mapHeight: int,
                                                   partitions: dict,
                                                   climates: dict,
                                                   climateAssignments: dict) -> Dict:
    # scaling partitions to fit the map size
    maps: Dict[string, GridMap] = {}
    scaledPartitions = copy.deepcopy(partitions)
    for area in scaledPartitions.keys():
        scaledPartitions[area].scalePartition(mapWidth, mapHeight)

    # finding area of each pixel
    pool = multiprocessing.Pool(processes=4)
    areaOfPixels = list(pool.map(callableFindContainingAreaForPixel(mapWidth, mapHeight, scaledPartitions),
                                 range(mapWidth * mapHeight)))

    climateNames = list(climates.keys())
    for climateName in climateNames:
        influence = list(pool.map(callableCalculateClimateScoreForPixelFromAssignments(climateName,
                                                                                       mapWidth,
                                                                                       mapHeight,
                                                                                       scaledPartitions,
                                                                                       areaOfPixels,
                                                                                       climates,
                                                                                       climateAssignments),
                                  range(mapWidth * mapHeight)))
        maps[climateName] = GridMap(mapWidth, mapHeight)
        maps[climateName].importValues(influence)

    for col, row in itertools.product(range(mapWidth), range(mapHeight)):
        infSum = 0.0
        for climateName in climates.keys():
            inf = maps[climateName].getValue(row, col)
            infSum = infSum + inf

        if infSum != 0.0:
            for climateName in climates.keys():
                rawInf = maps[climateName].getValue(row, col)
                maps[climateName].setValue(row, col, rawInf / infSum)

    return maps


# ===========================================
# Surface and Vegetation
# ===========================================

def calcSurfaceTotalInfluence(surface: string, row: int, col: int, climateMaps: dict, climates: dict):
    totalInfluence = 0.0
    for climateName in climateMaps.keys():
        if climates[climateName].surfaceType == surface:
            inf = climateMaps[climateName].getValue(row, col)
            totalInfluence = totalInfluence + inf

    return totalInfluence


def generateSurfaceMaps(climateMaps: Dict, climates: Dict) -> dict:
    maps: dict = {}
    w = (list(climateMaps.values()))[0].width
    h = (list(climateMaps.values()))[0].height

    surfaces = [c.surfaceType for c in climates.values()]

    for surface in surfaces:
        m = [calcSurfaceTotalInfluence(surface, row, col, climateMaps, climates) for row, col in
             itertools.product(range(h), range(w))]
        maps[surface] = GridMap(w, h)
        maps[surface].importValues(m)

    return maps


def calcVegetationProbability(row: int, col: int, climateMaps: Dict, climates: Dict):
    probability = 0.0
    for climateName in climateMaps.keys():
        inf = climateMaps[climateName].getValue(row, col)
        probability = probability + climates[climateName].vegetationProbability * inf

    return probability


def generateVegetationProbabilityMap(climateMaps: Dict, climates: Dict) -> GridMap:
    w = (list(climateMaps.values()))[0].width
    h = (list(climateMaps.values()))[0].height
    probabilities = [calcVegetationProbability(row, col, climateMaps, climates) for row, col in
                     itertools.product(range(h), range(w))]
    finalMap = GridMap(w, h)
    finalMap.importValues(probabilities)
    return finalMap


def calcVegetationTypeWeight(vegType: string, row: int, col: int, climateMaps: Dict, climates: Dict):
    totalWeight = 0.0
    for climateName in climateMaps.keys():
        inf = climateMaps[climateName].getValue(row, col)
        totalWeight = totalWeight + climates[climateName].getVegetationWeight(vegType) * inf

    return totalWeight


def generateVegetationTypeMaps(climateMaps: Dict, climates: Dict) -> dict:
    maps: dict = {}
    w = (list(climateMaps.values()))[0].width
    h = (list(climateMaps.values()))[0].height

    vegTypes: set = set()
    for climateName in climates.keys():
        for vegType in climates[climateName].vegetationTypes.keys():
            vegTypes.add(vegType)

    for vegType in vegTypes:
        m = [calcVegetationTypeWeight(vegType, row, col, climateMaps, climates) for row, col in
             itertools.product(range(h), range(w))]
        maps[vegType] = GridMap(w, h)
        maps[vegType].importValues(m)

    return normalizeMaps(maps)


def assignVegetation(row: int, col: int, vegTypeMaps: dict, vegetationProbability: GridMap):
    chance = vegetationProbability.getValue(row, col)
    r = random()
    if r < chance:
        typeRand = random()
        for vegType in vegTypeMaps.keys():
            typeChance = vegTypeMaps[vegType].getValue(row, col)
            if typeRand < typeChance:
                return row, col, vegType
            else:
                typeRand = typeRand - typeChance
    else:
        return row, col, None


def generateVegetationLocations(vegTypeMaps: dict, vegetationProbability: GridMap) -> dict:
    w = (list(vegTypeMaps.values()))[0].width
    h = (list(vegTypeMaps.values()))[0].height

    locations: dict = {}
    assignments = [assignVegetation(row, col, vegTypeMaps, vegetationProbability) for row, col in
                   itertools.product(range(h), range(w))]

    for vegType in vegTypeMaps.keys():
        locations[vegType] = [[assign[0], assign[1]] for assign in assignments if assign[2] == vegType]
    return locations
