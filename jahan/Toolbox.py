import multiprocessing

from jahan.Layout import *
from jahan.GridMap import *
from jahan.Canvas import *
from jahan.Noise2D import *
from jahan.VectorArithmetic import Vector2D

# ======================================================================================================================
# General Stuff
# ======================================================================================================================

EMPTY_POLY = "EMPTY_POLYGON"

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
    def __init__(self, polygons: dict):
        self.polygons = polygons

    def __call__(self, p):
        container = EMPTY_POLY
        pixel = Vector2D(p[0], p[1])
        for areaName in self.polygons.keys():
            if areaName != EMPTY_POLY and self.polygons[areaName].containsPoint(pixel):
                container = areaName
                break
        return p, container


# ======================================================================================================================
# Polygon Influence
# ======================================================================================================================

class calcPolygonInfluenceOnPixel(object):
    def __init__(self, areaName: string, polygons: dict, areaOfPixels, fadeRadius: float = 0.075):
        self.areaName = areaName
        self.polygon = polygons[areaName]
        self.polygons = polygons
        self.areaOfPixels = areaOfPixels
        self.fadeRadius = fadeRadius

    def __call__(self, p):
        areaOfPixel = self.areaOfPixels[p]
        pixel = Vector2D(p[0], p[1])

        if self.areaName == EMPTY_POLY:
            dist = self.polygon.findDistanceToClosestBorderSegment(pixel)
        else:
            dist = self.polygon.findDistanceToPoint(pixel)

        if areaOfPixel == self.areaName:
            blendValue = 0.5 + 0.5 * min(dist, self.fadeRadius) / self.fadeRadius
        else:
            blendValue = 0.5 - 0.5 * min(dist, self.fadeRadius) / self.fadeRadius

        return easeInOut(blendValue)


def generateAreaInfluenceMapFromPolygons(polygons: dict, fadeRadius: float, mapWidth: int, mapHeight: int) -> dict:
    polygons = copy.deepcopy(polygons)
    for area in polygons.keys():
        polygons[area].scalePolygon(mapWidth, mapHeight)

    maps: Dict[string, GridMap] = {}
    areaNames = list(polygons.keys())

    pixelList = generate_2d_mesh(mapWidth, mapHeight)

    pool = multiprocessing.Pool(processes=4)
    findContainingAreaForPixel_callable = findContainingAreaForPixel(polygons)
    areaOfPixels = dict(pool.map(findContainingAreaForPixel_callable, pixelList))

    for areaName in areaNames:
        calcInfluenceOnPixel_callable = calcPolygonInfluenceOnPixel(areaName,
                                                                    polygons,
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
                            skeletonGenerator: SkeletonGenerator) -> object:
    embedding = embeddingMethod.calculateEmbedding(layoutSpec)
    skeletons = skeletonGenerator.generateSkeleton(embedding, layoutSpec)
    return embedding, skeletons


# ======================================================================================================================
# Polygon generation
# ======================================================================================================================

def isSeedFarEnoughFromBorders(s, minDistance):
    return minDistance < s.X and minDistance < s.Y and \
           minDistance < 1 - s.X and minDistance < 1 - s.Y


def GeneratePolygonsFromAreaSkeletons(canvas: Canvas2D,
                                      layoutSpec: AreaLayoutSpecification,
                                      skeletons: List[AreaSkeleton],
                                      BoundRadiusValues: dict,
                                      distanceFunction,
                                      deletionDepth: int = 0) -> (Dict[str, AreaPolygon], AreaPolygon):
    for area in layoutSpec.areas:
        if not (area in BoundRadiusValues.keys()):
            BoundRadiusValues[area] = 1
        elif BoundRadiusValues[area] <= 0:
            BoundRadiusValues[area] = 0.00001

    polygons: Dict[str, AreaPolygon] = {}
    emptyPolygon: AreaPolygon = AreaPolygon(EMPTY_POLY)
    for s in skeletons:
        polygons[s.areaName] = AreaPolygon(s.areaName)

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
        # Otherwise, add it to empty polygon.
        if isSeedFarEnoughFromBorders(seed, scaledMinDist):
            skeleton_index = distances.index(minDist)
            areaName = skeletons[skeleton_index].areaName

            if minDist < BoundRadiusValues[areaName]:
                polygons[areaName].addCell(seed, canvas.getPolygonOfSeed(seed))
            else:
                emptyPolygon.addCell(seed, canvas.getPolygonOfSeed(seed))
        else:
            emptyPolygon.addCell(seed, canvas.getPolygonOfSeed(seed))

    def isSeedInOtherPolygonss(seedToCheck: Vector2D, areasToIgnore: list):
        for a in polygons.keys():
            if (not (a in areasToIgnore)) and (seedToCheck in polygons[a].seeds):
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

    # Move undesired cells to the empty polygon
    postProcessedPolygons = polygons.copy()
    for area in polygons.keys():
        ignoreList = layoutSpec.getNeighbours(area)
        ignoreList.append(area)

        for seed in polygons[area].seeds:
            badCell = False
            neighbours = canvas.getNeighboursOfSeed(seed)
            for n in neighbours:
                if isSeedInOtherPolygonss(n, ignoreList):
                    badCell = True

            if badCell:
                to_remove = getNeighbourCellsInDepth(seed, deletionDepth)
                for c in to_remove:
                    postProcessedPolygons[area].removeCell(c)
                    emptyPolygon.addCell(c, canvas.getPolygonOfSeed(c))

    postProcessedPolygons[EMPTY_POLY] = emptyPolygon
    return postProcessedPolygons


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
# Landscape Items
# ======================================================================================================================

def calcItemetationDensity(x: int, y: int, landscapeMaps: Dict, landscapes: Dict):
    density = 0.0
    for landscapeName in landscapeMaps.keys():
        inf = landscapeMaps[landscapeName].getValue(x, y)
        density = density + landscapes[landscapeName].itemDensity * inf

    return density


def generateItemDensityMap(landscapeMaps: Dict, landscapes: Dict) -> GridMap:
    mapWidth = (list(landscapeMaps.values()))[0].width
    mapHeight = (list(landscapeMaps.values()))[0].height

    pixelList = generate_2d_mesh(mapWidth, mapHeight)

    densities = [calcItemetationDensity(x, y, landscapeMaps, landscapes) for x, y in pixelList]
    finalMap = GridMap(mapWidth, mapHeight)
    finalMap.importValues(densities)
    return finalMap


def calcItemTypeWeight(itemType: string, x: int, y: int, landscapeMaps: Dict, landscapes: Dict):
    totalWeight = 0.0
    for landscapeName in landscapeMaps.keys():
        inf = landscapeMaps[landscapeName].getValue(x, y)
        totalWeight = totalWeight + landscapes[landscapeName].getItemWeight(itemType) * inf

    return totalWeight


def generateItemTypeMaps(landscapeMaps: Dict, landscapes: Dict) -> dict:
    maps: dict = {}
    mapWidth = (list(landscapeMaps.values()))[0].width
    mapHeight = (list(landscapeMaps.values()))[0].height

    # gather up all of the item types
    itemTypes: set = set()
    for landscapeName in landscapes.keys():
        for itemType in landscapes[landscapeName].itemTypes.keys():
            itemTypes.add(itemType)

    pixelList = generate_2d_mesh(mapWidth, mapHeight)

    for itemType in itemTypes:
        m = [calcItemTypeWeight(itemType, x, y, landscapeMaps, landscapes) for x, y in pixelList]
        maps[itemType] = GridMap(mapWidth, mapHeight)
        maps[itemType].importValues(m)
        maps[itemType] = normalizeGridMapValues(maps[itemType])

    return normalizeGridMaps(maps)


def assignItem(x: int, y: int, itemTypeMaps: dict, itemDensityMap: GridMap):
    chanceOfItem = itemDensityMap.getValue(x, y)
    r = rnd.random()
    if r < chanceOfItem:
        typeRand = rnd.random()
        for itemType in itemTypeMaps.keys():
            typeChance = itemTypeMaps[itemType].getValue(x, y)
            if typeRand <= typeChance:
                return x, y, itemType
            else:
                typeRand = typeRand - typeChance
        return x, y, None
    else:
        return x, y, None


def generateItemLocations(itemTypeMaps: dict, itemDensityMap: GridMap) -> dict:
    mapWidth = (list(itemTypeMaps.values()))[0].width
    mapHeight = (list(itemTypeMaps.values()))[0].height

    pixelList = generate_2d_mesh(mapWidth, mapHeight)

    locations: dict = {}
    assignments = [assignItem(x, y, itemTypeMaps, itemDensityMap) for x, y in pixelList]

    for itemType in itemTypeMaps.keys():
        locations[itemType] = [[assign[0], assign[1]] for assign in assignments if assign[2] == itemType]
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

    itemDensityMap = generateItemDensityMap(landscapeMaps, landscapes)
    itemTypeMaps = generateItemTypeMaps(landscapeMaps, landscapes)
    itemLocations = generateItemLocations(itemTypeMaps, itemDensityMap)

    return landscapeMaps, surfaceMaps, itemDensityMap, itemTypeMaps, itemLocations


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
                                           polygons: dict,
                                           influenceMaps: dict,
                                           heightSettings: dict) -> GridMap:
    partialHeightMaps: dict = {}
    scaledPolygons = copy.deepcopy(polygons)
    for area in scaledPolygons.keys():
        scaledPolygons[area].scalePolygon(mapWidth, mapHeight)

    for area in scaledPolygons.keys():
        partialHeightMaps[area] = heightSettings[area].heightMapForPolygon(scaledPolygons[area], mapWidth,
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

def placeMarkers(markerSpecifications: list, polygons: list, heightMap: GridMap):
    placements = {}
    for spec in markerSpecifications:
        placements[spec.name] = spec.placeMarker(polygons, heightMap)

    return placements
