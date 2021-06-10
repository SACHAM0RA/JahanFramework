import copy
import math
import string
import networkx as nx
from typing import List, Dict
from jahan.VectorArithmetic import Vector2D, Segment2D, Vector2D_fromList
from shapely.geometry import Point, Polygon


# ======================================================================================================================

class AreaLayoutSpecification:

    def __init__(self):
        self.__areas: list = []
        self.__neighbourhoods: list = []
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

    def findDistanceToPoint(self, p: Vector2D, distanceFunction) -> float:
        if len(self.__segments) != 0:
            distances = [s.getDistanceToPoint(p, distanceFunction) for s in self.__segments]
            return min(distances)
        else:
            return distanceFunction(self.__root, p)

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
    __DirtyBorderSegments = True
    __cachedBorderSegments = None

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
        self.__DirtyBorderSegments = True

    def removeCell(self, seed: Vector2D):
        if seed in self.__canvasSeeds:
            index = self.__canvasSeeds.index(seed)
            self.__canvasSeeds.remove(seed)
            self.__canvasCells.remove(self.__canvasCells[index])
            self.__DirtySuperCell = True
            self.__DirtyBorderSegments = True

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
    def borderSegments(self):
        if not self.__DirtyBorderSegments:
            return self.__cachedBorderSegments
        else:
            cells = self.cells
            segments = []
            for cell in cells:
                size = len(cell)
                for i in range(size):
                    segment = Segment2D(cell[i % size], cell[(i + 1) % size])
                    segments.append(segment)

            borderSegments = [s for s in segments if segments.count(s) == 1]
            self.__DirtyBorderSegments = False
            self.__cachedBorderSegments = borderSegments

            return borderSegments

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

            def findContinueOrMeetSegment(target: Segment2D):
                for s in borderSegments:
                    if s != target:
                        if s.continues(target):
                            return s
                        if s.meets(target):
                            s.reverse()
                            return s
                return None

            orderedSegments: list = [borderSegments[0]]
            for i in range(len(borderSegments) - 1):
                orderedSegments.append(findContinueOrMeetSegment(orderedSegments[i]))

            self.__DirtySuperCell = False
            self.__cachedSuperCell = orderedSegments
            return orderedSegments

    @property
    def centerOfMass(self):
        s = Vector2D(0, 0)
        for seed in self.seeds:
            s = s + seed

        return s * (1 / len(self.seeds))

    @property
    def superCellPoints(self):
        superSegments = self.superCellSegments
        return [s.start for s in superSegments]

    @property
    def superCellPointsAsList(self):
        polygon = self.superCellPoints
        return [p.asList for p in polygon]

    def scalePartition(self, x_scale: int, y_scale: int):
        scale = Vector2D(x_scale, y_scale)
        for i in range(len(self.__canvasSeeds)):
            self.__canvasSeeds[i] = self.__canvasSeeds[i] * scale
            newCell = []
            for j in range(len(self.__canvasCells[i])):
                newCell.append(self.__canvasCells[i][j] * scale)
            self.__canvasCells[i] = newCell

        self.__DirtySuperCell = True
        self.__DirtyBorderSegments = True

    def containsPoint(self, p: Vector2D) -> bool:
        poly = Polygon(self.superCellPointsAsList)
        return poly.contains(Point(p.asList)) or poly.intersects(Point(p.asList))

    def findDistanceToPoint(self, p: Vector2D) -> float:
        poly = Polygon(self.superCellPointsAsList)
        return abs(poly.exterior.distance(Point(p.asList)))

    def findDistanceToClosestBorderSegment(self, p: Vector2D) -> float:
        borderSegments = self.borderSegments
        distances = [s.getDistanceToPoint(p, lambda x, y: (x - y).length) for s in borderSegments]
        return min(distances)


# ======================================================================================================================

class PlanarEmbeddingMethod:
    def _calculateRawPositions(self, layoutSpec: AreaLayoutSpecification) -> dict:
        return {}

    def calculateEmbedding(self, layoutSpec: AreaLayoutSpecification, padding=0.1) -> dict:
        embedding = self._calculateRawPositions(layoutSpec)
        points = list(embedding.values())
        points_X = [p.X for p in points]
        points_Y = [p.Y for p in points]

        max_X = max(points_X)
        min_X = min(points_X)
        range_X = max_X - min_X

        max_Y = max(points_Y)
        min_Y = min(points_Y)
        range_Y = max_Y - min_Y

        # Normalizing in the range if [0,1] and applying padding
        for area in layoutSpec.areas:
            p = embedding[area]
            p.X = (p.X - min_X) / range_X
            p.X = padding + p.X * (1 - 2 * padding)
            p.Y = (p.Y - min_Y) / range_Y
            p.Y = padding + p.Y * (1 - 2 * padding)
            embedding[area] = p
        return embedding


class DefaultEmbedding(PlanarEmbeddingMethod):
    def __init__(self, iteration: int = 10000):
        self.__iteration = iteration

    def _calculateRawPositions(self, layoutSpec: AreaLayoutSpecification) -> dict:
        G = layoutSpec.networkxGraph

        if not nx.check_planarity(G):
            raise Exception("Given 'layout' is not planar.")
        else:

            # ugly planar layout
            # A Linear-time Algorithm for Drawing a Planar Graph on a Grid 1989
            # http://citeseerx.ist.psu.edu/viewdoc/summary?doi=10.1.1.51.6677
            initial_pos = nx.planar_layout(G, scale=len(layoutSpec))

            # expanding the ugly embedding and make it a bit more beautiful
            # Force-directed graph drawing
            # Fruchterman–Reingold algorithm
            pos = nx.spring_layout(G, pos=initial_pos, iterations=self.__iteration, scale=len(layoutSpec))

            def getEdge(connection, positions) -> Segment2D:
                a = connection[0]
                b = connection[1]
                pos_a = list(positions[a])
                pos_b = list(positions[b])
                return Segment2D(Vector2D_fromList(pos_a), Vector2D_fromList(pos_b))

            def isPlanar(positions) -> bool:
                for connection_1 in layoutSpec.neighbourhoods:
                    edge_1 = getEdge(connection_1, positions)
                    for connection_2 in layoutSpec.neighbourhoods:
                        if connection_1 != connection_2:
                            edge_2 = getEdge(connection_2, positions)
                            if edge_1.doesIntersect(edge_2):
                                return False
                return True

            while not isPlanar(pos):
                pos = nx.spring_layout(G, pos=pos, iterations=self.__iteration, scale=len(layoutSpec))

            embedding: Dict[string, Vector2D] = {}
            for area in layoutSpec.areas:
                embedding[area] = Vector2D_fromList(pos[area])
        return embedding


# ======================================================================================================================

class SkeletonGenerator:
    def generateSkeleton(self, embedding: dict, layoutSpec: AreaLayoutSpecification) -> List[AreaSkeleton]:
        pass


class StraightHalfEdgeSkeletonGenerator(SkeletonGenerator):
    def __init__(self, stretchWeights: dict):
        self.__stretchWeights = stretchWeights

    def generateSkeleton(self, embedding: dict, layoutSpec: AreaLayoutSpecification) -> List[AreaSkeleton]:
        skeletons: List[AreaSkeleton] = []
        for area in layoutSpec.areas:
            segments: List[Segment2D] = []
            for neighbour in layoutSpec.getNeighbours(area):
                try:
                    area_w = self.__stretchWeights[area]
                    neighbour_w = self.__stretchWeights[neighbour]

                    area_f = area_w / (area_w + neighbour_w)
                    neighbour_f = neighbour_w / (area_w + neighbour_w)
                except:
                    area_f = 0.5
                    neighbour_f = 0.5

                a = embedding[area]
                b = embedding[neighbour]*area_f + embedding[area]*neighbour_f
                segments.append(Segment2D(a, b))
            skeletons.append(AreaSkeleton(area, embedding[area], segments))
        return skeletons
