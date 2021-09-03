import itertools

from jahan.Layout import AreaPolygon
from jahan.GridMap import GridMap, addGrids
import jahan.Noise2D as noise2d
from jahan.VectorArithmetic import Vector2D
import multiprocessing


def generate_2d_mesh(mapWidth, mapHeight):
    ret = list(itertools.product(range(mapWidth), range(mapHeight)))
    ret = [(x, y) for y, x in ret]
    return ret


# ===========================================
# Height Foundation
# ===========================================

class HeightFoundation:
    def __call__(self, polygon: AreaPolygon, mapWidth: int, mapHeight: int) -> GridMap:
        return GridMap(mapWidth, mapHeight)


class Flat_HeightFoundation(HeightFoundation):
    def __init__(self, flatHeight: float):
        self.__H = flatHeight

    def __call__(self, polygon: AreaPolygon, mapWidth: int, mapHeight: int) -> GridMap:
        heightMap = GridMap(mapWidth, mapHeight)
        heightMap.importValues([self.__H] * mapWidth * mapHeight)
        return heightMap


class getSignedDistanceOfPixelToAreaPolygon:
    def __init__(self, polygon: AreaPolygon):
        self.polygon = polygon

    def __call__(self, p):
        pixel = Vector2D(p[0], p[1])
        absDist = self.polygon.findDistanceToPoint(pixel)
        if self.polygon.containsPoint(pixel):
            return -1 * absDist
        else:
            return absDist


class SDF_HeightFoundation(HeightFoundation):
    def __init__(self, ascending: bool, minHeight: float, maxHeight: float):
        self.__ascending = ascending
        self.__minH = min(minHeight, maxHeight)
        self.__maxH = max(minHeight, maxHeight)

    def __call__(self, polygon: AreaPolygon, mapWidth: int, mapHeight: int) -> GridMap:
        pixelList = generate_2d_mesh(mapWidth, mapHeight)

        pool = multiprocessing.Pool(processes=4)
        pixelDistanceValues = list(pool.map(getSignedDistanceOfPixelToAreaPolygon(polygon), pixelList))

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


def ease(x: float):
    if x < 0.5:
        return 4 * x * x * x
    else:
        return 1 - ((-2 * x + 2) ** 3) / 2


class distance_from_point:
    def __init__(self, center_of_mass, polygon, applyEasing=False):
        self.center_of_mass = center_of_mass
        self.max_seed_dist = max([(self.center_of_mass - s).length for s in polygon.seeds])
        self.applyEasing = applyEasing

    def __call__(self, p):
        pixel = Vector2D(p[0], p[1])
        dist = (self.center_of_mass - pixel).length / self.max_seed_dist
        if self.applyEasing:
            return ease(min(dist, 1.0))
        return min(dist, 1.0)


class Cone_HeightFoundation(HeightFoundation):
    def __init__(self, ascending: bool, minHeight: float, maxHeight: float):
        self.__ascending = ascending
        self.__minH = min(minHeight, maxHeight)
        self.__maxH = max(minHeight, maxHeight)

    def __call__(self, polygon: AreaPolygon, mapWidth: int, mapHeight: int) -> GridMap:
        pixelList = generate_2d_mesh(mapWidth, mapHeight)

        pool = multiprocessing.Pool(processes=4)
        center_of_mass = polygon.centerOfMass
        dist_func = distance_from_point(center_of_mass, polygon, False)
        pixelDistanceValues = list(pool.map(dist_func, pixelList))

        maxDist = abs(max(pixelDistanceValues))
        pixelDistanceValues = [d / maxDist for d in pixelDistanceValues]
        diffH = self.__maxH - self.__minH
        if self.__ascending:
            pixelDistanceValues = [self.__maxH - diffH * d for d in pixelDistanceValues]
        else:
            pixelDistanceValues = [self.__minH + diffH * d for d in pixelDistanceValues]

        heightMap = GridMap(mapWidth, mapHeight)
        heightMap.importValues(pixelDistanceValues)
        return heightMap


class Bell_HeightFoundation(HeightFoundation):
    def __init__(self, ascending: bool, minHeight: float, maxHeight: float):
        self.__ascending = ascending
        self.__minH = min(minHeight, maxHeight)
        self.__maxH = max(minHeight, maxHeight)

    def __call__(self, polygon: AreaPolygon, mapWidth: int, mapHeight: int) -> GridMap:
        pixelList = generate_2d_mesh(mapWidth, mapHeight)

        pool = multiprocessing.Pool(processes=4)
        center_of_mass = polygon.centerOfMass
        dist_func = distance_from_point(center_of_mass, polygon, True)
        pixelDistanceValues = list(pool.map(dist_func, pixelList))

        maxDist = abs(max(pixelDistanceValues))
        pixelDistanceValues = [d / maxDist for d in pixelDistanceValues]
        diffH = self.__maxH - self.__minH
        if self.__ascending:
            pixelDistanceValues = [self.__maxH - diffH * d for d in pixelDistanceValues]
        else:
            pixelDistanceValues = [self.__minH + diffH * d for d in pixelDistanceValues]

        heightMap = GridMap(mapWidth, mapHeight)
        heightMap.importValues(pixelDistanceValues)
        return heightMap


# ===========================================
# Height Noise
# ===========================================

class HeightNoiseGenerator:
    def __init__(self, amplitude: float, scale: float):
        self.__a = amplitude
        self.__s = scale

    @property
    def amplitude(self):
        return self.__a

    @property
    def scale(self):
        return self.__s

    def generateNoiseMap(self, width: int, height: int) -> GridMap:
        return GridMap(width, height)


class WhiteHeightNoiseGenerator(HeightNoiseGenerator):
    def generateNoiseMap(self, width: int, height: int) -> GridMap:
        noise = noise2d.whiteNoise(width, height, self.amplitude)
        m: GridMap = GridMap(width, height)
        m.importValues(noise)
        return m


class PerlinHeightNoiseGenerator(HeightNoiseGenerator):
    def __init__(self, amplitude=1, scale=8, octaves=4):
        super().__init__(amplitude, scale)
        self.octaves = octaves

    def generateNoiseMap(self, width: int, height: int) -> GridMap:
        noise = noise2d.perlinNoise(width, height, self.amplitude, self.scale, self.octaves)
        m: GridMap = GridMap(width, height)
        m.importValues(noise)
        return m


class OpenSimplexHeightNoiseGenerator(HeightNoiseGenerator):
    def __init__(self, amplitude=1, scale=8, octaves=4):
        super().__init__(amplitude, scale)
        self.octaves = octaves

    def generateNoiseMap(self, width: int, height: int) -> GridMap:
        noise = noise2d.openSimplexNoise(width, height, self.amplitude, self.scale, self.octaves)
        m: GridMap = GridMap(width, height)
        m.importValues(noise)
        return m


class WorleyHeightNoiseGenerator(HeightNoiseGenerator):
    def __init__(self, amplitude=1, scale=8, seedCount=50):
        super().__init__(amplitude, scale)
        self.seedCount = seedCount

    def generateNoiseMap(self, width: int, height: int) -> GridMap:
        noise = noise2d.worleyNoise(width, height, self.amplitude, self.seedCount)
        m: GridMap = GridMap(width, height)
        m.importValues(noise)
        return m


# ===========================================
# Height Profile
# ===========================================

class HeightProfile:
    def __init__(self, foundation: HeightFoundation, detail: HeightNoiseGenerator = None, fadeRadius: float = 0.1):
        self.__foundation: HeightFoundation = foundation
        self.__detail = detail

    def heightMapForPolygon(self, polygon, mapWidth, mapHeight):
        foundationHeight = self.__foundation(polygon, mapWidth, mapHeight)
        if self.__detail is not None:
            return addGrids(foundationHeight, self.__detail.generateNoiseMap(mapWidth, mapHeight))
        else:
            return foundationHeight
