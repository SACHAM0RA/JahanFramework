import itertools
import math
import multiprocessing
import string

from jahan.GridMap import GridMap, normalizeGridMaps, normalizeGridMapValues, mulGrids

NONE_ITEM_KEY = "NONE_ITEM"
NONE_ITEM: dict = {NONE_ITEM_KEY: 4096}


def easeInOut(x: float):
    if x < 0.5:
        return 2 * x * x
    else:
        return 1 - ((-2 * x + 2) ** 2) / 2


def generate_2d_mesh(mapWidth, mapHeight):
    ret = list(itertools.product(range(mapWidth), range(mapHeight)))
    ret = [(x, y) for y, x in ret]
    return ret


class LandscapeMapGenerator:
    def __init__(self):
        pass

    def generateLandscapeMaps(self,
                              areaName: string,
                              width: int,
                              height: int,
                              landscapes: dict,
                              influenceMaps: dict,
                              heightMap: GridMap):
        pass


class SingleProfileLandscapeGenerator(LandscapeMapGenerator):
    def __init__(self, desiredLandscapeName: string):
        super().__init__()
        self.__desiredLandscapeName = desiredLandscapeName

    def generateLandscapeMaps(self,
                              areaName: string,
                              width: int,
                              height: int,
                              landscapes: dict,
                              influenceMaps: dict,
                              heightMap: GridMap):
        maps = {}
        for landscapeName in landscapes.keys():
            if landscapeName == self.__desiredLandscapeName:
                maps[landscapeName] = influenceMaps[areaName]
            else:
                maps[landscapeName] = GridMap(width, height)
        return maps


# ===========================================


class calcLandscapeInfluenceOnPixelByHeight:
    def __init__(self,
                 heightMap: GridMap,
                 desiredHeight: float,
                 fadeHeight: float):
        self.heightMap = heightMap
        self.desiredHeight = desiredHeight
        self.fadeHeight = fadeHeight

    def __call__(self, pixel) -> float:
        x = pixel[0]
        y = pixel[1]

        h: float = self.heightMap.getValue(x, y)
        diff = abs(h - self.desiredHeight)
        norm = min(diff, self.fadeHeight) / self.fadeHeight
        return easeInOut(1 - norm)


class HeightBasedLandscapeGenerator(LandscapeMapGenerator):
    def __init__(self, heightOrder: list):
        super().__init__()
        self.__heightOrder = heightOrder

    def generateLandscapeMaps(self,
                              areaName: string,
                              width: int,
                              height: int,
                              landscapes: dict,
                              influenceMaps: dict,
                              heightMap: GridMap):
        landscape_maps = {}
        pool = multiprocessing.Pool(processes=4)
        pixelList = generate_2d_mesh(width, height)

        h_min = heightMap.valueMin
        h_range = heightMap.valueRange

        areaInfluence = influenceMaps[areaName]

        desiredHeights = {}
        step: float = h_range / (len(self.__heightOrder) - 1)
        for i in range(len(self.__heightOrder)):
            landscapeName = self.__heightOrder[i]
            desiredHeights[landscapeName] = h_min + i * step

        for landscapeName in landscapes.keys():
            calcLandscapeInfluenceOnPixelByHeight_callable = \
                calcLandscapeInfluenceOnPixelByHeight(heightMap, desiredHeights[landscapeName], step)

            influence = list(pool.map(calcLandscapeInfluenceOnPixelByHeight_callable, pixelList))
            landscape_maps[landscapeName] = GridMap(width, height)
            landscape_maps[landscapeName].importValues(influence)

        landscape_maps = normalizeGridMaps(landscape_maps)

        for landscapeName in landscape_maps.keys():
            landscape_maps[landscapeName] = mulGrids(landscape_maps[landscapeName], areaInfluence)
        return landscape_maps


# ================ PROFILE ==================

class LandscapeProfile:
    def __init__(self,
                 surfaceType: string,
                 itemDensity: float,
                 itemTypes: dict):
        self.surfaceType = surfaceType
        self.itemTypes = itemTypes
        self.itemDensity = itemDensity

    def __copy__(self):
        return LandscapeProfile(self.surfaceType,
                                self.itemDensity,
                                self.itemTypes)

    def __key(self):
        return self, self.surfaceType, self.itemTypes, self.itemDensity

    def __hash__(self):
        return hash(self.__key())

    def hasItemType(self, itemType: string):
        return itemType in self.itemTypes.keys()

    def getItemWeight(self, itemType: string):
        if self.hasItemType(itemType):
            return self.itemTypes[itemType]
        else:
            return 0.0
