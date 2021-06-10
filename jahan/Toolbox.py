import multiprocessing

from jahan.Layout import *
from jahan.GridMap import *
from jahan.Canvas import *
from jahan.Noise2D import *
from jahan.VectorArithmetic import Vector2D

# ======================================================================================================================
# General Stuff
# ======================================================================================================================

EMPTY_PART = "EMPTY_PARTITION"

DESIRED_HEIGHT: int = 0
FADE_RADIUS: int = 1


def easeInOut(x: float):
    if x < 0.5:
        return 2 * x * x
    else:
        return 1 - ((-2 * x + 2) ** 2) / 2


def generate_2d_mesh(mapWidth, mapHeight):
    ret = list(itertools.product(range(mapWidth), range(mapHeight)))
    ret = [(x, y) for y, x in ret]
    return ret


# ======================================================================================================================
# Finding the area of a pixel
# ======================================================================================================================

class findContainingAreaForPixel(object):
    def __init__(self, partitions: dict):
        self.partitions = partitions

    def __call__(self, p):
        container = EMPTY_PART
        pixel = Vector2D(p[0], p[1])
        for areaName in self.partitions.keys():
            if areaName != EMPTY_PART and self.partitions[areaName].containsPoint(pixel):
                container = areaName
                break
        return p, container


# ======================================================================================================================
# Partition Influence
# ======================================================================================================================

class calcPartitionInfluenceOnPixel(object):
    def __init__(self, areaName: string, partitions: dict, areaOfPixels, fadeRadius: float = 0.075):
        self.areaName = areaName
        self.partition = partitions[areaName]
        self.partitions = partitions
        self.areaOfPixels = areaOfPixels
        self.fadeRadius = fadeRadius

    def __call__(self, p):
        areaOfPixel = self.areaOfPixels[p]
        pixel = Vector2D(p[0], p[1])

        if self.areaName == EMPTY_PART:
            dist = self.partition.findDistanceToClosestBorderSegment(pixel)
        else:
            dist = self.partition.findDistanceToPoint(pixel)

        if areaOfPixel == self.areaName:
            blendValue = 0.5 + 0.5 * min(dist, self.fadeRadius) / self.fadeRadius
        else:
            blendValue = 0.5 - 0.5 * min(dist, self.fadeRadius) / self.fadeRadius

        return easeInOut(blendValue)


def generateAreaInfluenceMapFromPartitions(partitions: dict, fadeRadius: float, mapWidth: int, mapHeight: int) -> dict:
    partitions = copy.deepcopy(partitions)
    for area in partitions.keys():
        partitions[area].scalePartition(mapWidth, mapHeight)

    maps: Dict[string, GridMap] = {}
    areaNames = list(partitions.keys())

    pixelList = generate_2d_mesh(mapWidth, mapHeight)

    pool = multiprocessing.Pool(processes=4)
    findContainingAreaForPixel_callable = findContainingAreaForPixel(partitions)
    areaOfPixels = dict(pool.map(findContainingAreaForPixel_callable, pixelList))

    for areaName in areaNames:
        calcInfluenceOnPixel_callable = calcPartitionInfluenceOnPixel(areaName,
                                                                      partitions,
                                                                      areaOfPixels,
                                                                      fadeRadius * min(mapWidth, mapHeight))

        influence = list(pool.map(calcInfluenceOnPixel_callable, pixelList))

        maps[areaName] = GridMap(mapWidth, mapHeight)
        maps[areaName].importValues(influence)

    return normalizeGridMaps(maps)


# ======================================================================================================================
# Distance Calculator
# ======================================================================================================================

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


class ChebyshevDistanceCalculator(DistanceCalculator):
    def __call__(self, *args, **kwargs):
        a = args[0]
        b = args[1]
        d = a - b
        return max(math.fabs(d.X), math.fabs(d.Y))


# ======================================================================================================================
# layout generation
# ======================================================================================================================

def generateLayoutSkeletons(layoutSpec: AreaLayoutSpecification,
                            embeddingMethod: PlanarEmbeddingMethod,
                            skeletonGenerator: SkeletonGenerator):
    embedding = embeddingMethod.calculateEmbedding(layoutSpec)
    skeletons = skeletonGenerator.generateSkeleton(embedding, layoutSpec)
    return embedding, skeletons


# ======================================================================================================================
# Canvas Partitioning
# ======================================================================================================================

def isSeedFarEnoughFromBorders(s, minDistance):
    return minDistance < s.X and minDistance < s.Y and \
           minDistance < 1 - s.X and minDistance < 1 - s.Y


def partitionCanvasByAreaSkeletons(canvas: Canvas2D,
                                   layoutSpec: AreaLayoutSpecification,
                                   skeletons: List[AreaSkeleton],
                                   BoundRadiusValues: dict,
                                   distanceFunction,
                                   deletionDepth: int = 0) -> (Dict[str, AreaPartition], AreaPartition):
    for area in layoutSpec.areas:
        if not (area in BoundRadiusValues.keys()):
            BoundRadiusValues[area] = 1
        elif BoundRadiusValues[area] <= 0:
            BoundRadiusValues[area] = 0.00001

    partitions: Dict[str, AreaPartition] = {}
    emptyPartition: AreaPartition = AreaPartition(EMPTY_PART)
    for s in skeletons:
        partitions[s.areaName] = AreaPartition(s.areaName)

    seeds = canvas.Seeds
    for seed in seeds:
        distances = list(map(
            lambda skeleton:
            skeleton.findDistanceToPoint(seed, distanceFunction),
            skeletons))

        minDist = min(distances)
        scaledMinDist = 1.1 * minDist

        # check if the seed is closer to skeleton than borders.
        # If so, assign it to nearest skeleton.
        # Otherwise, add it to empty partition.
        if isSeedFarEnoughFromBorders(seed, scaledMinDist):
            skeleton_index = distances.index(minDist)
            areaName = skeletons[skeleton_index].areaName

            if minDist < BoundRadiusValues[areaName]:
                partitions[areaName].addCell(seed, canvas.getPolygonOfSeed(seed))
            else:
                emptyPartition.addCell(seed, canvas.getPolygonOfSeed(seed))
        else:
            emptyPartition.addCell(seed, canvas.getPolygonOfSeed(seed))

    def isSeedInOtherPartitions(seedToCheck: Vector2D, areasToIgnore: list):
        for a in partitions.keys():
            if (not (a in areasToIgnore)) and (seedToCheck in partitions[a].seeds):
                return True
        return False

    def getNeighbourCellsInDepth(root_seed, depth: int) -> list:
        neighbourCells = {root_seed}
        for i in range(depth):
            cells = copy.copy(neighbourCells)
            for seed_to_check in cells:
                neighbour_to_add_list = canvas.getNeighboursOfSeed(seed_to_check)
                for neighbour_to_add in neighbour_to_add_list:
                    neighbourCells.add(neighbour_to_add)
        return list(neighbourCells)

    # Move undesired cells to the empty partition
    postProcessedPartitions = partitions.copy()
    for area in partitions.keys():
        ignoreList = layoutSpec.getNeighbours(area)
        ignoreList.append(area)

        for seed in partitions[area].seeds:
            badCell = False
            neighbours = canvas.getNeighboursOfSeed(seed)
            for n in neighbours:
                if isSeedInOtherPartitions(n, ignoreList):
                    badCell = True

            if badCell:
                to_remove = getNeighbourCellsInDepth(seed, deletionDepth)
                for c in to_remove:
                    postProcessedPartitions[area].removeCell(c)
                    emptyPartition.addCell(c, canvas.getPolygonOfSeed(c))

    postProcessedPartitions[EMPTY_PART] = emptyPartition
    return postProcessedPartitions


# ======================================================================================================================
# Landscape Generation
# ======================================================================================================================


def generateLandscapeMaps(mapWidth: int,
                          mapHeight: int,
                          landscapes: dict,
                          landscapeSettings: dict,
                          influenceMaps: dict,
                          heightMap: GridMap) -> dict:
    maps = {}
    for landscapeName in landscapes:
        maps[landscapeName] = GridMap(mapWidth, mapHeight)

    for areaName in landscapeSettings.keys():
        ms: dict = landscapeSettings[areaName].generateLandscapeMaps(areaName,
                                                                     mapWidth,
                                                                     mapHeight,
                                                                     landscapes,
                                                                     influenceMaps,
                                                                     heightMap)
        for landscapeName in ms.keys():
            maps[landscapeName] = addGrids(maps[landscapeName], ms[landscapeName])

    return normalizeGridMaps(maps)


# ======================================================================================================================
# Landscape Surface
# ======================================================================================================================

def calcSurfaceTotalInfluence(surface: string, x: int, y: int, landscapeMaps: dict, landscapes: dict):
    totalInfluence = 0.0
    for landscapeName in landscapeMaps.keys():
        if landscapes[landscapeName].surfaceType == surface:
            inf = landscapeMaps[landscapeName].getValue(x, y)
            totalInfluence = totalInfluence + inf

    return totalInfluence


def generateSurfaceMaps(landscapeMaps: Dict, landscapes: Dict) -> dict:
    maps: dict = {}
    mapWidth = (list(landscapeMaps.values()))[0].width
    mapHeight = (list(landscapeMaps.values()))[0].height

    surfaces = [c.surfaceType for c in landscapes.values()]
    pixelList = generate_2d_mesh(mapWidth, mapHeight)

    for surface in surfaces:
        m = [calcSurfaceTotalInfluence(surface, x, y, landscapeMaps, landscapes) for x, y in pixelList]
        maps[surface] = GridMap(mapWidth, mapHeight)
        maps[surface].importValues(m)

    return normalizeGridMaps(maps)


# ======================================================================================================================
# Landscape Vegetation
# ======================================================================================================================

def calcVegetationDensity(x: int, y: int, landscapeMaps: Dict, landscapes: Dict):
    density = 0.0
    for landscapeName in landscapeMaps.keys():
        inf = landscapeMaps[landscapeName].getValue(x, y)
        density = density + landscapes[landscapeName].vegetationDensity * inf

    return density


def generateVegetationDensityMap(landscapeMaps: Dict, landscapes: Dict) -> GridMap:
    mapWidth = (list(landscapeMaps.values()))[0].width
    mapHeight = (list(landscapeMaps.values()))[0].height

    pixelList = generate_2d_mesh(mapWidth, mapHeight)

    densities = [calcVegetationDensity(x, y, landscapeMaps, landscapes) for x, y in pixelList]
    finalMap = GridMap(mapWidth, mapHeight)
    finalMap.importValues(densities)
    return finalMap


def calcVegetationTypeWeight(vegType: string, x: int, y: int, landscapeMaps: Dict, landscapes: Dict):
    totalWeight = 0.0
    for landscapeName in landscapeMaps.keys():
        inf = landscapeMaps[landscapeName].getValue(x, y)
        totalWeight = totalWeight + landscapes[landscapeName].getVegetationWeight(vegType) * inf

    return totalWeight


def generateVegetationTypeMaps(landscapeMaps: Dict, landscapes: Dict) -> dict:
    maps: dict = {}
    mapWidth = (list(landscapeMaps.values()))[0].width
    mapHeight = (list(landscapeMaps.values()))[0].height

    # gather up all of the vegetation types
    vegTypes: set = set()
    for landscapeName in landscapes.keys():
        for vegType in landscapes[landscapeName].vegetationTypes.keys():
            vegTypes.add(vegType)

    pixelList = generate_2d_mesh(mapWidth, mapHeight)

    for vegType in vegTypes:
        m = [calcVegetationTypeWeight(vegType, x, y, landscapeMaps, landscapes) for x, y in pixelList]
        maps[vegType] = GridMap(mapWidth, mapHeight)
        maps[vegType].importValues(m)
        maps[vegType] = normalizeGridMapValues(maps[vegType])

    return normalizeGridMaps(maps)


def assignVegetation(x: int, y: int, vegTypeMaps: dict, vegetationDensityMap: GridMap):
    chanceOfVegetation = vegetationDensityMap.getValue(x, y)
    r = rnd.random()
    if r < chanceOfVegetation:
        typeRand = rnd.random()
        for vegType in vegTypeMaps.keys():
            typeChance = vegTypeMaps[vegType].getValue(x, y)
            if typeRand <= typeChance:
                return x, y, vegType
            else:
                typeRand = typeRand - typeChance
        return x, y, None
    else:
        return x, y, None


def generateVegetationLocations(vegTypeMaps: dict, vegetationDensityMap: GridMap) -> dict:
    mapWidth = (list(vegTypeMaps.values()))[0].width
    mapHeight = (list(vegTypeMaps.values()))[0].height

    pixelList = generate_2d_mesh(mapWidth, mapHeight)

    locations: dict = {}
    assignments = [assignVegetation(x, y, vegTypeMaps, vegetationDensityMap) for x, y in pixelList]

    for vegType in vegTypeMaps.keys():
        locations[vegType] = [[assign[0], assign[1]] for assign in assignments if assign[2] == vegType]
    return locations


# ======================================================================================================================
# Landscape process
# ======================================================================================================================

def generateLandscapeData(landscapes: dict,
                          landscapeSetting: dict,
                          mapWidth: int,
                          mapHeight: int,
                          influenceMaps: dict,
                          heightMap: GridMap):
    landscapeMaps = generateLandscapeMaps(mapWidth=mapWidth,
                                          mapHeight=mapHeight,
                                          landscapes=landscapes,
                                          landscapeSettings=landscapeSetting,
                                          influenceMaps=influenceMaps,
                                          heightMap=heightMap)

    surfaceMaps = generateSurfaceMaps(landscapeMaps=landscapeMaps, landscapes=landscapes)

    vegetationDensityMap = generateVegetationDensityMap(landscapeMaps, landscapes)
    vegetationTypeMaps = generateVegetationTypeMaps(landscapeMaps, landscapes)
    vegetationLocations = generateVegetationLocations(vegetationTypeMaps, vegetationDensityMap)

    return landscapeMaps, surfaceMaps, vegetationDensityMap, vegetationTypeMaps, vegetationLocations


# ======================================================================================================================
# Height Map Generation
# ======================================================================================================================

def calcHeightOfPixelFromPartialHeightMaps(x: int, y: int, influenceMaps: dict, partialHeightMaps: dict) -> float:
    h = 0
    for area in partialHeightMaps.keys():
        h = h + partialHeightMaps[area].getValue(x, y) * influenceMaps[area].getValue(x, y)
    return h


def generateHeightMapFromElevationSettings(mapWidth: int,
                                           mapHeight: int,
                                           partitions: dict,
                                           influenceMaps: dict,
                                           heightSettings: dict) -> GridMap:
    partialHeightMaps: dict = {}
    scaledPartitions = copy.deepcopy(partitions)
    for area in scaledPartitions.keys():
        scaledPartitions[area].scalePartition(mapWidth, mapHeight)

    for area in scaledPartitions.keys():
        partialHeightMaps[area] = heightSettings[area].heightMapForPartition(scaledPartitions[area], mapWidth,
                                                                             mapHeight)

    pixelList = generate_2d_mesh(mapWidth, mapHeight)

    heightValues = \
        [calcHeightOfPixelFromPartialHeightMaps(x, y, influenceMaps, partialHeightMaps) for x, y in pixelList]

    heightMap = GridMap(mapWidth, mapHeight)
    heightMap.importValues(heightValues)
    return heightMap


# ======================================================================================================================
# Marker Placement
# ======================================================================================================================

def placeMarkers(markerSpecifications: list, partitions: list, heightMap: GridMap):
    placements = {}
    for spec in markerSpecifications:
        placements[spec.name] = spec.placeMarker(partitions, heightMap)

    return placements
