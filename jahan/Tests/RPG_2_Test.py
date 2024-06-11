import jahan.Toolbox as tbx
import jahan.Layout as lyt
import jahan.Canvas as cnv
import jahan.Landscape as lnd
import jahan.Elevation as elv
import jahan.Markers as mrk
import jahan.Drawing as jDraw

if __name__ == '__main__':
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

    squareSeeds = cnv.SquareCanvasSeedGenerator(20, 20).generate()
    hexSeeds = cnv.HexagonCanvasSeedGenerator(20, 20).generate()
    radialSeeds = cnv.RadialCanvasSeedGenerator(0.1, 75).generate()
    loosSeeds = cnv.LooseSquareCanvasSeedGenerator(20, 20, 0.33).generate()
    randSeeds = cnv.UniformRandomCanvasSeedGenerator(200).generate()
    canvas = cnv.Canvas2D(loosSeeds)

    armStretchWeights = {"SHORE": 0.33,
                         "JUNGLE": 2,
                         "DESERT": 1,
                         "MOUNTAINS": 2,
                         "CITY": 1,
                         "RIVERSIDE": 0.5}

    embedding, skeletons = \
        tbx.generateLayoutSkeletons(layoutSpec=layoutSpec,
                                    embeddingMethod=lyt.DefaultEmbedding(),
                                    skeletonGenerator=lyt.StraightHalfEdgeSkeletonGenerator(armStretchWeights))

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

    influenceMaps = tbx.generateAreaInfluenceMapFromPolygons(polygons=polygons,
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
        elv.HeightProfile(foundation=elv.Bell_HeightFoundation(ascending=True, minHeight=7.5, maxHeight=20),
                          detail=elv.PerlinHeightNoiseGenerator(amplitude=4.0, octaves=4, scale=16))

    heightSettings = {"SHORE": heightProfile_1,
                      "JUNGLE": heightProfile_2,
                      "DESERT": heightProfile_1,
                      "MOUNTAINS": heightProfile_3,
                      "CITY": heightProfile_4,
                      "RIVERSIDE": heightProfile_2,
                      tbx.EMPTY_POLY: heightProfile_0}

    heightMap = tbx.generateHeightMapFromElevationSettings(mapWidth=200,
                                                           mapHeight=200,
                                                           polygons=polygons,
                                                           influenceMaps=influenceMaps,
                                                           heightSettings=heightSettings)

    landscapes = {"landscape_0": lnd.LandscapeProfile("NONE", 0.0, lnd.NONE_ITEM),
                  "landscape_1": lnd.LandscapeProfile("GRASS", 0.02, {"CEDAR": 10, "BUSH": 10}),
                  "landscape_2": lnd.LandscapeProfile("SAND", 0.001, {"OAK": 1, "BUSH": 1}),
                  "landscape_3": lnd.LandscapeProfile("SOIL", 0.007, {"OAK": 1, "CEDAR": 7}),
                  "landscape_4": lnd.LandscapeProfile("SNOW", 0.002, {"OAK": 1, "CEDAR": 1})}

    landscapeGenerator_0 = lnd.SingleProfileLandscapeGenerator(desiredLandscapeName="landscape_0")

    landscapeGenerator_1 = lnd.SingleProfileLandscapeGenerator(desiredLandscapeName="landscape_1")

    landscapeGenerator_2 = lnd.SingleProfileLandscapeGenerator(desiredLandscapeName="landscape_2")

    landscapeGenerator_3 = lnd.SingleProfileLandscapeGenerator(desiredLandscapeName="landscape_3")

    landscapeGenerator_4 = lnd.SingleProfileLandscapeGenerator(desiredLandscapeName="landscape_4")

    landscapeGenerator_h = lnd.HeightBasedLandscapeGenerator(heightOrder=["landscape_0",
                                                                          "landscape_1",
                                                                          "landscape_2",
                                                                          "landscape_3",
                                                                          "landscape_4"])

    landscapeSetting = {"SHORE": landscapeGenerator_3,
                        "JUNGLE": landscapeGenerator_1,
                        "DESERT": landscapeGenerator_2,
                        "MOUNTAINS": landscapeGenerator_h,
                        "CITY": landscapeGenerator_4,
                        "RIVERSIDE": landscapeGenerator_1,
                        tbx.EMPTY_POLY: landscapeGenerator_0}

    landscapeMaps, surfaceMaps, densityMap, itemTypeMaps, itemLocations = \
        tbx.generateLandscapeData(landscapes=landscapes,
                                  landscapeSetting=landscapeSetting,
                                  mapWidth=200,
                                  mapHeight=200,
                                  influenceMaps=influenceMaps,
                                  heightMap=heightMap)

    marker_spec_1 = mrk.MarkerSpecification(name="ORDER_HQ",
                                            containerArea="SHORE",
                                            heightPreference=0,
                                            heightImportance=0,
                                            centerPreference=1,
                                            centerImportance=1,
                                            effectorAreas=["MOUNTAINS", "JUNGLE"],
                                            effectorImportance=1)

    marker_spec_2 = mrk.MarkerSpecification(name="ARMY_HQ",
                                            containerArea="MOUNTAINS",
                                            heightPreference=1,
                                            heightImportance=1,
                                            centerPreference=1,
                                            centerImportance=1,
                                            effectorAreas=[],
                                            effectorImportance=0)

    marker_spec_3 = mrk.MarkerSpecification(name="CLAN_HQ",
                                            containerArea="JUNGLE",
                                            heightPreference=0,
                                            heightImportance=0,
                                            centerPreference=1,
                                            centerImportance=1,
                                            effectorAreas=[],
                                            effectorImportance=0)

    marker_placements = tbx.placeMarkers(markerSpecifications=[marker_spec_1, marker_spec_2, marker_spec_3],
                                         polygons=polygons,
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

    _, axes = jDraw.creatMapPlot()
    jDraw.addCanvas(axes, canvas, drawCells=True, drawNeighbours=False, pointColor=(0, 0, 0, 0.25))
    jDraw.addMultiAreaPolygons(axes, polygons_ecu, layoutColoring, drawSeeds=False, drawCells=False)
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
    jDraw.addMultiAreaPolygons(axes, polygons_ecu, layoutColoring, drawSeeds=False, drawCells=False)
    jDraw.addAreaLayoutGraph(axes, layoutSpec, embedding, drawNeighbourhoods=False)
    jDraw.showMap("LANDSCAPE MAPS")

    _, axes = jDraw.creatMapPlot()
    jDraw.AddMultipleMaps(axes, surfaceMaps, {"NONE": (0, 0, 0),
                                              "SNOW": (1, 0.98, 0.98),
                                              "GRASS": (0.48, 0.98, 0),
                                              "SOIL": (0.6, 0.46, 0.32),
                                              "SAND": (0.76, 0.69, 0.5)})
    jDraw.addMultiAreaPolygons(axes, polygons_ecu, layoutColoring, drawSeeds=False, drawCells=False)
    jDraw.addAreaLayoutGraph(axes, layoutSpec, embedding, drawNeighbourhoods=False)
    jDraw.showMap("SURFACE MAPS")

    _, axes = jDraw.creatMapPlot()
    jDraw.addSingleMap(axes, densityMap, 'binary', False, True)
    jDraw.addMultiAreaPolygons(axes, polygons_ecu, layoutColoring, drawSeeds=False, drawCells=False)
    jDraw.addAreaLayoutGraph(axes, layoutSpec, embedding, drawNeighbourhoods=False)
    jDraw.showMap("ITEM DENSITY MAP")

    _, axes = jDraw.creatMapPlot()
    jDraw.AddMultipleMaps(axes, itemTypeMaps, {"CEDAR": (1.0, 0.0, 0.0),
                                               "BUSH": (0.0, 1.0, 0.0),
                                               "OAK": (0.0, 0.0, 1.0)})
    jDraw.addMultiAreaPolygons(axes, polygons_ecu, layoutColoring, drawSeeds=False, drawCells=False)
    jDraw.addAreaLayoutGraph(axes, layoutSpec, embedding, drawNeighbourhoods=False)
    jDraw.showMap("ITEM TYPE MAPS")

    _, axes = jDraw.creatMapPlot()
    itemColoring = {"CEDAR": ('red', "o"), "BUSH": ('green', "^"), "OAK": ('blue', "s")}
    jDraw.addMultiAreaPolygons(axes, polygons_ecu, None, drawSeeds=False, drawCells=True)
    jDraw.addDictionaryOfLocations(axes, itemLocations, itemColoring, 200, 200)
    jDraw.addAreaLayoutGraph(axes, layoutSpec, embedding, drawNeighbourhoods=False)
    jDraw.showMap("ITEM LOCATIONS")

    _, axes = jDraw.creatMapPlot()
    jDraw.addMultiAreaPolygons(axes, polygons_ecu, None, drawSeeds=False, drawCells=True)
    jDraw.addAreaLayoutGraph(axes, layoutSpec, embedding, drawNeighbourhoods=False)
    jDraw.addDictionaryOfLabeledLocations(axes, marker_placements, 200, 200)
    jDraw.showMap("MARKER PLACEMENT")
