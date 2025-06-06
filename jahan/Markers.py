import string
from copy import deepcopy

from jahan.GridMap import GridMap
from jahan.Layout import AreaPolygon
from jahan.VectorArithmetic import Vector2D
import numpy as np


class MarkerSpecification:
    def __init__(self, name: string,
                 containerArea: string,
                 heightPreference: float,
                 heightImportance: float,
                 centerPreference: float,
                 centerImportance: float,
                 effectorAreas: list,
                 effectorImportance: float):

        if effectorAreas is None:
            effectorAreas = {}

        self.__name = name
        self.__containerArea = containerArea
        self.__heightPref = heightPreference
        self.__heightImp = heightImportance
        self.__centerPref = centerPreference
        self.__centerImp = centerImportance
        self.__effectorAreas = effectorAreas
        self.__effectorImp = effectorImportance

    @property
    def name(self):
        return self.__name

    @property
    def containingArea(self):
        return self.__containerArea

    @property
    def heightPreference(self):
        return self.__heightPref

    def placeMarker(self,
                    polygons: dict,
                    heightMap: GridMap):

        if not (self.__containerArea in polygons.keys()):
            raise Exception("{} is not among given polygons".format(self.__containerArea))

        heightMap = deepcopy(heightMap)

        w = heightMap.width
        h = heightMap.height

        polygons = deepcopy(polygons)
        for area in polygons.keys():
            polygons[area].scalePolygon(w, h)

        container_polygon: AreaPolygon = polygons[self.__containerArea]

        candidates = container_polygon.seeds
        center_of_mass: Vector2D = container_polygon.centerOfMass

        heights = [heightMap.getValue(c.X, c.Y) for c in candidates]
        min_H = np.nanmin(heights)
        max_H = np.nanmax(heights)
        range_H = max_H - min_H
        if range_H == 0:
            H_penalty = [0.0] * len(candidates)
        else:
            desired_H = min_H + range_H * self.__heightPref
            H_penalty = [abs((h - desired_H)) / range_H for h in heights]

        distances = [(c - center_of_mass).length for c in candidates]
        min_D = np.nanmin(distances)
        max_D = np.nanmax(distances)
        range_D = max_D - min_D
        if range_D == 0:
            D_penalty = [0.0] * len(candidates)
        else:
            desired_D = min_D + range_D * (1 - self.__centerPref)
            D_penalty = [abs((d - desired_D)) / range_D for d in distances]

        def DistanceSum(c: Vector2D):

            if len(self.__effectorAreas) == 0:
                return 0.0

            dist = 0.0
            for areaName in self.__effectorAreas:
                dist = dist + polygons[areaName].findDistanceToPoint(c)
            return dist

        tendencies = [DistanceSum(c) for c in candidates]
        min_T = np.nanmin(tendencies)
        max_T = np.nanmax(tendencies)
        range_T = max_T - min_T
        if range_T == 0:
            T_penalty = [0.0] * len(candidates)
        else:
            T_penalty = [(t - min_T) / range_T for t in tendencies]

        penalties = [self.__heightImp * H_penalty[i] +
                     self.__centerImp * D_penalty[i] +
                     self.__effectorImp * T_penalty[i]
                     for i in range(len(candidates))]
        min_penalty = np.nanmin(penalties)
        index = penalties.index(min_penalty)

        return candidates[index]
