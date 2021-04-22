import jahan.JahanToolbox as jtb
import jahan.Drawing as jDraw
from jahan.AreaClasses import *

if __name__ == '__main__':
    # ==================================================================================================================
    # ================================================== SPECIFICATION =================================================
    # ==================================================================================================================

    # ==================================================================================================================
    # SPECIFICATION STEP 1 : AREA DEFINITIONS
    # ==================================================================================================================

    layout = AreaLayout()
    layout.addArea("A")
    layout.addArea("B")
    layout.addArea("C")
    layout.addArea("D")
    layout.addArea("E")
    layout.addArea("F")
    layout.addArea("G")
    layout.addArea("H")
    layout.addArea("I")
    layout.addArea("J")
    layout.addArea("K")
    layout.addArea("L")
    layout.connectAreas("A", "B")
    layout.connectAreas("A", "C")
    layout.connectAreas("B", "C")
    layout.connectAreas("D", "E")
    layout.connectAreas("B", "D")
    layout.connectAreas("E", "C")
    layout.connectAreas("E", "F")
    layout.connectAreas("B", "G")
    layout.connectAreas("B", "H")
    layout.connectAreas("H", "F")
    layout.connectAreas("G", "I")
    layout.connectAreas("G", "H")
    layout.connectAreas("F", "J")
    layout.connectAreas("K", "L")
    layout.connectAreas("K", "E")
    layout.connectAreas("L", "C")

    # ==================================================================================================================
    # SPECIFICATION STEP 2 : ELEVATION SETTINGS
    # ==================================================================================================================

    noiseGenerator_1 = jtb.PerlinHeightNoiseGenerator(amplitude=2.5, octaves=4, scale=12)

    heightProfile_1 = jtb.HeightProfile(foundation=jtb.Flat_HeightFoundation(flatHeight=0.0),
                                        fadeRadius=0.1, detail=noiseGenerator_1)

    heightProfile_2 = jtb.HeightProfile(foundation=jtb.Flat_HeightFoundation(flatHeight=15.0),
                                        fadeRadius=0.1, detail=noiseGenerator_1)

    heightProfile_3 = jtb.HeightProfile(foundation=jtb.SDF_HeightFoundation(ascending=True, minHeight=10, maxHeight=30),
                                        fadeRadius=0.1, detail=noiseGenerator_1)

    heightProfile_4 = jtb.HeightProfile(foundation=jtb.SDF_HeightFoundation(ascending=False, minHeight=0, maxHeight=20),
                                        fadeRadius=0.1, detail=noiseGenerator_1)

    elevationSettings = {"A": heightProfile_1,
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
                         "L": heightProfile_4}

    # ==================================================================================================================
    # SPECIFICATION STEP 3 : CLIMATE DEFINITIONS
    # ==================================================================================================================

    climates = {"climate_1": AreaClimate(0.075, "MUD", 0.0, {"CEDAR": 5, "BUSH": 10}),
                "climate_2": AreaClimate(0.075, "GRASS", 1.0, {"OAK": 10, "BUSH": 10}),
                "climate_3": AreaClimate(0.075, "MUD", 0.5, {"OAK": 1, "CEDAR": 5})}

    climateAssignments = {"A": "climate_1",
                          "B": "climate_2",
                          "C": "climate_2",
                          "D": "climate_1",
                          "E": "climate_1",
                          "F": "climate_3",
                          "G": "climate_2",
                          "H": "climate_1",
                          "I": "climate_1",
                          "J": "climate_2",
                          "K": "climate_3",
                          "L": "climate_3"}

    # ==================================================================================================================
    # =================================================== GENERATION ===================================================
    # ==================================================================================================================

    # ==================================================================================================================
    # PIPELINE MODULE 1 : LAYOUT EMBEDDING
    # ==================================================================================================================
    embedding = jtb.defaultPlanarEmbedding(layout, 0.1)

    # ==================================================================================================================
    # PIPELINE MODULE 2 : AREA SKELETON GENERATION
    # ==================================================================================================================
    skeletons = jtb.generateAreaSkeletonsFromHalfEdges(layout, embedding)

    # ==================================================================================================================
    # PIPELINE MODULE 3 : CANVAS GENERATION (DIFFERENT IMPLEMENTATIONS)
    # ==================================================================================================================

    # canvasGenerator = jtb.SquareGridCanvasGenerator(25, 25)
    canvasGenerator = jtb.LooseSquareGridCanvasGenerator(25, 25, 0.35)
    # canvasGenerator = jtb.HexagonGridCanvasGenerator(25, 25)
    # canvasGenerator = jtb.RandomCanvasGenerator(500)
    # canvasGenerator = jtb.CircularCanvasGenerator(0.05, 150)

    canvas = canvasGenerator.generate()

    # ==================================================================================================================
    # PIPELINE MODULE 4 : PARTITIONING DISTANCE (DIFFERENT IMPLEMENTATIONS)
    # ==================================================================================================================

    distanceCalculator = jtb.EuclideanDistanceCalculator()
    # distanceCalculator = jtb.ManhattanDistanceCalculator()
    # distanceCalculator = jtb.InfiniteNormDistanceCalculator()

    # ==================================================================================================================
    # PIPELINE MODULE 5 : PARTITIONING
    # ==================================================================================================================

    partitions, emptyPartition = jtb.partitionCanvasByAreaSkeletons(canvas, layout, skeletons, distanceCalculator)

    # ==================================================================================================================
    # PIPELINE MODULE 6 : GENERATING HEIGHT MAPS (DIFFERENT IMPLEMENTATIONS)
    # ==================================================================================================================

    heightMap = jtb.generateHeightMapFromElevationSettings(128, 128, elevationSettings, partitions)
    # heightMap = jtb.generateAreaInfluenceMapFromPartitions(partitions, 128, 128)

    # ==================================================================================================================
    # PIPELINE MODULE 7 : GENERATING CLIMATE INFLUENCE MAPS
    # ==================================================================================================================
    #climateMaps = jtb.generateClimateInfluenceMapsFromAreaPartitions(128, 128, partitions, climates, climateAssignments)

    # ==================================================================================================================
    # PIPELINE MODULE 8 : GENERATING SURFACE MAPS
    # ==================================================================================================================
    #surfaceMaps = jtb.generateSurfaceMaps(climateMaps, climates)

    # ==================================================================================================================
    # PIPELINE MODULE 9 : VEGETATION PLACEMENT
    # ==================================================================================================================
    #vegetationProbabilityMap = jtb.generateVegetationProbabilityMap(climateMaps, climates)
    #vegetationTypeMaps = jtb.generateVegetationTypeMaps(climateMaps, climates)
    #vegetationLocations = jtb.generateVegetationLocations(vegetationTypeMaps, vegetationProbabilityMap)

    # ==================================================================================================================
    # ============================================= DEBUG AND VISUALIZATION ============================================
    # ==================================================================================================================

    figure, axes = jDraw.creatMapPlot()
    layoutColoring = jDraw.createColoringSchemeForAreaLayout(layout)
    vegetationColoring = {"CEDAR": (1, 0, 0), "BUSH": (0, 1, 0), "OAK": (0, 0, 1)}
    jDraw.addCanvas(axes, canvas, drawCells=True, drawNeighbours=False)
    jDraw.addAreaLayoutGraph(axes, layout, embedding, drawNeighbourhoods=True)
    jDraw.addMultiAreaPartitions(axes, partitions, layoutColoring, drawSeeds=False, drawCells=False)
    # jDraw.addMultipleAreaSkeletons(axes, skeletons, layoutColoring)
    # jDraw.addSingleMap(axes, vegetationProbabilityMap, 'Greens')
    # jDraw.addSingleMap(axes, climateMaps["climate_1"], 'Greys')
    # jDraw.AddMultipleMaps(axes, surfaceMaps, {"GRASS": (0, 0.5, 0), "MUD": (0.62, 0.32, 0.17)})
    # jDraw.AddMultipleMaps(axes, vegetationTypeMaps, vegetationColoring)
    # jDraw.addDictionaryOfLocations(axes, vegetationLocations, vegetationColoring, 128, 128)

    jDraw.showMap("PLOT")
    jDraw.showHeightMap(heightMap)
