import jahan.Toolbox as tbx
import jahan.Layout as lyt
import jahan.Drawing as jDraw
import jahan.Canvas as cnv

layoutSpec = lyt.AreaLayoutSpecification()
layoutSpec.addArea("A")
layoutSpec.addArea("B")
layoutSpec.addArea("C")
layoutSpec.addArea("D")
layoutSpec.addArea("E")
layoutSpec.addArea("F")
layoutSpec.addArea("G")
layoutSpec.addArea("H")
layoutSpec.addArea("I")
layoutSpec.addArea("J")
layoutSpec.addArea("K")
layoutSpec.addArea("L")
layoutSpec.connectAreas("A", "C")
layoutSpec.connectAreas("B", "C")
layoutSpec.connectAreas("E", "C")
layoutSpec.connectAreas("E", "F")
layoutSpec.connectAreas("H", "F")
layoutSpec.connectAreas("G", "I")
layoutSpec.connectAreas("G", "H")
layoutSpec.connectAreas("K", "L")
layoutSpec.connectAreas("K", "E")
layoutSpec.connectAreas("L", "C")
layoutSpec.connectAreas("H", "C")

figure, axs = jDraw.creatMultiMapPlot(1, 2)

stretchWeights = {"A": 1,
                  "B": 1,
                  "C": 1,
                  "D": 1,
                  "E": 1,
                  "F": 1,
                  "G": 1,
                  "H": 1,
                  "I": 1,
                  "J": 1,
                  "K": 1,
                  "L": 1}

embedding, skeletons = \
    tbx.generateLayoutSkeletons(layoutSpec=layoutSpec,
                                embeddingMethod=lyt.DefaultEmbedding(),
                                skeletonGenerator=lyt.StraightHalfEdgeSkeletonGenerator(stretchWeights))

jDraw.addAreaLayoutGraph(axs[0], layoutSpec, embedding, drawNeighbourhoods=True)
layoutColoring = jDraw.createColoringSchemeForAreaLayout(layoutSpec)
jDraw.addMultipleAreaSkeletons(axs[1], skeletons, layoutColoring)

jDraw.showMultiMap(["PLANAR EMBEDDING", "AREA SKELETONS"], axs)

squareSeeds = cnv.SquareCanvasSeedGenerator(20, 20).generate()
hexSeeds = cnv.HexagonCanvasSeedGenerator(20, 20).generate()
radialSeeds = cnv.RadialCanvasSeedGenerator(0.1, 75).generate()
loosSeeds = cnv.LooseSquareCanvasSeedGenerator(20, 20, 0.33).generate()
randSeeds = cnv.UniformRandomCanvasSeedGenerator(200).generate()
canvas = cnv.Canvas2D(loosSeeds)

boundRadiusValues = {"A": 1,
                     "B": 1,
                     "C": 1,
                     "D": 1,
                     "E": 1,
                     "F": 1,
                     "G": 1,
                     "H": 1,
                     "I": 1,
                     "J": 1,
                     "K": 1,
                     "L": 1}

polygons_ecu = tbx.GeneratePolygonsFromAreaSkeletons(canvas=canvas,
                                                     layoutSpec=layoutSpec,
                                                     skeletons=skeletons,
                                                     BoundRadiusValues=boundRadiusValues,
                                                     distanceFunction=tbx.EuclideanDistanceCalculator())

polygons_man = tbx.GeneratePolygonsFromAreaSkeletons(canvas=canvas,
                                                     layoutSpec=layoutSpec,
                                                     skeletons=skeletons,
                                                     BoundRadiusValues=boundRadiusValues,
                                                     distanceFunction=tbx.ManhattanDistanceCalculator())

polygons_che = tbx.GeneratePolygonsFromAreaSkeletons(canvas=canvas,
                                                     layoutSpec=layoutSpec,
                                                     skeletons=skeletons,
                                                     BoundRadiusValues=boundRadiusValues,
                                                     distanceFunction=tbx.ChebyshevDistanceCalculator())
polygons = polygons_ecu

_, axes = jDraw.creatMapPlot()
jDraw.addAreaLayoutGraph(axes, layoutSpec, embedding, drawNeighbourhoods=True)
jDraw.showMap("PLANAR EMBEDDING")

_, axes = jDraw.creatMapPlot()
jDraw.addMultipleAreaSkeletons(axes, skeletons, layoutColoring)
jDraw.showMap("AREA SKELETONS")

_, axes = jDraw.creatMapPlot()
jDraw.addCanvas(axes, canvas, drawCells=True, drawNeighbours=False, pointColor=(0, 0, 0, 0.25))
jDraw.addMultiAreaPolygons(axes, polygons_ecu, layoutColoring, drawSeeds=True, drawCells=True)
jDraw.addAreaLayoutGraph(axes, layoutSpec, embedding, drawNeighbourhoods=True)
jDraw.showMap("EUCLIDEAN DISTANCE")

_, axes = jDraw.creatMapPlot()
jDraw.addCanvas(axes, canvas, drawCells=True, drawNeighbours=False, pointColor=(0, 0, 0, 0.25))
jDraw.addMultiAreaPolygons(axes, polygons_man, layoutColoring, drawSeeds=True, drawCells=True)
jDraw.addAreaLayoutGraph(axes, layoutSpec, embedding, drawNeighbourhoods=True)
jDraw.showMap("MANHATTAN DISTANCE")

_, axes = jDraw.creatMapPlot()
jDraw.addCanvas(axes, canvas, drawCells=True, drawNeighbours=False, pointColor=(0, 0, 0, 0.25))
jDraw.addMultiAreaPolygons(axes, polygons_che, layoutColoring, drawSeeds=True, drawCells=True)
jDraw.addAreaLayoutGraph(axes, layoutSpec, embedding, drawNeighbourhoods=True)
jDraw.showMap("CHEBYSHEV DISTANCE")
