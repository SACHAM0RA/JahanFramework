import jahan.Layout as lyt
import jahan.Canvas as cnv
import jahan.Elevation as elv
import jahan.Landscape as lnd
import jahan.Markers as mrk
import jahan.Toolbox as tbx
import jahan.Drawing as jDraw

if __name__ == '__main__':
    # ==================================================================================================================
    # ================================================== SPECIFICATION =================================================
    # ==================================================================================================================

    # ==================================================================================================================
    # SPECIFICATION STEP 1 : AREA DEFINITIONS
    # ==================================================================================================================

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

    # ==================================================================================================================
    # SPECIFICATION STEP 2 : ELEVATION SETTINGS
    # ==================================================================================================================

    noiseGenerator_0 = elv.PerlinHeightNoiseGenerator(amplitude=2.5, octaves=4, scale=16)
    noiseGenerator_1 = elv.PerlinHeightNoiseGenerator(amplitude=5.5, octaves=4, scale=16)
    noiseGenerator_2 = elv.OpenSimplexHeightNoiseGenerator(amplitude=7.5, octaves=4, scale=16)
    noiseGenerator_3 = elv.WorleyHeightNoiseGenerator(amplitude=7.5, seedCount=100)

    heightProfile_0 = elv.HeightProfile(foundation=elv.Flat_HeightFoundation(flatHeight=0),
                                        detail=noiseGenerator_0)

    heightProfile_1 = \
        elv.HeightProfile(foundation=elv.Flat_HeightFoundation(flatHeight=7.5),
                          detail=noiseGenerator_1)

    heightProfile_2 = \
        elv.HeightProfile(foundation=elv.Flat_HeightFoundation(flatHeight=15.0),
                          detail=noiseGenerator_1)

    heightProfile_3 = \
        elv.HeightProfile(foundation=elv.SDF_HeightFoundation(ascending=True, minHeight=10, maxHeight=30),
                          detail=noiseGenerator_1)

    heightProfile_4 = \
        elv.HeightProfile(foundation=elv.Bell_HeightFoundation(ascending=False, minHeight=10, maxHeight=20),
                          detail=noiseGenerator_1)

    heightSettings = {"A": heightProfile_1,
                      "B": heightProfile_2,
                      "C": heightProfile_3,
                      "D": heightProfile_4,
                      "E": heightProfile_1,
                      "F": heightProfile_2,
                      "G": heightProfile_3,
                      "H": heightProfile_4,
                      "I": heightProfile_1,
                      "J": heightProfile_2,
                      "K": heightProfile_3,
                      "L": heightProfile_4,
                      tbx.EMPTY_POLY: heightProfile_0}

    # ==================================================================================================================
    # SPECIFICATION STEP 3 : LANDSCAPE DEFINITIONS
    # ==================================================================================================================

    landscapes = {"landscape_0": lnd.LandscapeProfile("NONE", 0.0, {}),
                  "landscape_1": lnd.LandscapeProfile("GRASS", 0.01, {"CEDAR": 5, "BUSH": 10}),
                  "landscape_2": lnd.LandscapeProfile("MUD", 0.025, {"OAK": 10, "BUSH": 10}),
                  "landscape_3": lnd.LandscapeProfile("SNOW", 0.02, {"OAK": 1, "CEDAR": 7})}

    # ==================================================================================================================
    # SPECIFICATION STEP 4 : MARKER SPECIFICATION
    # ==================================================================================================================

    marker_spec_1 = mrk.MarkerSpecification(name="MARK-1",
                                            containerArea="H",
                                            heightPreference=1,
                                            heightImportance=1,
                                            centerPreference=0,
                                            centerImportance=0,
                                            effectorAreas=["G", "B"],
                                            effectorImportance=1)

    marker_spec_2 = mrk.MarkerSpecification(name="MARK-2",
                                            containerArea="J",
                                            heightPreference=1,
                                            heightImportance=0,
                                            centerPreference=1,
                                            centerImportance=1,
                                            effectorAreas=[],
                                            effectorImportance=0)

    marker_spec_3 = mrk.MarkerSpecification(name="MARK-3",
                                            containerArea="E",
                                            heightPreference=0,
                                            heightImportance=1,
                                            centerPreference=0,
                                            centerImportance=0,
                                            effectorAreas=["F"],
                                            effectorImportance=1)

    # ==================================================================================================================
    # =================================================== GENERATION ===================================================
    # ==================================================================================================================

    # ==================================================================================================================
    # PIPELINE PROCESS 1 : LAYOUT SKELETON GENERATION
    # ==================================================================================================================

    embedding, skeletons = tbx.generateLayoutSkeletons(layoutSpec=layoutSpec,
                                                       embeddingMethod=lyt.DefaultEmbedding(),
                                                       skeletonGenerator=lyt.StraightHalfEdgeSkeletonGenerator())

    # ==================================================================================================================
    # PIPELINE PROCESS 3 : CANVAS GENERATION
    # ==================================================================================================================

    # seeds = cnv.SquareGridCanvasGenerator(16, 16).generate()
    seeds = cnv.LooseSquareCanvasSeedGenerator(16, 16, 0.35).generate()
    # seeds = cnv.HexagonGridCanvasGenerator(16, 16).generate()
    # seeds = cnv.RandomCanvasGenerator(256).generate()
    # seeds = cnv.CircularCanvasGenerator(0.05, 150).generate()

    canvas = cnv.Canvas2D(seeds)

    # ==================================================================================================================
    # PIPELINE PROCESS 5 : PARTITIONING
    # ==================================================================================================================

    distanceCalculator = tbx.EuclideanDistanceCalculator()
    # distanceCalculator = tbx.ManhattanDistanceCalculator()
    # distanceCalculator = tbx.ChebyshevDistanceCalculator()

    partitions = tbx.GeneratePolygonsFromAreaSkeletons(canvas, layoutSpec, skeletons, distanceCalculator)

    # ==================================================================================================================
    # PIPELINE PROCESS 6 : INFLUENCE CALCULATION
    # ==================================================================================================================

    influenceMaps = tbx.generateAreaInfluenceMapFromPolygons(partitions, 0.05, 200, 200)

    # ==================================================================================================================
    # PIPELINE PROCESS 7 : GENERATING HEIGHT MAPS
    # ==================================================================================================================

    heightMap = tbx.generateHeightMapFromElevationSettings(mapWidth=200,
                                                           mapHeight=200,
                                                           polygons=partitions,
                                                           influenceMaps=influenceMaps,
                                                           heightSettings=heightSettings)

    # ==================================================================================================================
    # PIPELINE PROCESS 8 : GENERATING LANDSCAPE INFLUENCE MAPS
    # ==================================================================================================================

    landscapesHeightOrder = ["landscape_0", "landscape_1", "landscape_2", "landscape_3"]

    landscapeGenerator_0 = lnd.SingleProfileLandscapeGenerator(landscapes, influenceMaps, heightMap, "landscape_0")
    landscapeGenerator_1 = lnd.SingleProfileLandscapeGenerator(landscapes, influenceMaps, heightMap, "landscape_1")
    landscapeGenerator_2 = lnd.SingleProfileLandscapeGenerator(landscapes, influenceMaps, heightMap, "landscape_2")
    landscapeGenerator_3 = lnd.SingleProfileLandscapeGenerator(landscapes, influenceMaps, heightMap, "landscape_3")
    landscapeGenerator_h = lnd.HeightBasedLandscapeGenerator(landscapes, influenceMaps, heightMap, landscapesHeightOrder)

    landscapeSetting = {"A": landscapeGenerator_1,
                        "B": landscapeGenerator_1,
                        "C": landscapeGenerator_1,
                        "D": landscapeGenerator_1,
                        "E": landscapeGenerator_2,
                        "F": landscapeGenerator_2,
                        "G": landscapeGenerator_2,
                        "H": landscapeGenerator_2,
                        "I": landscapeGenerator_3,
                        "J": landscapeGenerator_h,
                        "K": landscapeGenerator_h,
                        "L": landscapeGenerator_h,
                        tbx.EMPTY_POLY: landscapeGenerator_0}

    landscapeMaps = tbx.generateLandscapeMaps(mapWidth=200,
                                              mapHeight=200,
                                              landscapes=landscapes,
                                              landscapeSettings=landscapeSetting)

    # ==================================================================================================================
    # PIPELINE PROCESS 9 : GENERATING SURFACE MAPS
    # ==================================================================================================================
    surfaceMaps = tbx.generateSurfaceMaps(landscapeMaps=landscapeMaps,
                                          landscapes=landscapes)

    # ==================================================================================================================
    # PIPELINE PROCESS 10 : VEGETATION PLACEMENT
    # ==================================================================================================================
    vegetationProbabilityMap, vegetationTypeMaps, vegetationLocations = \
        tbx.placeVegetation(landscapeMaps=landscapeMaps,
                            landscapes=landscapes)

    # ==================================================================================================================
    # PIPELINE PROCESS 11 : MARKER PLACEMENT
    # ==================================================================================================================

    marker_placements = tbx.placeMarkers(markerSpecifications=[marker_spec_1, marker_spec_2, marker_spec_3],
                                         polygons=partitions,
                                         heightMap=heightMap)

    # ==================================================================================================================
    # ============================================= DEBUG AND VISUALIZATION ============================================
    # ==================================================================================================================

    figure, axes = jDraw.creatMapPlot()
    layoutColoring = jDraw.createColoringSchemeForAreaLayout(layoutSpec)
    vegetationColoring = {"CEDAR": ('red', '*'), "BUSH": ('green', 'P'), "OAK": ('blue', 'X')}
    # jDraw.addMultipleAreaSkeletons(axes, skeletons, layoutColoring)
    # jDraw.addSingleMap(axes, vegetationProbabilityMap, 'Greens')
    # jDraw.addSingleMap(axes, landscapeMaps["landscape_1"], 'Greys')
    # jDraw.AddMultipleMaps(axes, surfaceMaps, {"NONE": (0, 0, 0),
    #                                           "SNOW": (1, 1, 1),
    #                                           "GRASS": (0, 0.5, 0),
    #                                           "MUD": (0.62, 0.32, 0.17)})
    # jDraw.AddMultipleMaps(axes, vegetationTypeMaps, vegetationColoring)
    # jDraw.addDictionaryOfLocations(axes, vegetationLocations, vegetationColoring, 200, 200)

    jDraw.addSingleMap(axes, heightMap, 'gist_earth', True)

    # jDraw.addCanvas(axes, canvas, drawCells=True, drawNeighbours=False)
    # jDraw.addMultiAreaPartitions(axes, partitions, layoutColoring, drawSeeds=False, drawCells=False)
    jDraw.addAreaLayoutGraph(axes, layoutSpec, embedding, drawNeighbourhoods=True)

    # jDraw.addDictionaryOfLabeledLocations(axes, marker_placements, 128, 128)

    jDraw.showMap("PLOT")
    # jDraw.showHeightMap(heightMap)
