from functools import reduce


class GridMap:
    __width: int
    __height: int
    __values = []

    def __init__(self, w: int, h: int):
        self.__width = w
        self.__height = h
        self.__values = [0.0] * (w * h)

    def __len__(self):
        return len(self.__values)

    def __isValidIndex(self, row: int, column: int):
        return 0 <= row < self.__height and 0 <= column < self.__width

    def __extractCoordinates(self, index):
        return index / self.__width, index % self.__height

    def __extractIndex(self, row: int, height: int):
        return row * self.__width + height

    def getValue(self, row: int, column: int):
        if self.__isValidIndex(row, column):
            index = self.__extractIndex(row, column)
            return self.__values[index]
        else:
            raise IndexError("Row and Column are not valid for GrayscaleMap")

    def setValue(self, row: int, column: int, value: float):
        if self.__isValidIndex(row, column):
            if 0 <= value <= 1:
                index = self.__extractIndex(row, column)
                self.__values[index] = value
            else:
                raise Exception("Values in GrayscaleMaps should in [0.0, 1.0]")
        else:
            raise IndexError("Row and Column are not valid for GrayscaleMap")

    def importValues(self, values: list):
        if len(values) == self.__width * self.__height:
            self.__values = values.copy()
        else:
            raise Exception("Cannot import values, input list is not consistent with map dimensions.")

    def exportValues(self):
        return self.__values.copy()

    @property
    def width(self):
        return self.__width

    @property
    def height(self):
        return self.__height

    @property
    def asListOfListsForImShow(self):
        ret = []
        for i in range(self.__height):
            ret.append([])
            for j in range(self.__width):
                ret[i].append(self.getValue(j, self.__height - i - 1))
        return ret


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

        sums = []
        for i in range(len(a)):
            if bValues[i] == 0:
                sums.append(0.0)
            else:
                sums.append(aValues[i] / bValues[i])

        newMap = GridMap(a.width, a.height)
        newMap.importValues(sums)
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


def normalizeMaps(maps: dict) -> dict:
    w = (list(maps.values()))[0].width
    h = (list(maps.values()))[0].height
    sumMap = GridMap(w, h)
    for key in maps.keys():
        sumMap = addGrids(sumMap, maps[key])

    normalMaps = {}
    for key in maps.keys():
        normalMaps[key] = divGrids(maps[key], sumMap)
    return normalMaps


def normalizeMapValues(m: GridMap) -> GridMap:
    values = m.exportValues()
    upper = max(values)
    lower = min(values)
    normalValues = [(v - lower) / (upper - lower) for v in values]
    newMap = GridMap(m.width, m.height)
    newMap.importValues(normalValues)
    return newMap
