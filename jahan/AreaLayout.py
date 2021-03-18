import string
from typing import List, Tuple


class AreaLayout:
    _areas: List[string] = []
    _neighbourhoods: List[Tuple[string]] = []

    def addArea(self, name: string):
        if not name in self._areas:
            self._areas.append(name)

    def connectAreas(self, a: string, b: string):
        if (a in self._areas) and (b in self._areas) and (not (a, b) in self._neighbourhoods):
            self._neighbourhoods.append((a, b))

    def hasArea(self, name: string):
        return name in self._areas

    def hasNeighbourhood(self, a: string, b: string):
        return (a, b) in self._neighbourhoods
