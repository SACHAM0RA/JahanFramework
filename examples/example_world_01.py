import jahan.JahanToolbox as jtb
import jahan.Drawing as jDraw
from jahan.AreaClasses import *

#canvas = jtb.squareGridCanvasGenerator(25, 25)
canvas = jtb.looseSquareGridCanvasGenerator(25, 25, 0.5)
#canvas = jtb.hexagonGridCanvasGenerator(25, 25)
#canvas = jtb.randomCanvasGenerator(625)
#canvas = jtb.circularCanvasGenerator(0.05, 100)

layout = AreaLayout()
layout.addArea("A")
layout.addArea("B")
layout.addArea("C")
layout.addArea("D")
layout.addArea("E")
layout.addArea("F")
layout.addArea("G")
layout.addArea("H")
layout.addArea("I")
layout.addArea("J")
layout.addArea("K")
layout.addArea("L")
layout.connectAreas("A", "B")
layout.connectAreas("A", "C")
layout.connectAreas("B", "C")
layout.connectAreas("D", "E")
layout.connectAreas("B", "D")
layout.connectAreas("E", "C")
layout.connectAreas("E", "F")
layout.connectAreas("B", "G")
layout.connectAreas("B", "H")
layout.connectAreas("H", "F")
layout.connectAreas("G", "I")
layout.connectAreas("G", "H")
layout.connectAreas("F", "J")
layout.connectAreas("K", "L")
layout.connectAreas("K", "E")
layout.connectAreas("L", "C")

embedding = jtb.defaultPlanarEmbedding(layout, 0.1)

skeletons = jtb.generateAreaSkeletonsFromHalfEdges(layout, embedding)

partitions = jtb.partitionCanvasByAreaSkeletons(canvas, layout, skeletons, jtb.euclideanDistance)

figure, axes = jDraw.creatMapPlot()
layoutColoring = jDraw.createColoringSchemeForAreaLayout(layout)

jDraw.addCanvas(axes, canvas, drawCells=True, drawNeighbours=False)
#jDraw.addAreaLayoutGraph(axes, layout, embedding)
jDraw.addAreaPartitionDict(axes, partitions, layoutColoring,
                           drawSeeds=False, drawCells=False)
#jDraw.addAreaSkeletonsList(axes, skeletons, layoutColoring)
jDraw.showMapPlot("PLOT")
