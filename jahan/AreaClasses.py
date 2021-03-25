import string
from typing import List
import networkx as nx

from jahan.VectorArithmetic import *


class AreaLayout:
    __areas: List = []
    __neighbourhoods: List = []
    __graph: nx.Graph

    def __init__(self):
        self.__graph = nx.Graph()

    def __len__(self):
        return len(self.__areas)

    def addArea(self, area: string):
        if not (area in self.__areas):
            self.__areas.append(area)
            self.__graph.add_node(area)

    def connectAreas(self, a: string, b: string):
        if (a in self.__areas) and (b in self.__areas) and (not (a, b) in self.__neighbourhoods):
            self.__neighbourhoods.append((a, b))
            self.__graph.add_edge(a, b)

    def hasArea(self, area: string):
        return area in self.__areas

    def hasNeighbourhood(self, a: string, b: string):
        return (a, b) in self.__neighbourhoods

    @property
    def areas(self):
        return self.__areas.copy()

    @property
    def neighbourhoods(self):
        return self.__neighbourhoods.copy()

    def getNeighbours(self, area: string) -> List:
        return list(self.__graph.neighbors(area))

    @property
    def networkxGraph(self):
        return self.__graph


# ======================================================================================================================

class AreaSkeleton:
    __areaName: string
    __segments: List = []
    __root: Vector2D

    def __init__(self, name: string, root: Vector2D, segments: List):
        self.__areaName = name
        self.__root = root
        self.__segments = segments

    def findDistanceToPoint(self, p: Vector2D, distanceFunction: FunctionType) -> float:
        distances = map(lambda s: s.getDistanceToPoint(p, distanceFunction), self.__segments)
        return min(distances)

    @property
    def areaName(self) -> string:
        return self.__areaName

    @property
    def root(self) -> Vector2D:
        return self.__root.__copy__()

    @property
    def segments(self) -> List[Segment2D]:
        return self.__segments.copy()


# ======================================================================================================================

class AreaPartition:
    __areaName: string
    __canvasSeeds: List = []
    __canvasCells: List = []

    def __init__(self, areaName: string):
        self.__areaName = areaName
        self.__canvasSeeds = []
        self.__canvasCells = []

    def addCell(self, seed: Vector2D, cell: List[Vector2D]):
        self.__canvasSeeds.append(seed)
        self.__canvasCells.append(cell)

    def removeCell(self, seed: Vector2D):
        index = self.__canvasSeeds.index(seed)
        self.__canvasSeeds.remove(seed)
        self.__canvasCells.remove(self.__canvasCells[index])

    @property
    def areaName(self):
        return self.__areaName

    @property
    def seeds(self):
        return self.__canvasSeeds.copy()

    @property
    def cells(self):
        return self.__canvasCells.copy()

    @property
    def superCellSegments(self):
        cells = self.cells
        segments = []
        for cell in cells:
            size = len(cell)
            for i in range(size):
                segment = Segment2D(cell[i % size], cell[(i + 1) % size])
                segments.append(segment)

        return list(filter(lambda s: segments.count(s) == 1, segments))
