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


def getColorFormPalette(index):
    h = palette[index % len(palette)]
    h = h.lstrip('#')
    rgb = tuple(int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))
    return rgb


def BrightenColor(color):
    return color[0] * 0.5 + 0.5, color[1] * 0.5 + 0.5, color[2] * 0.5 + 0.5


def creatMapPlot():
    figure, axes = plt.subplots()
    return figure, axes


def addCircle(axes, center: Vector2D, radius: float, color=(0, 0, 0)):
    filled_circle = plt.Circle((center.X, center.Y), radius, color=color)
    axes.set_aspect(1)
    axes.add_artist(filled_circle)


def addText(axes, center: Vector2D, text: string, color=(0, 0, 0), bold: bool = True):
    formattedText = text
    if bold:
        formattedText: string = r"$\bf{T}$".format(T=text)
    text = plt.text(center.X, center.Y,
                    formattedText,
                    color=color,
                    verticalalignment='center',
                    horizontalalignment='center')

    axes.set_aspect(1)
    axes.add_artist(text)


def addLine(axes, a: Vector2D, b: Vector2D, color=(0, 0, 0), width=1):
    plt.plot([a.X, b.X], [a.Y, b.Y], c=color, linewidth=width)
    axes.set_aspect(1)


def addCanvas(axes, canvas: Canvas2D):
    for point in canvas.points:
        addCircle(axes, point, 0.005, (0.8, 0.8, 0.8))


def createColoringSchemeForAreaLayout(layout: AreaLayout) -> Dict:
    scheme: Dict = {}
    for index in range(len(layout)):
        scheme[layout.areas[index]] = getColorFormPalette(index)
    return scheme


def addLayoutGraph(axes, layout: AreaLayout, embedding):
    color = (0.5, 0.5, 1)
    for edge in layout.neighbourhoods:
        addLine(axes, embedding[edge[0]], embedding[edge[1]], color, 2)

    for area in layout.areas:
        addCircle(axes, embedding[area], 0.02, color)
        addText(axes, embedding[area], area, (0, 0, 0))


def addAreaSkeletons(axes, skeleton: AreaSkeleton, color=(1, 0, 0)):
    addCircle(axes, skeleton.root, 0.03, color)

    textColor = (0, 0, 0)
    addText(axes, skeleton.root, skeleton.areaName, textColor)

    for seg in skeleton.segments:
        addLine(axes, seg.start, seg.end, color, 6)


def addAreaSkeletonsList(axes, skeletons: List[AreaSkeleton], coloring: Dict):
    for skeleton in skeletons:
        addAreaSkeletons(axes, skeleton, coloring[skeleton.areaName])


def addAreaPartition(axes, partition: AreaPartition, color=(1, 0, 0)):
    for p in partition.partitionPoints:
        addCircle(axes, p, 0.01, color)


def addAreaPartitionDict(axes, partitions: Dict[str, AreaPartition], coloring: Dict):
    for area in partitions.keys():
        addAreaPartition(axes, partitions[area], BrightenColor(coloring[area]))


def showMapPlot(title: string):
    plt.ylim((0, 1))
    plt.xlim((0, 1))
    plt.title(title)
    plt.show()
