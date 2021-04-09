import jahan.JahanToolbox as jtb
import jahan.Drawing as jDraw
from jahan.AreaClasses import *

if __name__ == '__main__':
    # ==================================================================================================================
    # ================================================== SPECIFICATION =================================================
    # ==================================================================================================================

    # ========================================
    # SPECIFICATION STEP 1 : AREA DEFINITIONS
    # ========================================

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

    # ===========================================
    # SPECIFICATION STEP 2 : CLIMATE DEFINITIONS
    # ===========================================

    climates = {"EMPTY": AreaClimate(0.075, "EMPTY", 0.0, {}),
                "climate_1": AreaClimate(0.075, "MUD", 0.0, {"CEDAR": 5, "BUSH": 10}),
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

    # =====================================
    # PIPELINE MODULE 1 : LAYOUT EMBEDDING
    # =====================================
    embedding = jtb.defaultPlanarEmbedding(layout, 0.1)

    # =============================================
    # PIPELINE MODULE 2 : AREA SKELETON GENERATION
    # =============================================
    skeletons = jtb.generateAreaSkeletonsFromHalfEdges(layout, embedding)

    # ==================================================================
    # PIPELINE MODULE 3 : CANVAS GENERATION (DIFFERENT IMPLEMENTATIONS)
    # ==================================================================

    # canvas = jtb.squareGridCanvasGenerator(20, 20)
    canvas = jtb.looseSquareGridCanvasGenerator(20, 20, 0.35)
    # canvas = jtb.hexagonGridCanvasGenerator(20, 20)
    # canvas = jtb.randomCanvasGenerator(400)
    # canvas = jtb.circularCanvasGenerator(0.05, 100)

    # ====================================================================
    # PIPELINE MODULE 4 : CANVAS PARTITIONING (DIFFERENT IMPLEMENTATIONS)
    # ====================================================================
    partitions, emptyPartition = jtb.partitionCanvasByAreaSkeletons(canvas, layout, skeletons, jtb.euclideanDistance)
    # partitions, emptyPartition = jtb.partitionCanvasByAreaSkeletons(canvas, layout, skeletons, jtb.manhattanDistance)
    # partitions, emptyPartition = jtb.partitionCanvasByAreaSkeletons(canvas, layout, skeletons, jtb.infNormDistance)

    # ==================================================================================
    # PIPELINE MODULE 5 : GENERATING CLIMATE INFLUENCE MAPS (DIFFERENT IMPLEMENTATIONS)
    # ==================================================================================
    climateMaps = jtb.generateClimateInfluenceMapsFromAreaPartitions(128, 128, partitions, climates, climateAssignments)

    # ============================================
    # PIPELINE MODULE 6 : GENERATING SURFACE MAPS
    # ============================================
    surfaceMaps = jtb.generateSurfaceMaps(climateMaps, climates)

    # =========================================
    # PIPELINE MODULE 7 : VEGETATION PLACEMENT
    # =========================================
    vegetationProbabilityMap = jtb.generateVegetationProbabilityMap(climateMaps, climates)
    vegetationTypeMaps = jtb.generateVegetationTypeMaps(climateMaps, climates)
    vegetationLocations = jtb.generateVegetationLocations(vegetationTypeMaps, vegetationProbabilityMap)

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
    # jDraw.AddMultipleMaps(axes, climateMaps, layoutColoring)
    # jDraw.addSingleMap(axes, vegetationProbabilityMap, 'Greens')
    # jDraw.addSingleMap(axes, climateMaps["climate_1"], 'Greys')
    # jDraw.AddMultipleMaps(axes, surfaceMaps, {"GRASS": (0, 0.5, 0), "MUD": (0.62, 0.32, 0.17)})
    # jDraw.AddMultipleMaps(axes, vegetationTypeMaps, vegetationColoring)
    jDraw.addDictionaryOfLocations(axes, vegetationLocations, vegetationColoring, 128, 128)
    jDraw.showMapPlot("PLOT")
