import matplotlib.pyplot as plt
import matplotlib.lines as mlines

from jahan.Landscape import NONE_ITEM_KEY
from jahan.Layout import *
from jahan.GridMap import *
from jahan.Canvas import *
from typing import Dict

# MISC. ================================================================================================================
from jahan.Toolbox import EMPTY_POLY

palette = \
    [
        "#e58e26", "#b71540", "#4a69bd", "#0a3d62", "#079992",
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


def creatMultiMapPlot(rows, cols):
    figure, axs = plt.subplots(nrows=rows, ncols=cols)
    axes = []
    if rows > 1:
        for j in range(cols):
            for i in range(rows):
                ax = axs[i][j]
                ax.axes.xaxis.set_visible(False)
                ax.axes.yaxis.set_visible(False)
                ax.set_aspect(1)
                axes.append(ax)
    else:
        for i in range(cols):
            ax = axs[i]
            ax.axes.xaxis.set_visible(False)
            ax.axes.yaxis.set_visible(False)
            ax.set_aspect(1)
            axes.append(ax)

    plt.ylim((0, 1))
    plt.xlim((0, 1))
    figure.tight_layout()
    return figure, axes


def addCircle(axes, center: Vector2D, radius: float, color=(0, 0, 0)):
    filled_circle = plt.Circle((center.X, center.Y), radius, color=color, zorder=currentOrder)
    axes.add_artist(filled_circle)
    axes.set_aspect(1)
    incrementOrder()


def addText(axes, center: Vector2D, inputText: string, color=(0, 0, 0), bold: bool = True, fontSize='large',
            bgColor=(0, 0, 0, 0.75), edgeColor=(0, 0, 0, 1), pad=0.3):
    formattedText = inputText
    if bold:
        formattedText: string = r"$\bf{T}$".format(T=inputText)

    textArtist = axes.text(center.X, center.Y,
                           formattedText,
                           color=color,
                           verticalalignment='center',
                           horizontalalignment='center',
                           zorder=currentOrder,
                           fontsize=fontSize,
                           fontstretch='condensed')

    textArtist.set_bbox(dict(pad=pad, facecolor=bgColor, edgecolor=edgeColor))

    axes.set_aspect(1)
    incrementOrder()


def addLine(axes, a: Vector2D, b: Vector2D, color=(0, 0, 0), width=1, style='-'):
    line = plt.Line2D([a.X, b.X], [a.Y, b.Y],
                      c=color, linewidth=width, linestyle=style, zorder=currentOrder)
    axes.add_artist(line)
    axes.set_aspect(1)
    incrementOrder()


def addFilledPolygon(axes, polygon: List[Vector2D], color=(0, 0, 0)):
    points = list(map(lambda v: v.asList, polygon))
    poly = plt.Polygon(points, closed=True, color=color, fill=False, zorder=currentOrder)
    axes.add_artist(poly)
    axes.set_aspect(1)
    incrementOrder()


def addOutlinePolygon(axes, polygon: List[Vector2D], outlineColor=(0, 0, 0), fillColor=(0, 0, 0)):
    points = list(map(lambda v: v.asList, polygon))
    poly = plt.Polygon(points,
                       closed=True,
                       edgecolor=outlineColor,
                       facecolor=fillColor,
                       zorder=currentOrder)
    axes.add_artist(poly)
    axes.set_aspect(1)
    incrementOrder()


def addSegmentList(axes, segments: List[Segment2D], color=(0, 0, 0), width=1, style='-'):
    for segment in segments:
        addLine(axes, segment.start, segment.end, color, width, style)


def addCanvas(axes, canvas: Canvas2D,
              drawCells: bool = True,
              drawNeighbours: bool = False,
              pointColor=(0, 0, 0, 1),
              neighbourColor=(1, 0, 0, 1)):
    for point in canvas.Seeds:
        if drawNeighbours:
            neighbours = canvas.getNeighboursOfSeed(point)
            for n in neighbours:
                addLine(axes, point, n, neighbourColor, style='--')

        addCircle(axes, point, 0.005, pointColor)

    if drawCells:
        for s in canvas.voronoiSegments:
            addLine(axes, s.start, s.end, pointColor)


def createColoringSchemeForAreaLayout(layout: AreaLayoutSpecification) -> dict:
    scheme = {}
    for index in range(len(layout)):
        scheme[layout.areas[index]] = getColorFormPalette(index)
    scheme[EMPTY_POLY] = (0, 0, 0, 0)
    return scheme


def addAreaLayoutGraph(axes, layout: AreaLayoutSpecification, embedding, drawNeighbourhoods: bool = True):
    color = (0, 0, 0, 0.75)

    if drawNeighbourhoods:
        for edge in layout.neighbourhoods:
            addLine(axes, embedding[edge[0]], embedding[edge[1]], color, 2)

    # for area in layout.areas:
    #     addCircle(axes, embedding[area], size, color)

    for area in layout.areas:
        addText(axes, embedding[area], area, (1, 1, 1), pad=0.8, fontSize="large")


def addSingleAreaSkeleton(axes, skeleton: AreaSkeleton, color=(1, 0, 0)):
    for seg in skeleton.segments:
        addLine(axes, seg.start, seg.end - seg.normal * 0.02, color, 5)

    addCircle(axes, skeleton.root, 0.04, color)


def addAreaSkeletonsText(axes, skeleton: AreaSkeleton):
    textColor = (1, 1, 1, 0.75)
    addText(axes, skeleton.root, skeleton.areaName, textColor)


def addMultipleAreaSkeletons(axes, skeletons: List[AreaSkeleton], coloring: dict):
    for skeleton in skeletons:
        addSingleAreaSkeleton(axes, skeleton, coloring[skeleton.areaName])

    for skeleton in skeletons:
        addAreaSkeletonsText(axes, skeleton)


def addAreaPolygon(axes, polygon: AreaPolygon,
                   color=(1, 0, 0),
                   drawSeeds: bool = False,
                   drawCells: bool = False):
    bColor = BrightenColor(color, 0.75)

    if drawCells:
        for poly in polygon.cells:
            addOutlinePolygon(axes, poly, color, bColor)

    if drawSeeds:
        for seed in polygon.seeds:
            addCircle(axes, seed, 0.005, color)

    addSegmentList(axes, polygon.superCellSegments, (0.1, 0.1, 0.1), width=2)


def addMultiAreaPolygons(axes,
                         polygons: Dict[str, AreaPolygon],
                         coloring,
                         drawSeeds: bool = True,
                         drawCells: bool = True):
    for area in polygons.keys():
        if area != EMPTY_POLY:

            if coloring is None:
                color = (0.75, 0.75, 0.75)
            else:
                color = coloring[area]

            addAreaPolygon(axes,
                           polygons[area],
                           color,
                           drawSeeds, drawCells)


def addSingleMap(axes, gridMap: GridMap, colorMap, contour: bool = False, colorBar: bool = False):
    image = plt.imshow(gridMap.asListOfListsForImShow,
                       aspect='auto',
                       extent=[0, 1, 0, 1],
                       cmap=colorMap,
                       zorder=currentOrder)
    axes.add_artist(image)
    axes.set_aspect(1)
    incrementOrder()

    w = gridMap.width
    h = gridMap.height

    if contour:
        x = [coord / w for coord in range(w)]
        y = [coord / h for coord in range(h)]
        X, Y = np.meshgrid(x, y)
        heightValues = gridMap.exportForContour()
        Z = np.array(heightValues)
        Z = Z.reshape(gridMap.height, gridMap.width)

        axes.contour(X, Y, Z,
                     colors=[(0, 0, 0, 0.75)],
                     linewidths=1,
                     zorder=currentOrder)

        incrementOrder()

    if colorBar:
        colorBar = plt.colorbar(image, shrink=0.5, orientation='vertical', pad=0.05)
        colorBar.ax.tick_params(labelsize=16)


def calcInfluenceColor(row: int, col: int, maps: Dict, coloring: Dict):
    r = 0.0
    g = 0.0
    b = 0.0

    for key in coloring.keys():
        if key in maps.keys():
            inf = maps[key].getValue(row, col)
            r = r + coloring[key][0] * inf
            g = g + coloring[key][1] * inf
            b = b + coloring[key][2] * inf

    return r, g, b


def AddMultipleMaps(axes, maps: Dict, coloring: Dict, legend: bool = True):
    colors = []
    w = (list(maps.values()))[0].width
    h = (list(maps.values()))[0].height
    for y in range(h):
        colors.append([])
        for x in range(w):
            colors[y].append(calcInfluenceColor(x, h - y - 1, maps, coloring))

    image = plt.imshow(colors,
                       aspect='auto',
                       extent=[0, 1, 0, 1])
    axes.add_artist(image)
    axes.set_aspect(1)
    incrementOrder()

    if legend:
        handles = []
        for key in coloring.keys():
            if not (key in ["NONE", EMPTY_POLY]):
                handle = mlines.Line2D([],
                                       [],
                                       color=coloring[key],
                                       marker="s",
                                       linestyle='None',
                                       markersize=10,
                                       label=key)
                handles.append(handle)

        plt.legend(handles=handles, bbox_to_anchor=(1.01, 1.02), loc='upper left')


def addLocationSign(axes, loc, marker, color):
    plt.plot(loc[0], loc[1], marker=marker, color=color, markersize=6, zorder=currentOrder)
    axes.set_aspect(1)
    incrementOrder()


def addSingleLocationList(axes, locations: list, color, marker, mapWidth: float, mapHeight: float):
    for loc in locations:
        loc[0] = loc[0] / mapWidth
        loc[1] = loc[1] / mapHeight
        addLocationSign(axes, loc, marker, color)


def addDictionaryOfLocations(axes, locationLists: dict, coloring, mapWidth: float, mapHeight: float):
    handles = []
    for key in locationLists.keys():
        if key != NONE_ITEM_KEY:
            addSingleLocationList(axes, locationLists[key], coloring[key][0], coloring[key][1], mapWidth, mapHeight)

            if not (key in ["NONE", EMPTY_POLY]):
                handle = mlines.Line2D([],
                                       [],
                                       color=coloring[key][0],
                                       marker=coloring[key][1],
                                       linestyle='None',
                                       markersize=10,
                                       label=key)
                handles.append(handle)

    plt.legend(handles=handles, bbox_to_anchor=(1.01, 1.02), loc='upper left')


def showMap(title: string):
    plt.title(title)
    plt.tight_layout()
    plt.show()


def showMultiMap(titles: list, axs):
    for i in range(len(axs)):
        if i < len(titles):
            axs[i].title.set_text(titles[i])
        else:
            axs[i].set_visible(False)

    plt.tight_layout()
    plt.show()


def addDictionaryOfLabeledLocations(axes, labeledLocations: dict, w: float, h: float):
    for label in labeledLocations.keys():
        loc = labeledLocations[label]
        loc.X = loc.X / w
        loc.Y = loc.Y / h

        addText(axes, loc, label, (1, 1, 1), True, 'medium', (0, 0, 0, 0.8), (1, 0, 0))


def showHeightMap(m: GridMap):
    fig = plt.figure(figsize=(8.0, 8.0), dpi=100)
    ax = fig.add_subplot(projection='3d')
    ax.view_init(60, 60)

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

    plt.tight_layout()
    plt.show()
