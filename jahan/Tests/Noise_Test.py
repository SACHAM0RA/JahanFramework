import jahan.Elevation as elv
import jahan.Drawing as jDraw

perlin_noise = elv.PerlinHeightNoiseGenerator(amplitude=1, octaves=4, scale=10).generateNoiseMap(200, 200)
open_simplex_noise = elv.OpenSimplexHeightNoiseGenerator(amplitude=1, octaves=4, scale=10).generateNoiseMap(200, 200)
worley_noise = elv.WorleyHeightNoiseGenerator(amplitude=1, seedCount=120).generateNoiseMap(200, 200)

_, axes = jDraw.creatMapPlot()
jDraw.addSingleMap(axes, perlin_noise, 'Greys', False)
jDraw.showMap("PERLIN NOISE")

_, axes = jDraw.creatMapPlot()
jDraw.addSingleMap(axes, open_simplex_noise, 'Greys', False)
jDraw.showMap("OPEN SIMPLEX NOISE")

_, axes = jDraw.creatMapPlot()
jDraw.addSingleMap(axes, worley_noise, 'Greys', False)
jDraw.showMap("WORLEY NOISE")