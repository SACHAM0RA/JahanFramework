import copy

import jahan.Toolbox as tbx
import jahan.Layout as lyt
import jahan.Canvas as cnv
import jahan.Elevation as elv
import jahan.Drawing as jDraw

if __name__ == '__main__':
    layoutSpec = lyt.AreaLayoutSpecification()
    layoutSpec.addArea("A")
    layoutSpec.addArea("B")
    layoutSpec.addArea("C")
    layoutSpec.connectAreas("A", "B")
    layoutSpec.connectAreas("B", "C")

    squareSeeds = cnv.SquareCanvasSeedGenerator(16, 16).generate()
    hexSeeds = cnv.HexagonCanvasSeedGenerator(16, 16).generate()
    radialSeeds = cnv.RadialCanvasSeedGenerator(0.5, 150).generate()
    loosSeeds = cnv.LooseSquareCanvasSeedGenerator(16, 16, 0.35).generate()
    randSeeds = cnv.UniformRandomCanvasSeedGenerator(256).generate()
    canvas = cnv.Canvas2D(loosSeeds)

    armStretchWeights = {"A": 1,
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
                                    skeletonGenerator=lyt.StraightHalfEdgeSkeletonGenerator(armStretchWeights))

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

    partitions_ecu = tbx.partitionCanvasByAreaSkeletons(canvas=canvas,
                                                        layoutSpec=layoutSpec,
                                                        skeletons=skeletons,
                                                        BoundRadiusValues=boundRadiusValues,
                                                        distanceFunction=tbx.EuclideanDistanceCalculator())

    partitions_man = tbx.partitionCanvasByAreaSkeletons(canvas=canvas,
                                                        layoutSpec=layoutSpec,
                                                        skeletons=skeletons,
                                                        BoundRadiusValues=boundRadiusValues,
                                                        distanceFunction=tbx.ManhattanDistanceCalculator())

    partitions_che = tbx.partitionCanvasByAreaSkeletons(canvas=canvas,
                                                        layoutSpec=layoutSpec,
                                                        skeletons=skeletons,
                                                        BoundRadiusValues=boundRadiusValues,
                                                        distanceFunction=tbx.ChebyshevDistanceCalculator())
    partitions = partitions_ecu

    influenceMaps = tbx.generateAreaInfluenceMapFromPartitions(partitions, 0.00001, 200, 200)

    perlin_noise = elv.PerlinHeightNoiseGenerator(amplitude=8, octaves=4, scale=16)
    worley_noise = elv.WorleyHeightNoiseGenerator(amplitude=8, seedCount=200)


    # ======================

    def drawHeightMap(foundation, detail, title):
        heightProfile_0 = \
            elv.HeightProfile(foundation=elv.Flat_HeightFoundation(flatHeight=0),
                              detail=None)

        heightProfile_1 = \
            elv.HeightProfile(foundation=foundation,
                              detail=detail)

        HeightSettings = {"A": heightProfile_0,
                          "B": heightProfile_1,
                          "C": heightProfile_0,
                          tbx.EMPTY_PART: heightProfile_0}

        heightMap = tbx.generateHeightMapFromElevationSettings(200,
                                                               200,
                                                               partitions,
                                                               influenceMaps,
                                                               HeightSettings)

        _, axes = jDraw.creatMapPlot()
        jDraw.addSingleMap(axes, heightMap, 'gist_earth', True)
        jDraw.addAreaPartition(axes, partitions["B"])
        jDraw.showMap(title)


    drawHeightMap(foundation=elv.Flat_HeightFoundation(flatHeight=50),
                  detail=None,
                  title="FLAT HEIGHT FOUNDATION\nNO NOISE")

    drawHeightMap(foundation=elv.SDF_HeightFoundation(ascending=True, minHeight=10, maxHeight=30),
                  detail=None,
                  title="SDF HEIGHT FOUNDATION\nNO NOISE")

    drawHeightMap(foundation=elv.Cone_HeightFoundation(ascending=True, minHeight=10, maxHeight=30),
                  detail=None,
                  title="CONE HEIGHT FOUNDATION\nNO NOISE")

    drawHeightMap(foundation=elv.Bell_HeightFoundation(ascending=True, minHeight=10, maxHeight=30),
                  detail=None,
                  title="BELL HEIGHT FOUNDATION\nNO NOISE")

    drawHeightMap(foundation=elv.Flat_HeightFoundation(flatHeight=50),
                  detail=perlin_noise,
                  title="FLAT HEIGHT FOUNDATION\nPERLIN NOISE")

    drawHeightMap(foundation=elv.SDF_HeightFoundation(ascending=True, minHeight=10, maxHeight=30),
                  detail=perlin_noise,
                  title="SDF HEIGHT FOUNDATION\nPERLIN NOISE")

    drawHeightMap(foundation=elv.Cone_HeightFoundation(ascending=True, minHeight=10, maxHeight=30),
                  detail=perlin_noise,
                  title="CONE HEIGHT FOUNDATION\nPERLIN NOISE")

    drawHeightMap(foundation=elv.Bell_HeightFoundation(ascending=True, minHeight=10, maxHeight=30),
                  detail=perlin_noise,
                  title="BELL HEIGHT FOUNDATION\nPERLIN NOISE")

    drawHeightMap(foundation=elv.Flat_HeightFoundation(flatHeight=50),
                  detail=worley_noise,
                  title="FLAT HEIGHT FOUNDATION\nWORLEY NOISE")

    drawHeightMap(foundation=elv.SDF_HeightFoundation(ascending=True, minHeight=10, maxHeight=30),
                  detail=worley_noise,
                  title="SDF HEIGHT FOUNDATION\nWORLEY NOISE")

    drawHeightMap(foundation=elv.Cone_HeightFoundation(ascending=True, minHeight=10, maxHeight=30),
                  detail=worley_noise,
                  title="CONE HEIGHT FOUNDATION\nWORLEY NOISE")

    drawHeightMap(foundation=elv.Bell_HeightFoundation(ascending=True, minHeight=10, maxHeight=30),
                  detail=worley_noise,
                  title="BELL HEIGHT FOUNDATION\nWORLEY NOISE")
