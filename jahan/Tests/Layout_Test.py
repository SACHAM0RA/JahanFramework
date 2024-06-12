import jahan.Toolbox as tbx
import jahan.Layout as lyt
import jahan.Drawing as jDraw
import jahan.Canvas as cnv

layoutSpec = lyt.AreaLayoutSpecification()
layoutSpec.addArea("SHORE")
layoutSpec.addArea("JUNGLE")
layoutSpec.addArea("DESERT")
layoutSpec.addArea("MOUNTAINS")
layoutSpec.addArea("CITY")
layoutSpec.addArea("RIVERSIDE")

layoutSpec.connectAreas("SHORE", "DESERT")
layoutSpec.connectAreas("SHORE", "RIVERSIDE")
layoutSpec.connectAreas("SHORE", "MOUNTAINS")
layoutSpec.connectAreas("JUNGLE", "DESERT")
layoutSpec.connectAreas("DESERT", "CITY")
layoutSpec.connectAreas("DESERT", "RIVERSIDE")
layoutSpec.connectAreas("MOUNTAINS", "RIVERSIDE")
layoutSpec.connectAreas("CITY", "RIVERSIDE")

figure, axs = jDraw.creatMultiMapPlot(1, 2)

armStretchWeights = {"SHORE": 0.33,
                     "JUNGLE": 2,
                     "DESERT": 1,
                     "MOUNTAINS": 2,
                     "CITY": 1,
                     "RIVERSIDE": 0.5}

embedding, skeletons = \
    tbx.generateLayoutSkeletons(layoutSpec=layoutSpec,
                                embeddingMethod=lyt.DefaultEmbedding(applyForceDirected=False),
                                skeletonGenerator=lyt.StraightHalfEdgeSkeletonGenerator(armStretchWeights))

jDraw.addAreaLayoutGraph(axs[0], layoutSpec, embedding, drawNeighbourhoods=True)
layoutColoring = jDraw.createColoringSchemeForAreaLayout(layoutSpec)
jDraw.addMultipleAreaSkeletons(axs[1], skeletons, layoutColoring)

jDraw.showMultiMap(['PLANAR EMBEDDING', 'AREA SKELETONS'], axs)

squareSeeds = cnv.SquareCanvasSeedGenerator(20, 20).generate()
hexSeeds = cnv.HexagonCanvasSeedGenerator(20, 20).generate()
radialSeeds = cnv.RadialCanvasSeedGenerator(0.1, 75).generate()
loosSeeds = cnv.LooseSquareCanvasSeedGenerator(20, 20, 0.33).generate()
randSeeds = cnv.UniformRandomCanvasSeedGenerator(200).generate()
canvas = cnv.Canvas2D(loosSeeds)

boundRadiusValues = {"SHORE": 2,
                     "JUNGLE": 2,
                     "DESERT": 2,
                     "MOUNTAINS": 2,
                     "CITY": 2,
                     "RIVERSIDE": 2}

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
