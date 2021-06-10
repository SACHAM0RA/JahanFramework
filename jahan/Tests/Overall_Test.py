import jahan.Toolbox as tbx
import jahan.Layout as lyt
import jahan.Canvas as cnv
import jahan.Landscape as lnd
import jahan.Elevation as elv
import jahan.Markers as mrk
import jahan.Drawing as jDraw

if __name__ == '__main__':
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

    squareSeeds = cnv.SquareCanvasSeedGenerator(20, 20).generate()
    hexSeeds = cnv.HexagonCanvasSeedGenerator(20, 20).generate()
    radialSeeds = cnv.RadialCanvasSeedGenerator(0.5, 150).generate()
    loosSeeds = cnv.LooseSquareCanvasSeedGenerator(20, 20, 0.33).generate()
    randSeeds = cnv.UniformRandomCanvasSeedGenerator(400).generate()
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

    influenceMaps = tbx.generateAreaInfluenceMapFromPartitions(partitions=partitions,
                                                               fadeRadius=0.05,
                                                               mapWidth=200,
                                                               mapHeight=200)

    heightProfile_0 = \
        elv.HeightProfile(foundation=elv.Flat_HeightFoundation(flatHeight=0),
                          detail=elv.PerlinHeightNoiseGenerator(amplitude=2.5, octaves=4, scale=16))

    heightProfile_1 = \
        elv.HeightProfile(foundation=elv.Flat_HeightFoundation(flatHeight=7.5),
                          detail=elv.PerlinHeightNoiseGenerator(amplitude=4.0, octaves=4, scale=16))

    heightProfile_2 = \
        elv.HeightProfile(foundation=elv.Flat_HeightFoundation(flatHeight=15.0),
                          detail=elv.PerlinHeightNoiseGenerator(amplitude=4.0, octaves=4, scale=16))

    heightProfile_3 = \
        elv.HeightProfile(foundation=elv.SDF_HeightFoundation(ascending=True, minHeight=10, maxHeight=30),
                          detail=elv.PerlinHeightNoiseGenerator(amplitude=4.0, octaves=4, scale=16))

    heightProfile_4 = \
        elv.HeightProfile(foundation=elv.Bell_HeightFoundation(ascending=False, minHeight=7.5, maxHeight=20),
                          detail=elv.PerlinHeightNoiseGenerator(amplitude=4.0, octaves=4, scale=16))

    heightSettings = {"A": heightProfile_1,
                      "B": heightProfile_2,
                      "C": heightProfile_3,
                      "D": heightProfile_4,
                      "E": heightProfile_1,
                      "F": heightProfile_2,
                      "G": heightProfile_3,
                      "H": heightProfile_4,
                      "I": heightProfile_4,
                      "J": heightProfile_3,
                      "K": heightProfile_3,
                      "L": heightProfile_4,
                      tbx.EMPTY_PART: heightProfile_0}

    heightMap = tbx.generateHeightMapFromElevationSettings(mapWidth=200,
                                                           mapHeight=200,
                                                           partitions=partitions,
                                                           influenceMaps=influenceMaps,
                                                           heightSettings=heightSettings)

    landscapes = {"landscape_0": lnd.LandscapeProfile("NONE", 0.0, lnd.NO_VEG),
                  "landscape_1": lnd.LandscapeProfile("GRASS", 0.01, {"CEDAR": 5, "BUSH": 10}),
                  "landscape_2": lnd.LandscapeProfile("SOIL", 0.025, {"OAK": 10, "BUSH": 10}),
                  "landscape_3": lnd.LandscapeProfile("SNOW", 0.02, {"OAK": 1, "CEDAR": 7}),
                  "landscape_4": lnd.LandscapeProfile("SNOW", 0.001, {"OAK": 1, "CEDAR": 1})}

    landscapeGenerator_0 = lnd.AreaLandscapeMapsFromAssignment(desiredLandscapeName="landscape_0")

    landscapeGenerator_1 = lnd.AreaLandscapeMapsFromAssignment(desiredLandscapeName="landscape_1")

    landscapeGenerator_2 = lnd.AreaLandscapeMapsFromAssignment(desiredLandscapeName="landscape_2")

    landscapeGenerator_3 = lnd.AreaLandscapeMapsFromAssignment(desiredLandscapeName="landscape_3")

    landscapeGenerator_4 = lnd.AreaLandscapeMapsFromAssignment(desiredLandscapeName="landscape_4")

    landscapeGenerator_h = lnd.AreaLandscapeMapsFromHeight(heightOrder=["landscape_0",
                                                                        "landscape_1",
                                                                        "landscape_2",
                                                                        "landscape_3",
                                                                        "landscape_4"])

    landscapeSetting = {"A": landscapeGenerator_1,
                        "B": landscapeGenerator_1,
                        "C": landscapeGenerator_2,
                        "D": landscapeGenerator_2,
                        "E": landscapeGenerator_2,
                        "F": landscapeGenerator_3,
                        "G": landscapeGenerator_3,
                        "H": landscapeGenerator_4,
                        "I": landscapeGenerator_4,
                        "J": landscapeGenerator_h,
                        "K": landscapeGenerator_h,
                        "L": landscapeGenerator_h,
                        tbx.EMPTY_PART: landscapeGenerator_0}

    landscapeMaps, surfaceMaps, vegetationDensityMap, vegetationTypeMaps, vegetationLocations = \
        tbx.generateLandscapeData(landscapes=landscapes,
                                  landscapeSetting=landscapeSetting,
                                  mapWidth=200,
                                  mapHeight=200,
                                  influenceMaps=influenceMaps,
                                  heightMap=heightMap)

    marker_spec_1 = mrk.MarkerSpecification(name="MARK-1",
                                            containerArea="H",
                                            heightPreference=1,
                                            heightImportance=1,
                                            centerPreference=0,
                                            centerImportance=0,
                                            neighbourhoodTendencies=["G", "B"],
                                            tendencyImportance=1)

    marker_spec_2 = mrk.MarkerSpecification(name="MARK-2",
                                            containerArea="J",
                                            heightPreference=1,
                                            heightImportance=0,
                                            centerPreference=1,
                                            centerImportance=1,
                                            neighbourhoodTendencies=[],
                                            tendencyImportance=0)

    marker_spec_3 = mrk.MarkerSpecification(name="MARK-3",
                                            containerArea="E",
                                            heightPreference=0,
                                            heightImportance=1,
                                            centerPreference=0,
                                            centerImportance=0,
                                            neighbourhoodTendencies=["F"],
                                            tendencyImportance=1)

    marker_placements = tbx.placeMarkers(markerSpecifications=[marker_spec_1, marker_spec_2, marker_spec_3],
                                         partitions=partitions,
                                         heightMap=heightMap)

    layoutColoring = jDraw.createColoringSchemeForAreaLayout(layoutSpec)

    _, axes = jDraw.creatMapPlot()
    jDraw.addAreaLayoutGraph(axes, layoutSpec, embedding, drawNeighbourhoods=True)
    jDraw.showMap("PLANAR EMBEDDING")

    _, axes = jDraw.creatMapPlot()
    jDraw.addMultipleAreaSkeletons(axes, skeletons, layoutColoring)
    jDraw.showMap("AREA SKELETONS")

    _, axes = jDraw.creatMapPlot()
    jDraw.addCanvas(axes, canvas, drawCells=True, drawNeighbours=False, pointColor=(0, 0, 0, 0.25))
    jDraw.addMultiAreaPartitions(axes, partitions_ecu, layoutColoring, drawSeeds=True, drawCells=True)
    jDraw.addAreaLayoutGraph(axes, layoutSpec, embedding, drawNeighbourhoods=True)
    jDraw.showMap("EUCLIDEAN DISTANCE")

    _, axes = jDraw.creatMapPlot()
    jDraw.addCanvas(axes, canvas, drawCells=True, drawNeighbours=False, pointColor=(0, 0, 0, 0.25))
    jDraw.addMultiAreaPartitions(axes, partitions_man, layoutColoring, drawSeeds=True, drawCells=True)
    jDraw.addAreaLayoutGraph(axes, layoutSpec, embedding, drawNeighbourhoods=True)
    jDraw.showMap("MANHATTAN DISTANCE")

    _, axes = jDraw.creatMapPlot()
    jDraw.addCanvas(axes, canvas, drawCells=True, drawNeighbours=False, pointColor=(0, 0, 0, 0.25))
    jDraw.addMultiAreaPartitions(axes, partitions_che, layoutColoring, drawSeeds=True, drawCells=True)
    jDraw.addAreaLayoutGraph(axes, layoutSpec, embedding, drawNeighbourhoods=True)
    jDraw.showMap("CHEBYSHEV DISTANCE")

    _, axes = jDraw.creatMapPlot()
    jDraw.addCanvas(axes, canvas, drawCells=True, drawNeighbours=False, pointColor=(0, 0, 0, 0.25))
    jDraw.addMultiAreaPartitions(axes, partitions_ecu, layoutColoring, drawSeeds=False, drawCells=False)
    jDraw.AddMultipleMaps(axes, influenceMaps, layoutColoring, False)
    jDraw.addAreaLayoutGraph(axes, layoutSpec, embedding, drawNeighbourhoods=True)
    jDraw.showMap("INFLUENCE MAPS")

    _, axes = jDraw.creatMapPlot()
    jDraw.addSingleMap(axes, heightMap, 'gist_earth', True, True)
    jDraw.addAreaLayoutGraph(axes, layoutSpec, embedding, drawNeighbourhoods=True)
    jDraw.showMap("HEIGHT MAP")

    _, axes = jDraw.creatMapPlot()
    jDraw.AddMultipleMaps(axes, landscapeMaps, {"landscape_0": (0, 0, 0),
                                                "landscape_1": (0.5, 1.0, 0.0),
                                                "landscape_2": (1.0, 1.0, 0.0),
                                                "landscape_3": (1.0, 0.5, 0.0),
                                                "landscape_4": (1.0, 0.0, 0.0)})
    jDraw.addMultiAreaPartitions(axes, partitions_ecu, layoutColoring, drawSeeds=False, drawCells=False)
    jDraw.addAreaLayoutGraph(axes, layoutSpec, embedding, drawNeighbourhoods=False)
    jDraw.showMap("LANDSCAPE MAPS")

    _, axes = jDraw.creatMapPlot()
    jDraw.AddMultipleMaps(axes, surfaceMaps, {"NONE": (0, 0, 0),
                                              "SNOW": (1, 0.98, 0.98),
                                              "GRASS": (0.48, 0.98, 0),
                                              "SOIL": (0.6, 0.46, 0.32)})
    jDraw.addMultiAreaPartitions(axes, partitions_ecu, layoutColoring, drawSeeds=False, drawCells=False)
    jDraw.addAreaLayoutGraph(axes, layoutSpec, embedding, drawNeighbourhoods=False)
    jDraw.showMap("SURFACE MAPS")

    _, axes = jDraw.creatMapPlot()
    jDraw.addSingleMap(axes, vegetationDensityMap, 'binary', False, True)
    jDraw.addMultiAreaPartitions(axes, partitions_ecu, layoutColoring, drawSeeds=False, drawCells=False)
    jDraw.addAreaLayoutGraph(axes, layoutSpec, embedding, drawNeighbourhoods=False)
    jDraw.showMap("VEGETATION DENSITY MAP")

    _, axes = jDraw.creatMapPlot()
    jDraw.AddMultipleMaps(axes, vegetationTypeMaps, {"CEDAR": (1.0, 0.0, 0.0),
                                                     "BUSH": (0.0, 1.0, 0.0),
                                                     "OAK": (0.0, 0.0, 1.0)})
    jDraw.addMultiAreaPartitions(axes, partitions_ecu, layoutColoring, drawSeeds=False, drawCells=False)
    jDraw.addAreaLayoutGraph(axes, layoutSpec, embedding, drawNeighbourhoods=False)
    jDraw.showMap("VEGETATION TYPE MAPS")

    _, axes = jDraw.creatMapPlot()
    vegetationColoring = {"CEDAR": ('red', "o"), "BUSH": ('green', "^"), "OAK": ('blue', "s")}
    jDraw.addMultiAreaPartitions(axes, partitions_ecu, None, drawSeeds=False, drawCells=True)
    jDraw.addDictionaryOfLocations(axes, vegetationLocations, vegetationColoring, 200, 200)
    jDraw.addAreaLayoutGraph(axes, layoutSpec, embedding, drawNeighbourhoods=False)
    jDraw.showMap("VEGETATION LOCATIONS")

    _, axes = jDraw.creatMapPlot()
    jDraw.addMultiAreaPartitions(axes, partitions_ecu, None, drawSeeds=False, drawCells=True)
    jDraw.addAreaLayoutGraph(axes, layoutSpec, embedding, drawNeighbourhoods=False)
    jDraw.addDictionaryOfLabeledLocations(axes, marker_placements, 200, 200)
    jDraw.showMap("MARKER PLACEMENT")
