import jahan.Canvas as cnv
import jahan.Drawing as jDraw

squareSeeds = cnv.SquareCanvasSeedGenerator(10, 10).generate()
hexSeeds = cnv.HexagonCanvasSeedGenerator(10, 10).generate()
radialSeeds = cnv.RadialCanvasSeedGenerator(0.1, 75).generate()
loosSeeds = cnv.LooseSquareCanvasSeedGenerator(10, 10, 0.35).generate()
randSeeds = cnv.UniformRandomCanvasSeedGenerator(100).generate()


figure, axs = jDraw.creatMultiMapPlot(2, 3)
jDraw.addCanvas(axs[0], cnv.Canvas2D(squareSeeds), drawCells=True, drawNeighbours=False)
jDraw.addCanvas(axs[1], cnv.Canvas2D(hexSeeds), drawCells=True, drawNeighbours=False)
jDraw.addCanvas(axs[2], cnv.Canvas2D(radialSeeds), drawCells=True, drawNeighbours=False)
jDraw.addCanvas(axs[3], cnv.Canvas2D(loosSeeds), drawCells=True, drawNeighbours=False)
jDraw.addCanvas(axs[4], cnv.Canvas2D(randSeeds), drawCells=True, drawNeighbours=False)

jDraw.showMultiMap(["SQUARE", "HEXAGON", "RADIAL", "LOOSED SQUARE", "UNIFORM RANDOM"], axs)
