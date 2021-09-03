import jahan.Toolbox as tbx
import jahan.Layout as lyt
import jahan.Drawing as jDraw
import jahan.Canvas as cnv

layoutSpec = lyt.AreaLayoutSpecification()
layoutSpec.addArea("A")
layoutSpec.addArea("B")
layoutSpec.addArea("C")
layoutSpec.connectAreas("A", "B")
layoutSpec.connectAreas("B", "C")

figure, axs = jDraw.creatMultiMapPlot(1, 3)

stretchWeights = {"A": 1,
                  "B": 0.5,
                  "C": 1}

boundRadiusValues = {"A": 1,
                     "B": 0.05,
                     "C": 1}

embedding, skeletons = \
    tbx.generateLayoutSkeletons(layoutSpec=layoutSpec,
                                embeddingMethod=lyt.DefaultEmbedding(),
                                skeletonGenerator=lyt.StraightHalfEdgeSkeletonGenerator(stretchWeights))

squareSeeds = cnv.SquareCanvasSeedGenerator(20, 20).generate()
hexSeeds = cnv.HexagonCanvasSeedGenerator(20, 20).generate()
radialSeeds = cnv.RadialCanvasSeedGenerator(0.5, 150).generate()
loosSeeds = cnv.LooseSquareCanvasSeedGenerator(20, 20, 0.33).generate()
randSeeds = cnv.UniformRandomCanvasSeedGenerator(400).generate()
canvas = cnv.Canvas2D(hexSeeds)

polygons = tbx.GeneratePolygonsFromAreaSkeletons(canvas=canvas,
                                                 layoutSpec=layoutSpec,
                                                 skeletons=skeletons,
                                                 BoundRadiusValues=boundRadiusValues,
                                                 distanceFunction=tbx.EuclideanDistanceCalculator())

jDraw.addAreaLayoutGraph(axs[0], layoutSpec, embedding, drawNeighbourhoods=True)

layoutColoring = jDraw.createColoringSchemeForAreaLayout(layoutSpec)
jDraw.addMultipleAreaSkeletons(axs[1], skeletons, layoutColoring)

jDraw.addCanvas(axs[2], canvas, drawCells=True, drawNeighbours=False, pointColor=(0, 0, 0, 0.25))
jDraw.addMultiAreaPolygons(axs[2], polygons, layoutColoring, drawSeeds=True, drawCells=True)
jDraw.addAreaLayoutGraph(axs[2], layoutSpec, embedding, drawNeighbourhoods=True)

jDraw.showMultiMap(["PLANAR EMBEDDING", "AREA SKELETONS", "AREA POLYGONS"], axs)
