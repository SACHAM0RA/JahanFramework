from jahan.AreaClasses import *
from jahan.MapClasses import *
from jahan.Noise2D import *
from jahan.VectorArithmetic import Canvas2D, Vector2D
from typing import Dict
import multiprocessing


# ===========================================
# Setting Random Seed
# ===========================================


# ===========================================
# General Stuff
# ===========================================

def easeInOutQuart(x: float):
    if x < 0.5:
        return 8 * x * x * x * x
    else:
        return 1 - ((-2 * x + 2) ** 4) / 2


class calcPartitionInfluenceOnPixel(object):
    def __init__(self, areaName: string, w: int, h: int, partition, areaOfPixels, fadeRadius: float = 0.075):
        self.areaName = areaName
        self.w = w
        self.h = h
        self.partition = partition
        self.areaOfPixels = areaOfPixels
        self.fadeRadius = fadeRadius

    def __call__(self, pixelIndex):
        areaOfPixel = self.areaOfPixels[pixelIndex]
        pixel = Vector2D(pixelIndex / self.w, pixelIndex % self.h)
        fadeRadius = self.fadeRadius * min(self.w, self.h)

        if areaOfPixel == "EMPTY":
            return 0.0
        dist = self.partition.findDistanceToPoint(pixel)
        if areaOfPixel == self.areaName:
            blendValue = 0.5 + 0.5 * min(dist, fadeRadius) / fadeRadius
        else:
            blendValue = 0.5 - 0.5 * min(dist, fadeRadius) / fadeRadius

        return easeInOutQuart(blendValue)


def generateAreaInfluenceMapFromPartitions(partitions: dict, fadeRadius: dict, mapWidth: int, mapHeight: int) -> dict:
    maps: Dict[string, GridMap] = {}
    areaNames = list(partitions.keys())

    pool = multiprocessing.Pool(processes=4)
    areaOfPixels = list(
        pool.map(findContainingAreaForPixel(mapWidth, mapHeight, partitions), range(mapWidth * mapHeight)))

    for areaName in areaNames:
        influence = list(pool.map(calcPartitionInfluenceOnPixel(areaName,
                                                                mapWidth,
                                                                mapHeight,
                                                                partitions[areaName],
                                                                areaOfPixels,
                                                                fadeRadius[areaName]),
                                  range(mapWidth * mapHeight)))
        maps[areaName] = GridMap(mapWidth, mapHeight)
        maps[areaName].importValues(influence)

    maps = normalizeGridMaps(maps)
    return maps


# ===========================================
# Distance Calculator
# ===========================================

class DistanceCalculator:
    def __call__(self, *args, **kwargs) -> float:
        return 0.0


class ManhattanDistanceCalculator(DistanceCalculator):
    def __call__(self, *args, **kwargs):
        a = args[0]
        b = args[1]
        d = a - b
        return math.fabs(d.X) + math.fabs(d.Y)


class EuclideanDistanceCalculator(DistanceCalculator):
    def __call__(self, *args, **kwargs):
        a = args[0]
        b = args[1]
        return (a - b).length


class InfiniteNormDistanceCalculator(DistanceCalculator):
    def __call__(self, *args, **kwargs):
        a = args[0]
        b = args[1]
        d = a - b
        return max(math.fabs(d.X), math.fabs(d.Y))


# ===========================================
# Canvas generation
# ===========================================

class CanvasGenerator:
    def generate(self) -> Canvas2D:
        return Canvas2D([])


class SquareGridCanvasGenerator(CanvasGenerator):
    def __init__(self, width: int, height: int):
        self.__w = width
        self.__h = height

    def generate(self) -> Canvas2D:
        points = []
        dx: float = 1 / self.__w
        dy: float = 1 / self.__h

        for i in range(self.__w):
            for j in range(self.__h):
                p = Vector2D(dx * (i + 0.5), dy * (j + 0.5))
                points.append(p)

        return Canvas2D(points)


class LooseSquareGridCanvasGenerator(CanvasGenerator):
    def __init__(self, width: int, height: int, looseness: float = 0.5):
        self.__w = width
        self.__h = height
        self.__looseness = looseness

    def generate(self) -> Canvas2D:
        points = []
        dx: float = 1 / self.__w
        dy: float = 1 / self.__h

        for i in range(self.__w):
            for j in range(self.__h):
                p = Vector2D(dx * (i + 0.5) + dx * uniform(-1 * self.__looseness, self.__looseness),
                             dy * (j + 0.5) + dy * uniform(-1 * self.__looseness, self.__looseness))
                points.append(p)

        return Canvas2D(points)


class HexagonGridCanvasGenerator(CanvasGenerator):
    def __init__(self, width: int, height: int):
        self.__w = width
        self.__h = height

    def generate(self) -> Canvas2D:
        points = []
        dx: float = 1 / self.__w
        dy: float = 1 / self.__h

        for i in range(self.__w + 1):
            for j in range(self.__h):
                offset = (j % 2) * 0.5
                p = Vector2D(dx * (i + offset), dy * (j + 0.5))
                points.append(p)

        return Canvas2D(points)


class CircularCanvasGenerator(CanvasGenerator):
    def __init__(self, deltaRadius: float = 0.5, ringLength: int = 100):
        self.__deltaRadius = deltaRadius
        self.__ringLength = ringLength

    def generate(self) -> Canvas2D:
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
        return Canvas2D(points)


class RandomCanvasGenerator(CanvasGenerator):
    def __init__(self, seedCount: int):
        self.__seedCount = seedCount

    def generate(self) -> Canvas2D:
        points = []
        for i in range(self.__seedCount):
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


# ===========================================
# Finding the area of a pixel
# ===========================================

class findContainingAreaForPixel(object):
    def __init__(self, w: int, h: int, partitions):
        self.w = w
        self.h = h
        self.partitions = partitions

    def __call__(self, pixelIndex):
        container = "EMPTY"
        p = Vector2D(pixelIndex / self.w, pixelIndex % self.h)
        for areaName in self.partitions.keys():
            if self.partitions[areaName].containsPoint(p):
                container = areaName
                break
        return container


# ===========================================
# Climate from climate assignments to areas
# ===========================================

class calcClimateInfluenceOnPixelFromAssignments(object):
    def __init__(self,
                 climateName: string,
                 w: int, h: int,
                 partitions,
                 areaOfPixels,
                 climates: dict,
                 climateAssignments: Dict):
        self.climateName = climateName
        self.w = w
        self.h = h
        self.partitions = partitions
        self.areaOfPixels = areaOfPixels
        self.climates = climates
        self.climateAssignments = climateAssignments

    def __call__(self, pixelIndex):
        areaOfPixel = self.areaOfPixels[pixelIndex]
        pixel = Vector2D(pixelIndex / self.w, pixelIndex % self.h)
        fadeRadius = self.climates[self.climateName].influenceFadeRadius * min(self.w, self.h)

        if areaOfPixel in self.partitions.keys():
            if self.climateAssignments[areaOfPixel] == self.climateName:
                return 1.0
            else:
                closestDist = math.inf
                for areaName in self.partitions.keys():
                    dist = self.partitions[areaName].findDistanceToPoint(pixel)
                    if self.climateAssignments[areaName] == self.climateName and dist < closestDist:
                        closestDist = dist
                return 1.0 - min(closestDist, fadeRadius) / fadeRadius
        else:
            return 0


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
    areaOfPixels = list(pool.map(findContainingAreaForPixel(mapWidth, mapHeight, scaledPartitions),
                                 range(mapWidth * mapHeight)))

    climateNames = list(climates.keys())
    for climateName in climateNames:
        influence = list(pool.map(calcClimateInfluenceOnPixelFromAssignments(climateName,
                                                                             mapWidth,
                                                                             mapHeight,
                                                                             scaledPartitions,
                                                                             areaOfPixels,
                                                                             climates,
                                                                             climateAssignments),
                                  range(mapWidth * mapHeight)))
        maps[climateName] = GridMap(mapWidth, mapHeight)
        maps[climateName].importValues(influence)

    maps = normalizeGridMaps(maps)
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

    return normalizeGridMaps(maps)


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


# ===========================================
# Height Foundation
# ===========================================

class HeightFoundation:
    def __call__(self, partition: AreaPartition, mapWidth: int, mapHeight: int) -> GridMap:
        return GridMap(mapWidth, mapHeight)


class Flat_HeightFoundation(HeightFoundation):
    def __init__(self, flatHeight: float):
        self.__H = flatHeight

    def __call__(self, partition: AreaPartition, mapWidth: int, mapHeight: int) -> GridMap:
        heightMap = GridMap(mapWidth, mapHeight)
        heightMap.importValues([self.__H] * mapWidth * mapHeight)
        return heightMap


class getSignedDistanceOfPixelToAreaPartition:
    def __init__(self, mapWidth: int, mapHeight: int, partition: AreaPartition):
        self.partition = partition
        self.w = mapWidth
        self.h = mapHeight

    def __call__(self, pixelIndex: int):
        pixel = Vector2D(pixelIndex / self.w, pixelIndex % self.h)
        absDist = self.partition.findDistanceToPoint(pixel)
        if self.partition.containsPoint(pixel):
            return -1 * absDist
        else:
            return absDist


class SDF_HeightFoundation(HeightFoundation):
    def __init__(self, ascending: bool, minHeight: float, maxHeight: float):
        self.__ascending = ascending
        self.__minH = min(minHeight, maxHeight)
        self.__maxH = max(minHeight, maxHeight)

    def __call__(self, partition: AreaPartition, mapWidth: int, mapHeight: int) -> GridMap:
        pool = multiprocessing.Pool(processes=4)
        pixelDistanceValues = list(
            pool.map(getSignedDistanceOfPixelToAreaPartition(mapWidth, mapHeight, partition),
                     range(mapWidth * mapHeight)))

        absoluteMinDist = abs(min(pixelDistanceValues))
        pixelDistanceValues = [d / absoluteMinDist for d in pixelDistanceValues]
        diffH = self.__maxH - self.__minH
        if self.__ascending:
            pixelDistanceValues = [self.__minH - diffH * d for d in pixelDistanceValues]
        else:
            pixelDistanceValues = [self.__maxH + diffH * d for d in pixelDistanceValues]

        heightMap = GridMap(mapWidth, mapHeight)
        heightMap.importValues(pixelDistanceValues)
        return heightMap


# ===========================================
# Height Noise
# ===========================================

class HeightNoiseGenerator:
    def __init__(self, amplitude: float):
        self.__a = amplitude

    @property
    def amplitude(self):
        return self.__a

    def generateNoiseMap(self, width: int, height: int) -> GridMap:
        return GridMap(width, height)


class WhiteHeightNoiseGenerator(HeightNoiseGenerator):
    def generateNoiseMap(self, width: int, height: int) -> GridMap:
        noise = whiteNoise(width, height, self.amplitude)
        m: GridMap = GridMap(width, height)
        m.importValues(noise)
        return m


class PerlinHeightNoiseGenerator(HeightNoiseGenerator):
    def __init__(self, amplitude: float, octaves=4, scale=8):
        super().__init__(amplitude)
        self.scale = scale
        self.octaves = octaves

    def generateNoiseMap(self, width: int, height: int) -> GridMap:
        noise = perlinNoise(width, height, self.amplitude, self.octaves, self.scale)
        m: GridMap = GridMap(width, height)
        m.importValues(noise)
        return m


class OpenSimplexHeightNoiseGenerator(HeightNoiseGenerator):
    def generateNoiseMap(self, width: int, height: int) -> GridMap:
        noise = openSimplexNoise(width, height, self.amplitude)
        m: GridMap = GridMap(width, height)
        m.importValues(noise)
        return m


class WorleyHeightNoiseGenerator(HeightNoiseGenerator):
    def generateNoiseMap(self, width: int, height: int) -> GridMap:
        return GridMap(width, height)


# ===========================================
# Height Profile
# ===========================================

class HeightProfile:
    def __init__(self, foundation: HeightFoundation, detail: HeightNoiseGenerator, fadeRadius: float = 0.1):
        self.__foundation: HeightFoundation = foundation
        self.__noise = detail
        self.__fadeRadius = fadeRadius

    @property
    def fadeRadius(self):
        return self.__fadeRadius

    def heightMapForPartition(self, partition, mapWidth, mapHeight):
        foundationHeight = self.__foundation(partition, mapWidth, mapHeight)
        return addGrids(foundationHeight, self.__noise.generateNoiseMap(mapWidth, mapHeight))


# ===========================================
# Height map generation
# ===========================================

def calcHeightOfPixelFromPartialHeightMaps(row: int, col: int, influenceMaps: dict, partialHeightMaps: dict) -> float:
    h = 0
    for area in partialHeightMaps.keys():
        h = h + partialHeightMaps[area].getValue(row, col) * influenceMaps[area].getValue(row, col)
    return h


def generateHeightMapFromElevationSettings(mapWidth: int, mapHeight: int, settings: dict, partitions: dict) -> GridMap:
    partialHeightMaps: dict = {}
    scaledPartitions = copy.deepcopy(partitions)
    for area in scaledPartitions.keys():
        scaledPartitions[area].scalePartition(mapWidth, mapHeight)

    for area in scaledPartitions.keys():
        partialHeightMaps[area] = settings[area].heightMapForPartition(scaledPartitions[area], mapWidth, mapHeight)

    fadeRadius = {}
    for area in settings.keys():
        fadeRadius[area] = settings[area].fadeRadius

    influenceMaps = generateAreaInfluenceMapFromPartitions(scaledPartitions, fadeRadius, mapWidth, mapHeight)

    heightValues = [calcHeightOfPixelFromPartialHeightMaps(row, col, influenceMaps, partialHeightMaps) for
                    row, col in
                    itertools.product(range(mapHeight), range(mapWidth))]

    pool = multiprocessing.Pool(processes=4)
    areaOfPixels = list(
        pool.map(findContainingAreaForPixel(mapWidth, mapHeight, scaledPartitions), range(mapWidth * mapHeight)))

    indices = [i for i, area in enumerate(areaOfPixels) if area == "EMPTY"]
    for i in indices:
        heightValues[i] = np.nan

    heightMap = GridMap(mapWidth, mapHeight)
    heightMap.importValues(heightValues)
    return heightMap
