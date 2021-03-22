import jahan.JahanToolbox as jtb
import jahan.Drawing as jDraw
from jahan.AreaClasses import *

canvas = jtb.squareGridCanvasGenerator(30, 30)

layout = AreaLayout()
layout.addArea("A")
layout.addArea("B")
layout.addArea("C")
layout.addArea("D")
layout.addArea("E")
layout.addArea("F")
layout.connectAreas("A", "B")
layout.connectAreas("A", "C")
layout.connectAreas("B", "C")
layout.connectAreas("D", "E")
layout.connectAreas("B", "D")
layout.connectAreas("E", "C")
layout.connectAreas("E", "F")
layout.connectAreas("C", "F")

embedding = jtb.defaultPlanarEmbedding(layout, 0.2)

skeletons = jtb.generateAreaSkeletonsFromHalfEdges(layout, embedding)

partitions = jtb.partitionCanvasByAreaSkeletons(canvas, skeletons, jtb.euclideanDistance)

figure, axes = jDraw.creatMapPlot()
coloring = jDraw.createColoringSchemeForAreaLayout(layout)

#jDraw.addCanvas(axes, canvas)
#jDraw.addLayoutGraph(axes, layout, embedding)
#jDraw.addAreaSkeletonsList(axes, skeletons, coloring)
jDraw.addAreaPartitionDict(axes, partitions, coloring)
jDraw.showMapPlot("PLOT")
