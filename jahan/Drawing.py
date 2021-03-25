import matplotlib.pyplot as plt
from typing import Dict
from jahan.AreaClasses import *

palette = \
    [
        "#e58e26", "#b71540", "#4a69bd", "#0a3d62", "#079992",
        "#fad390", "#f8c291", "#6a89cc", "#82ccdd", "#b8e994",
        "#f6b93b", "#e55039", "#0c2461", "#60a3bc", "#78e08f",
        "#fa983a", "#eb2f06", "#1e3799", "#3c6382", "#38ada9"
    ]

currentOrder = 0


def incrementOrder():
    global currentOrder
    currentOrder = currentOrder + 1


def getColorFormPalette(index):
    h = palette[index % len(palette)]
    h = h.lstrip('#')
    rgb = tuple(int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))
    return rgb


def BrightenColor(color, preserve=0.8):
    brightUp = 1 - preserve
    return color[0] * preserve + brightUp, \
           color[1] * preserve + brightUp, \
           color[2] * preserve + brightUp


def creatMapPlot():
    figure, axes = plt.subplots()
    return figure, axes


def addCircle(axes, center: Vector2D, radius: float, color=(0, 0, 0)):
    filled_circle = plt.Circle((center.X, center.Y), radius, color=color, zorder=currentOrder)
    axes.set_aspect(1)
    axes.add_artist(filled_circle)
    incrementOrder()


def addText(axes, center: Vector2D, text: string, color=(0, 0, 0), bold: bool = True):
    formattedText = text
    if bold:
        formattedText: string = r"$\bf{T}$".format(T=text)
    text = plt.text(center.X, center.Y,
                    formattedText,
                    color=color,
                    verticalalignment='center',
                    horizontalalignment='center',
                    zorder=currentOrder)

    axes.set_aspect(1)
    axes.add_artist(text)
    incrementOrder()


def addLine(axes, a: Vector2D, b: Vector2D, color=(0, 0, 0), width=1, style='-'):
    line = plt.Line2D([a.X, b.X], [a.Y, b.Y],
                      c=color, linewidth=width, linestyle=style, zorder=currentOrder)
    axes.set_aspect(1)
    axes.add_artist(line)
    incrementOrder()


def addFilledPolygon(axes, polygon: List[Vector2D], color=(0, 0, 0)):
    points = list(map(lambda v: v.asList, polygon))
    poly = plt.Polygon(points, closed=True, color=color, fill=False, zorder=currentOrder)
    axes.set_aspect(1)
    axes.add_artist(poly)
    incrementOrder()


def addOutlinePolygon(axes, polygon: List[Vector2D], outlineColor=(0, 0, 0), fillColor=(0, 0, 0)):
    points = list(map(lambda v: v.asList, polygon))
    poly = plt.Polygon(points,
                       closed=True,
                       edgecolor=outlineColor,
                       facecolor=fillColor,
                       zorder=currentOrder)
    axes.set_aspect(1)
    axes.add_artist(poly)
    incrementOrder()


def addSegmentList(axes, segments: List[Segment2D], color=(0, 0, 0), width=1, style='-'):
    for segment in segments:
        addLine(axes, segment.start, segment.end, color, width, style)


def addCanvas(axes, canvas: Canvas2D, drawCells: bool = True, drawNeighbours: bool = False):
    pointColor = (0.8, 0.8, 0.8)
    neighbourColor = (0.8, 0.6, 0.6)
    for point in canvas.Seeds:
        if drawNeighbours:
            neighbours = canvas.getNeighboursOfSeed(point)
            for n in neighbours:
                addLine(axes, point, n, neighbourColor, style='--')

        addCircle(axes, point, 0.005, pointColor)

    if drawCells:
        for s in canvas.voronoiSegments:
            addLine(axes, s.start, s.end, pointColor)


def createColoringSchemeForAreaLayout(layout: AreaLayout) -> Dict:
    scheme: Dict = {}
    for index in range(len(layout)):
        scheme[layout.areas[index]] = getColorFormPalette(index)
    return scheme


def addAreaLayoutGraph(axes, layout: AreaLayout, embedding):
    color = (0.5, 0.5, 1)
    for edge in layout.neighbourhoods:
        addLine(axes, embedding[edge[0]], embedding[edge[1]], color, 2)

    for area in layout.areas:
        addCircle(axes, embedding[area], 0.02, color)

    for area in layout.areas:
        addText(axes, embedding[area], area, (0, 0, 0))


def addAreaSkeleton(axes, skeleton: AreaSkeleton, color=(1, 0, 0)):
    for seg in skeleton.segments:
        addLine(axes, seg.start, seg.end, color, 3)

    addCircle(axes, skeleton.root, 0.03, color)


def addAreaSkeletonsText(axes, skeleton: AreaSkeleton):
    textColor = (0, 0, 0)
    addText(axes, skeleton.root, skeleton.areaName, textColor)


def addAreaSkeletonsList(axes, skeletons: List[AreaSkeleton], coloring: Dict):
    for skeleton in skeletons:
        addAreaSkeleton(axes, skeleton, coloring[skeleton.areaName])

    for skeleton in skeletons:
        addAreaSkeletonsText(axes, skeleton)


def addAreaPartition(axes, partition: AreaPartition,
                     color=(1, 0, 0),
                     drawSeeds: bool = False,
                     drawCells: bool = False):
    bColor = BrightenColor(color, 0.5)

    for poly in partition.cells:
        addOutlinePolygon(axes, poly, (0.1, 0.1, 0.1), (0.1, 0.1, 0.1))
    addSegmentList(axes, partition.superCellSegments, (0.75, 0.75, 0.75), width=2)

    if drawCells:
        for poly in partition.cells:
            addOutlinePolygon(axes, poly, color, bColor)

    if drawSeeds:
        for seed in partition.seeds:
            addCircle(axes, seed, 0.01, color)


def addAreaPartitionDict(axes,
                         partitions: Dict[str, AreaPartition],
                         coloring: Dict,
                         drawSeeds: bool = True,
                         drawCells: bool = True):
    for area in partitions.keys():
        addAreaPartition(axes,
                         partitions[area],
                         coloring[area],
                         drawSeeds, drawCells)


def showMapPlot(title: string):
    plt.ylim((0, 1))
    plt.xlim((0, 1))
    plt.title(title)
    plt.show()
