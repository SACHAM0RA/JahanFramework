import copy
import string
import networkx as nx
from jahan.VectorArithmetic import *
from shapely.geometry import Point, Polygon


class AreaClimate:
    influenceFadeRadius: float
    surfaceType: string
    vegetationTypes: dict
    vegetationProbability: float

    def __init__(self, influenceFadeRadius: float,
                 surfaceType: string,
                 vegetationProbability: float,
                 vegetationSetting: dict):
        self.influenceFadeRadius = influenceFadeRadius
        self.surfaceType = surfaceType
        self.vegetationTypes = vegetationSetting
        self.vegetationProbability = vegetationProbability

    def __copy__(self):
        return AreaClimate(self.influenceFadeRadius,
                           self.surfaceType,
                           self.vegetationProbability,
                           self.vegetationTypes)

    def __deepcopy__(self, memodict={}):
        return self.__copy__()

    def __key(self):
        return self.influenceFadeRadius, self.surfaceType, self.vegetationTypes, self.vegetationProbability

    def __hash__(self):
        return hash(self.__key())

    def hasVegetationType(self, vegType: string):
        return vegType in self.vegetationTypes.keys()

    def getVegetationWeight(self, vegType: string):
        if self.hasVegetationType(vegType):
            return self.vegetationTypes[vegType]
        else:
            return 0.0


# ======================================================================================================================

class AreaLayout:

    def __init__(self):
        self.__areas: List = []
        self.__neighbourhoods: List = []
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

    def __key(self):
        return self.__areas, self.__neighbourhoods

    def __hash__(self):
        return hash(self.__key())

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
        distances = [s.getDistanceToPoint(p, distanceFunction) for s in self.__segments]
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
    __canvasSeeds: List = []  # List of Vectors
    __canvasCells: List = []  # list of list of Vectors, each list is one polygon
    __DirtySuperCell = True
    __cachedSuperCell = None

    def __init__(self, areaName: string):
        self.__areaName = areaName
        self.__canvasSeeds = []
        self.__canvasCells = []

    def __copy__(self):
        cp = AreaPartition(self.areaName)
        for i in range(len(self.__canvasSeeds)):
            cp.addCell(copy.copy(self.__canvasSeeds[i]),
                       copy.copy(self.__canvasCells[i]))
        return cp

    def __deepcopy__(self, memodict={}):
        return self.__copy__()

    def addCell(self, seed: Vector2D, cell: List[Vector2D]):
        self.__canvasSeeds.append(seed)
        self.__canvasCells.append(cell)
        self.__DirtySuperCell = True

    def removeCell(self, seed: Vector2D):
        index = self.__canvasSeeds.index(seed)
        self.__canvasSeeds.remove(seed)
        self.__canvasCells.remove(self.__canvasCells[index])
        self.__DirtySuperCell = True

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
        if not self.__DirtySuperCell:
            return self.__cachedSuperCell
        else:
            cells = self.cells
            segments = []
            for cell in cells:
                size = len(cell)
                for i in range(size):
                    segment = Segment2D(cell[i % size], cell[(i + 1) % size])
                    segments.append(segment)

            borderSegments = [s for s in segments if segments.count(s) == 1]

            def findContinueOrMeetSegment(target: Segment2D, segments: list):
                for s in segments:
                    if s != target:
                        if s.continues(target):
                            return s
                        if s.meets(target):
                            s.reverse()
                            return s
                return None

            orderedSegments: list = [borderSegments[0]]
            for i in range(len(borderSegments) - 1):
                orderedSegments.append(findContinueOrMeetSegment(orderedSegments[i], borderSegments))

            self.__DirtySuperCell = False
            self.__cachedSuperCell = orderedSegments
            return orderedSegments

    @property
    def superCellPoints(self):
        superSegments = self.superCellSegments
        return [s.start for s in superSegments]

    @property
    def superCellPointsAsList(self):
        polygon = self.superCellPoints
        return [p.asList for p in polygon]

    def scalePartition(self, w: int, h: int):
        scale = Vector2D(w, h)
        for i in range(len(self.__canvasSeeds)):
            self.__canvasSeeds[i] = self.__canvasSeeds[i] * scale
            newCell = []
            for j in range(len(self.__canvasCells[i])):
                newCell.append(self.__canvasCells[i][j] * scale)
            self.__canvasCells[i] = newCell

    def containsPoint(self, p: Vector2D) -> bool:
        poly = Polygon(self.superCellPointsAsList)
        return poly.contains(Point(p.asList)) or poly.intersects(Point(p.asList))

    def findDistanceToPoint(self, p: Vector2D) -> float:
        poly = Polygon(self.superCellPointsAsList)
        return abs(poly.exterior.distance(Point(p.asList)))
