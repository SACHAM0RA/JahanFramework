import jahan.Toolbox as tbx
import jahan.Layout as lyt
import jahan.Canvas as cnv
import jahan.Landscape as lnd
import jahan.Elevation as elv
import jahan.Markers as mrk
import jahan.Drawing as jDraw
from jahan.GridMap import *
import time

if __name__ == '__main__':
    start_time = time.time()

    layoutSpec = lyt.AreaLayoutSpecification()
    layoutSpec.addArea("S")
    layoutSpec.addArea("F1")
    layoutSpec.addArea("F2")
    layoutSpec.addArea("T1")
    layoutSpec.addArea("T2")
    layoutSpec.addArea("MB1")
    layoutSpec.addArea("MB2")
    layoutSpec.addArea("BOSS")
    layoutSpec.addArea("T3")
    layoutSpec.addArea("T4")
    layoutSpec.addArea("C1")
    layoutSpec.addArea("C2")
    layoutSpec.addArea("C3")
    layoutSpec.addArea("C4")
    layoutSpec.addArea("C5")
    layoutSpec.addArea("C6")
    layoutSpec.addArea("C7")
    layoutSpec.addArea("C8")
    layoutSpec.addArea("C9")
    layoutSpec.addArea("C10")
    layoutSpec.addArea("C11")

    layoutSpec.connectAreas("S", "C1")
    layoutSpec.connectAreas("S", "C2")
    layoutSpec.connectAreas("F1", "C1")
    layoutSpec.connectAreas("F1", "C5")
    layoutSpec.connectAreas("F1", "C11")
    layoutSpec.connectAreas("F1", "C3")
    layoutSpec.connectAreas("F2", "C2")
    layoutSpec.connectAreas("F2", "C6")
    layoutSpec.connectAreas("F2", "C11")
    layoutSpec.connectAreas("F2", "C4")
    layoutSpec.connectAreas("T1", "C5")
    layoutSpec.connectAreas("T2", "C6")
    layoutSpec.connectAreas("MB1", "C3")
    layoutSpec.connectAreas("MB1", "C7")
    layoutSpec.connectAreas("MB1", "C9")
    layoutSpec.connectAreas("MB2", "C4")
    layoutSpec.connectAreas("MB2", "C8")
    layoutSpec.connectAreas("MB2", "C10")
    layoutSpec.connectAreas("BOSS", "C9")
    layoutSpec.connectAreas("BOSS", "C10")
    layoutSpec.connectAreas("T3", "C7")
    layoutSpec.connectAreas("T4", "C8")

    #squareSeeds = cnv.SquareCanvasSeedGenerator(64, 64).generate()
    hexSeeds = cnv.HexagonCanvasSeedGenerator(32, 32).generate()
    #radialSeeds = cnv.RadialCanvasSeedGenerator(0.05, 150).generate()
    #loosSeeds = cnv.LooseSquareCanvasSeedGenerator(50, 50, 0.33).generate()
    #randSeeds = cnv.UniformRandomCanvasSeedGenerator(400).generate()
    canvas = cnv.Canvas2D(hexSeeds)

    stretchWeights = {"S": 2.0,
                      "F1": 2.0,
                      "F2": 2.0,
                      "T1": 2.0,
                      "T2": 2.0,
                      "MB1": 2.0,
                      "MB2": 2.0,
                      "BOSS": 2.0,
                      "T3": 2.0,
                      "T4": 2.0,
                      "C1": 2.0,
                      "C2": 2.0,
                      "C3": 2.0,
                      "C4": 2.0,
                      "C5": 2.0,
                      "C6": 2.0,
                      "C7": 2.0,
                      "C8": 2.0,
                      "C9": 2.0,
                      "C10": 2.0,
                      "C11": 2.0
                      }

    embedding, skeletons = \
        tbx.generateLayoutSkeletons(layoutSpec=layoutSpec,
                                    embeddingMethod=lyt.DefaultEmbedding(iteration=40000),
                                    skeletonGenerator=lyt.StraightHalfEdgeSkeletonGenerator(stretchWeights))

    boundRadiusValues = {"S": 0.75,
                         "F1": 0.75,
                         "F2": 0.75,
                         "T1": 0.75,
                         "T2": 0.75,
                         "MB1": 0.75,
                         "MB2": 0.75,
                         "BOSS": 0.75,
                         "T3": 0.75,
                         "T4": 0.75,
                         "C1": 0.02,
                         "C2": 0.02,
                         "C3": 0.02,
                         "C4": 0.02,
                         "C5": 0.02,
                         "C6": 0.02,
                         "C7": 0.02,
                         "C8": 0.02,
                         "C9": 0.02,
                         "C10": 0.02,
                         "C11": 0.02
                         }

    #polygons_ecu = tbx.GeneratePolygonsFromAreaSkeletons(canvas=canvas,
    #                                                     layoutSpec=layoutSpec,
    #                                                     skeletons=skeletons,
    #                                                     BoundRadiusValues=boundRadiusValues,
    #                                                     distanceFunction=tbx.EuclideanDistanceCalculator(),
    #                                                     deletionDepth=1)

    polygons_man = tbx.GeneratePolygonsFromAreaSkeletons(canvas=canvas,
                                                         layoutSpec=layoutSpec,
                                                         skeletons=skeletons,
                                                         BoundRadiusValues=boundRadiusValues,
                                                         distanceFunction=tbx.ManhattanDistanceCalculator())

    #polygons_che = tbx.GeneratePolygonsFromAreaSkeletons(canvas=canvas,
    #                                                     layoutSpec=layoutSpec,
    #                                                     skeletons=skeletons,
    #                                                     BoundRadiusValues=boundRadiusValues,
    #                                                     distanceFunction=tbx.ChebyshevDistanceCalculator())
    polygons = polygons_man

    heightMap = GridMap(200, 200)

    landscapes = {"NONE": lnd.LandscapeProfile("NONE", 0.0, lnd.NONE_ITEM),
                  "TREASURE": lnd.LandscapeProfile("NONE", 0.005, {"TREASURE": 1}),
                  "ENEMY": lnd.LandscapeProfile("NONE", 0.0075, {"ENEMY": 1})}

    tr_land = lnd.SingleProfileLandscapeGenerator(desiredLandscapeName="TREASURE")
    enemy_land = lnd.SingleProfileLandscapeGenerator(desiredLandscapeName="ENEMY")
    none_land = lnd.SingleProfileLandscapeGenerator(desiredLandscapeName="NONE")

    landscapeSetting = {"S": none_land,
                        "F1": enemy_land,
                        "F2": enemy_land,
                        "T1": tr_land,
                        "T2": tr_land,
                        "MB1": enemy_land,
                        "MB2": enemy_land,
                        "BOSS": tr_land,
                        "T3": tr_land,
                        "T4": tr_land,
                        "C1": none_land,
                        "C2": none_land,
                        "C3": none_land,
                        "C4": none_land,
                        "C5": none_land,
                        "C6": none_land,
                        "C7": none_land,
                        "C8": none_land,
                        "C9": none_land,
                        "C10": none_land,
                        "C11": none_land
                        }

    influenceMaps = tbx.generateAreaInfluenceMapFromPolygons(polygons=polygons,
                                                             fadeRadius=0.001,
                                                             mapWidth=200,
                                                             mapHeight=200)

    landscapeMaps, surfaceMaps, itemDensityMap, itemTypeMaps, itemLocations = \
        tbx.generateLandscapeData(landscapes=landscapes,
                                  landscapeSetting=landscapeSetting,
                                  mapWidth=200,
                                  mapHeight=200,
                                  influenceMaps=influenceMaps,
                                  heightMap=heightMap)

    UB_1 = mrk.MarkerSpecification(name="UB-1",
                                   containerArea="S",
                                   heightPreference=0,
                                   heightImportance=0,
                                   centerPreference=1,
                                   centerImportance=1,
                                   effectorAreas=[],
                                   effectorImportance=0)

    UB_2 = mrk.MarkerSpecification(name="UB-2",
                                   containerArea="C3",
                                   heightPreference=0,
                                   heightImportance=0,
                                   centerPreference=1,
                                   centerImportance=1,
                                   effectorAreas=[],
                                   effectorImportance=0)

    UB_3 = mrk.MarkerSpecification(name="UB-3",
                                   containerArea="C4",
                                   heightPreference=0,
                                   heightImportance=0,
                                   centerPreference=1,
                                   centerImportance=1,
                                   effectorAreas=[],
                                   effectorImportance=0)

    KEY_A = mrk.MarkerSpecification(name="KEY-A",
                                    containerArea="T4",
                                    heightPreference=0,
                                    heightImportance=0,
                                    centerPreference=1,
                                    centerImportance=1,
                                    effectorAreas=[],
                                    effectorImportance=0)

    KEY_B = mrk.MarkerSpecification(name="KEY-B",
                                    containerArea="T3",
                                    heightPreference=0,
                                    heightImportance=0,
                                    centerPreference=1,
                                    centerImportance=1,
                                    effectorAreas=[],
                                    effectorImportance=0)

    marker_placements = tbx.placeMarkers(markerSpecifications=[UB_1, UB_2, UB_3, KEY_A, KEY_B],
                                         polygons=polygons,
                                         heightMap=heightMap)

    end_time = time.time()
    execution_time = end_time - start_time
    print("MAP GENERATION TIME: " + str(execution_time))

    layoutColoring = jDraw.createColoringSchemeForAreaLayout(layoutSpec)

    _, axes = jDraw.creatMapPlot()
    jDraw.addAreaLayoutGraph(axes, layoutSpec, embedding, drawNeighbourhoods=True)
    jDraw.showMap("PLANAR EMBEDDING")

    _, axes = jDraw.creatMapPlot()
    jDraw.addMultipleAreaSkeletons(axes, skeletons, layoutColoring)
    jDraw.showMap("AREA SKELETONS")

    _, axes = jDraw.creatMapPlot()
    jDraw.addCanvas(axes, canvas, drawCells=True, drawNeighbours=False, pointColor=(0, 0, 0, 0.25))
    jDraw.addMultiAreaPolygons(axes, polygons, layoutColoring, drawSeeds=True, drawCells=True)
    jDraw.addAreaLayoutGraph(axes, layoutSpec, embedding, drawNeighbourhoods=True)
    jDraw.showMap("EUCLIDEAN DISTANCE")

    _, axes = jDraw.creatMapPlot()
    jDraw.addMultiAreaPolygons(axes, polygons, None, drawSeeds=False, drawCells=True)
    jDraw.addAreaLayoutGraph(axes, layoutSpec, embedding, drawNeighbourhoods=False)
    jDraw.addDictionaryOfLabeledLocations(axes, marker_placements, 200, 200)
    jDraw.showMap("MARKER PLACEMENT")

    _, axes = jDraw.creatMapPlot()
    itemColoring = {"TREASURE": ('yellow', "s"), "ENEMY": ('red', "o")}
    jDraw.addMultiAreaPolygons(axes, polygons, None, drawSeeds=False, drawCells=True)
    jDraw.addDictionaryOfLocations(axes, itemLocations, itemColoring, 200, 200)
    jDraw.addAreaLayoutGraph(axes, layoutSpec, embedding, drawNeighbourhoods=False)
    jDraw.showMap("ITEM LOCATIONS")
