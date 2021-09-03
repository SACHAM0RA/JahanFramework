import jahan.Canvas as cnv
import jahan.Drawing as jDraw

squareSeeds = cnv.SquareCanvasSeedGenerator(10, 10).generate()
hexSeeds = cnv.HexagonCanvasSeedGenerator(10, 10).generate()
radialSeeds = cnv.RadialCanvasSeedGenerator(0.25, 75).generate()
loosSeeds = cnv.LooseSquareCanvasSeedGenerator(4, 4, 0.33).generate()
randSeeds = cnv.UniformRandomCanvasSeedGenerator(10).generate()


figure, axs = jDraw.creatMapPlot()
#jDraw.addCanvas(axs[0], cnv.Canvas2D(squareSeeds), drawCells=True, drawNeighbours=False)
#jDraw.addCanvas(axs[1], cnv.Canvas2D(hexSeeds), drawCells=True, drawNeighbours=False)
#jDraw.addCanvas(axs[2], cnv.Canvas2D(radialSeeds), drawCells=True, drawNeighbours=False)
#jDraw.addCanvas(axs[3], cnv.Canvas2D(loosSeeds), drawCells=True, drawNeighbours=False)
jDraw.addCanvas(axs, cnv.Canvas2D(loosSeeds), drawCells=True, drawNeighbours=True)

jDraw.showMap("VORONOI DIAGRAM")
