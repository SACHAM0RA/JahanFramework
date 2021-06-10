import numpy as np


class GridMap:
    def __init__(self, w: int, h: int):
        self.__width = w
        self.__height = h
        self.__values = [0.0] * (w * h)

    def __len__(self):
        return len(self.__values)

    def __isValidIndex(self, x: int, y: int):
        return 0 <= x < self.__width and 0 <= y < self.__height

    def __extractCoordinates(self, index):
        return index / self.__width, index % self.__height

    def __extractIndex(self, x: int, y: int):
        return y * self.__width + x

    def getValue(self, x, y):
        x = int(x)
        y = int(y)

        if self.__isValidIndex(x, y):
            index = self.__extractIndex(x, y)
            return self.__values[index]
        else:
            raise IndexError("X and Y are not valid for GrayscaleMap")

    def setValue(self, x: int, y: int, value: float):
        if self.__isValidIndex(x, y):
            if 0 <= value <= 1:
                index = self.__extractIndex(x, y)
                self.__values[index] = value
            else:
                raise Exception("Values in GrayscaleMaps should in [0.0, 1.0]")
        else:
            raise IndexError("X and Y are not valid for GrayscaleMap")

    def importValues(self, values: list):
        if len(values) == self.__width * self.__height:
            self.__values = values.copy()
        else:
            raise Exception(
                "Cannot import values. {A} != {B}".format(A=len(values), B=self.__width * self.__height))

    def exportValues(self):
        return self.__values.copy()

    @property
    def width(self):
        return self.__width

    @property
    def height(self):
        return self.__height

    @property
    def valueRange(self) -> float:
        minV = np.nanmin(self.__values)
        maxV = np.nanmax(self.__values)
        return abs(maxV - minV)

    @property
    def valueMin(self) -> float:
        return np.min(self.__values)

    @property
    def valueMax(self) -> float:
        return np.max(self.__values)

    @property
    def asListOfListsForImShow(self):
        ret = []
        for y in range(1, self.height):
            ret.append([])
            for x in range(1, self.width):
                ret[y - 1].append(self.getValue(x, self.height - y))
        return ret

    def exportFor3DPlotting(self):
        values = []
        for i in range(len(self.__values)):
            x = int(i % self.__height)
            y = int(i / self.__width)
            values.append(self.getValue(x, y))
        return values

    def exportForContour(self):
        values = []
        for i in range(len(self.__values)):
            x = int(i % self.__height)
            y = int(i / self.__width)
            values.append(self.getValue(x, y))
        return values


def addGrids(a: GridMap, b: GridMap):
    if len(a) == len(b):
        bValues = b.exportValues()
        aValues = a.exportValues()
        sums = [aValues[i] + bValues[i] for i in range(len(a))]
        newMap = GridMap(a.width, a.height)
        newMap.importValues(sums)
        return newMap
    else:
        raise Exception("Cannot ADD Grids with different sizes")


def subGrids(a: GridMap, b: GridMap):
    if len(a) == len(b):
        bValues = b.exportValues()
        aValues = a.exportValues()
        sums = [aValues[i] - bValues[i] for i in range(len(a))]
        newMap = GridMap(a.width, a.height)
        newMap.importValues(sums)
        return newMap
    else:
        raise Exception("Cannot SUB Grids with different sizes")


def divGrids(a: GridMap, b: GridMap):
    if len(a) == len(b):
        bValues = b.exportValues()
        aValues = a.exportValues()

        divs = []
        for i in range(len(a)):
            if bValues[i] == 0.0:
                divs.append(0.0)
            else:
                divs.append(aValues[i] / bValues[i])

        newMap = GridMap(a.width, a.height)
        newMap.importValues(divs)
        return newMap
    else:
        raise Exception("Cannot DIV Grids with different sizes")


def mulGrids(a: GridMap, b: GridMap):
    if len(a) == len(b):
        bValues = b.exportValues()
        aValues = a.exportValues()
        sums = [aValues[i] * bValues[i] for i in range(len(a))]
        newMap = GridMap(a.width, a.height)
        newMap.importValues(sums)
        return newMap
    else:
        raise Exception("Cannot MUL Grids with different sizes")


def scaleGrid(a: GridMap, scalar: float):
    aValues = a.exportValues()
    scaled = [aValues[i] * scalar for i in range(len(aValues))]
    newMap = GridMap(a.width, a.height)
    newMap.importValues(scaled)
    return newMap


def normalizeGridMaps(maps: dict) -> dict:
    w = (list(maps.values()))[0].width
    h = (list(maps.values()))[0].height
    sumMap = GridMap(w, h)
    for key in maps.keys():
        sumMap = addGrids(sumMap, maps[key])

    normalMaps = {}
    for key in maps.keys():
        normalMaps[key] = divGrids(maps[key], sumMap)
    return normalMaps


def normalizeGridMapValues(m: GridMap) -> GridMap:
    values = m.exportValues()
    upper = max(values)
    lower = min(values)
    normalValues = [(v - lower) / (upper - lower) for v in values]
    newMap = GridMap(m.width, m.height)
    newMap.importValues(normalValues)
    return newMap
