import matplotlib.pyplot as plt
from jahan.AreaClasses import *
from jahan.MapClasses import *
from typing import Dict

# MISC. ================================================================================================================

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


# ======================================================================================================================

def creatMapPlot():
    figure, axes = plt.subplots()
    axes.axes.xaxis.set_visible(False)
    axes.axes.yaxis.set_visible(False)
    plt.ylim((0, 1))
    plt.xlim((0, 1))
    axes.set_aspect(1)
    return figure, axes


def addCircle(axes, center: Vector2D, radius: float, color=(0, 0, 0)):
    filled_circle = plt.Circle((center.X, center.Y), radius, color=color, zorder=currentOrder)
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

    axes.add_artist(text)
    incrementOrder()


def addLine(axes, a: Vector2D, b: Vector2D, color=(0, 0, 0), width=1, style='-'):
    line = plt.Line2D([a.X, b.X], [a.Y, b.Y],
                      c=color, linewidth=width, linestyle=style, zorder=currentOrder)
    axes.add_artist(line)
    incrementOrder()


def addFilledPolygon(axes, polygon: List[Vector2D], color=(0, 0, 0)):
    points = list(map(lambda v: v.asList, polygon))
    poly = plt.Polygon(points, closed=True, color=color, fill=False, zorder=currentOrder)
    axes.add_artist(poly)
    incrementOrder()


def addOutlinePolygon(axes, polygon: List[Vector2D], outlineColor=(0, 0, 0), fillColor=(0, 0, 0)):
    points = list(map(lambda v: v.asList, polygon))
    poly = plt.Polygon(points,
                       closed=True,
                       edgecolor=outlineColor,
                       facecolor=fillColor,
                       zorder=currentOrder)
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


def createColoringSchemeForAreaLayout(layout: AreaLayout) -> dict:
    scheme = {}
    for index in range(len(layout)):
        scheme[layout.areas[index]] = getColorFormPalette(index)
    return scheme


def addAreaLayoutGraph(axes, layout: AreaLayout, embedding, drawNeighbourhoods: bool = True):
    color = (0, 0, 0, 1)

    if drawNeighbourhoods:
        for edge in layout.neighbourhoods:
            addLine(axes, embedding[edge[0]], embedding[edge[1]], color, 2)

    for area in layout.areas:
        addCircle(axes, embedding[area], 0.03, color)

    for area in layout.areas:
        addText(axes, embedding[area], area, (1, 1, 1))


def addSingleAreaSkeleton(axes, skeleton: AreaSkeleton, color=(1, 0, 0)):
    for seg in skeleton.segments:
        addLine(axes, seg.start, seg.end, color, 3)

    addCircle(axes, skeleton.root, 0.03, color)


def addAreaSkeletonsText(axes, skeleton: AreaSkeleton):
    textColor = (0, 0, 0)
    addText(axes, skeleton.root, skeleton.areaName, textColor)


def addMultipleAreaSkeletons(axes, skeletons: List[AreaSkeleton], coloring: dict):
    for skeleton in skeletons:
        addSingleAreaSkeleton(axes, skeleton, coloring[skeleton.areaName])

    for skeleton in skeletons:
        addAreaSkeletonsText(axes, skeleton)


def addAreaPartition(axes, partition: AreaPartition,
                     color=(1, 0, 0),
                     drawSeeds: bool = False,
                     drawCells: bool = False):
    bColor = BrightenColor(color, 0.5)

    # addOutlinePolygon(axes, partition.superCellPoints, (0.1, 0.1, 0.1), (0.1, 0.1, 0.1))
    addSegmentList(axes, partition.superCellSegments, (0.1, 0.1, 0.1), width=2)

    if drawCells:
        for poly in partition.cells:
            addOutlinePolygon(axes, poly, color, bColor)

    if drawSeeds:
        for seed in partition.seeds:
            addCircle(axes, seed, 0.01, color)


def addMultiAreaPartitions(axes,
                           partitions: Dict[str, AreaPartition],
                           coloring: Dict,
                           drawSeeds: bool = True,
                           drawCells: bool = True):
    for area in partitions.keys():
        addAreaPartition(axes,
                         partitions[area],
                         coloring[area],
                         drawSeeds, drawCells)


def addSingleMap(axes, gridMap: GridMap, colorMap):
    image = plt.imshow(gridMap.asListOfListsForImShow,
                       aspect='auto',
                       extent=[0, 1, 0, 1],
                       cmap=colorMap)
    axes.add_artist(image)
    incrementOrder()


def calcInfluenceColor(row: int, col: int, maps: Dict, coloring: Dict):
    r = 0.0
    g = 0.0
    b = 0.0

    for key in coloring.keys():
        inf = maps[key].getValue(row, col)
        r = r + coloring[key][0] * inf
        g = g + coloring[key][1] * inf
        b = b + coloring[key][2] * inf

    return r, g, b


def AddMultipleMaps(axes, influenceMap: Dict, coloring: Dict):
    colors = []
    w = (list(influenceMap.values()))[0].width
    h = (list(influenceMap.values()))[0].height
    for row in range(h):
        colors.append([])
        for col in range(w):
            colors[row].append(calcInfluenceColor(col, h - row - 1, influenceMap, coloring))

    image = plt.imshow(colors,
                       aspect='auto',
                       extent=[0, 1, 0, 1])
    axes.add_artist(image)
    incrementOrder()


def addSingleLocationList(axes, locations: list, color, w: float, h: float):
    for loc in locations:
        loc[0] = loc[0] / h
        loc[1] = loc[1] / w
        addCircle(axes, Vector2D_fromList(loc), 0.002, color)


def addDictionaryOfLocations(axes, locationLists: dict, coloring, w: float, h: float):
    for k in locationLists.keys():
        addSingleLocationList(axes, locationLists[k], coloring[k], w, h)


def showMap(title: string):
    plt.title(title)
    plt.show()


def showHeightMap(m: GridMap):
    fig = plt.figure(figsize=(8.0, 8.0), dpi=100)
    ax = fig.add_subplot(projection='3d')
    ax.view_init(90, 0)

    ax.xaxis.set_pane_color((0, 0, 0, 0))
    ax.yaxis.set_pane_color((0, 0, 0, 0))
    ax.zaxis.set_pane_color((0, 0, 0, 0))

    ax.xaxis._axinfo["grid"]['color'] = (1, 1, 1, 0)
    ax.yaxis._axinfo["grid"]['color'] = (1, 1, 1, 0)
    ax.zaxis._axinfo["grid"]['color'] = (1, 1, 1, 0)

    ax.tick_params(axis='both', which='major', labelcolor=(0, 0, 0, 0))
    ax.tick_params(axis='both', which='minor', labelcolor=(0, 0, 0, 0))

    plt.locator_params(nbins=24)

    x = range(m.width)
    y = range(m.height)
    X, Y = np.meshgrid(x, y)
    heightValues = m.exportFor3DPlotting()
    Z = np.array(heightValues)
    Z = Z.reshape(m.height, m.width)

    limits = max(m.width - 1, m.height - 1)
    ax.set_xlim3d(0, limits)
    ax.set_ylim3d(0, limits)
    ax.set_zlim3d(0, limits)

    minH = np.nanmin(heightValues)
    maxH = np.nanmax(heightValues)

    surface = ax.plot_surface(X, Y, Z,
                              rstride=1,
                              cstride=1,
                              cmap='gist_earth',
                              linewidth=0.0,
                              antialiased=False, vmin=minH,
                              vmax=maxH)

    colorBar = fig.colorbar(surface, shrink=0.5, orientation='vertical', pad=0.05)
    colorBar.ax.tick_params(labelsize=16)

    ax.contour(X, Y, Z,
               colors=[(1, 1, 1, 0.35)],
               linewidths=1)

    plt.show()
