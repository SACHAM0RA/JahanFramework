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
    layoutSpec.addArea("P-BASE")
    layoutSpec.addArea("E-BASE")
    layoutSpec.addArea("O-BASE")
    layoutSpec.addArea("GM-1")
    layoutSpec.addArea("GM-2")
    layoutSpec.addArea("GM-3")
    layoutSpec.addArea("BRDG-1")
    layoutSpec.addArea("BRDG-2")
    layoutSpec.addArea("BRDG-3")
    layoutSpec.addArea("BRDG-4")
    layoutSpec.addArea("OF")
    layoutSpec.addArea("WASTE")
    layoutSpec.connectAreas("P-BASE", "GM-1")
    layoutSpec.connectAreas("P-BASE", "GM-2")
    layoutSpec.connectAreas("P-BASE", "E-BASE")
    layoutSpec.connectAreas("GM-1", "BRDG-1")
    layoutSpec.connectAreas("GM-2", "BRDG-2")
    layoutSpec.connectAreas("GM-2", "BRDG-3")
    layoutSpec.connectAreas("BRDG-1", "O-BASE")
    layoutSpec.connectAreas("BRDG-2", "O-BASE")
    layoutSpec.connectAreas("BRDG-3", "O-BASE")
    layoutSpec.connectAreas("O-BASE", "BRDG-4")
    layoutSpec.connectAreas("BRDG-4", "OF")
    layoutSpec.connectAreas("OF", "WASTE")
    layoutSpec.connectAreas("WASTE", "GM-3")
    layoutSpec.connectAreas("GM-3", "E-BASE")

    squareSeeds = cnv.SquareCanvasSeedGenerator(20, 20).generate()
    hexSeeds = cnv.HexagonCanvasSeedGenerator(20, 20).generate()
    radialSeeds = cnv.RadialCanvasSeedGenerator(0.05, 150).generate()
    loosSeeds = cnv.LooseSquareCanvasSeedGenerator(20, 20, 0.33).generate()
    randSeeds = cnv.UniformRandomCanvasSeedGenerator(400).generate()
    canvas = cnv.Canvas2D(hexSeeds)

    stretchWeights = {"P-BASE": 1,
                      "E-BASE": 1,
                      "O-BASE": 2,
                      "GM-1": 0.75,
                      "GM-2": 0.75,
                      "GM-3": 0.75,
                      "BRDG-1": 1,
                      "BRDG-2": 1,
                      "BRDG-3": 1,
                      "BRDG-4": 1,
                      "OF": 0.75,
                      "WASTE": 1
                      }

    embedding, skeletons = \
        tbx.generateLayoutSkeletons(layoutSpec=layoutSpec,
                                    embeddingMethod=lyt.DefaultEmbedding(applyForceDirected=True, iteration=200000),
                                    skeletonGenerator=lyt.StraightHalfEdgeSkeletonGenerator(stretchWeights))
    print("SKELETONS GENERATION COMPLETED")

    boundRadiusValues = {"P-BASE": 1,
                         "E-BASE": 1,
                         "O-BASE": 1,
                         "GM-1": 1,
                         "GM-2": 1,
                         "GM-3": 1,
                         "BRDG-1": 0.05,
                         "BRDG-2": 0.05,
                         "BRDG-3": 0.05,
                         "BRDG-4": 0.05,
                         "OF": 1,
                         "WASTE": 1
                         }

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
    print("POLYGON GENERATION COMPLETED")

    influenceMaps = tbx.generateAreaInfluenceMapFromPolygons(polygons=polygons,
                                                             fadeRadius=0.00001,
                                                             mapWidth=200,
                                                             mapHeight=200)
    print("INFLUENCE MAP GENERATION COMPLETED")

    heightMap = GridMap(200, 200)

    landscapes = {"NONE": lnd.LandscapeProfile("NONE", 0, lnd.NONE_ITEM),
                  "GOLD_MINES": lnd.LandscapeProfile("NONE", 0.01, {"GOLD TRACK": 1}),
                  "OIL_FIELD": lnd.LandscapeProfile("POLLUTION", 0.01, {"OIL REFINERY": 1}),
                  "POLLUTED": lnd.LandscapeProfile("POLLUTION", 0.0, lnd.NONE_ITEM)}

    landscapeGenerator_NONE = lnd.SingleProfileLandscapeGenerator(desiredLandscapeName="NONE")
    landscapeGenerator_GM = lnd.SingleProfileLandscapeGenerator(desiredLandscapeName="GOLD_MINES")
    landscapeGenerator_WASTE = lnd.SingleProfileLandscapeGenerator(desiredLandscapeName="POLLUTED")
    landscapeGenerator_OIL = lnd.SingleProfileLandscapeGenerator(desiredLandscapeName="OIL_FIELD")

    landscapeSetting = {"P-BASE": landscapeGenerator_NONE,
                        "E-BASE": landscapeGenerator_NONE,
                        "O-BASE": landscapeGenerator_NONE,
                        "GM-1": landscapeGenerator_GM,
                        "GM-2": landscapeGenerator_GM,
                        "GM-3": landscapeGenerator_GM,
                        "BRDG-1": landscapeGenerator_NONE,
                        "BRDG-2": landscapeGenerator_NONE,
                        "BRDG-3": landscapeGenerator_NONE,
                        "BRDG-4": landscapeGenerator_WASTE,
                        "OF": landscapeGenerator_OIL,
                        "WASTE": landscapeGenerator_WASTE
                        }

    landscapeMaps, surfaceMaps, itemDensityMap, itemTypeMaps, itemLocations = \
        tbx.generateLandscapeData(landscapes=landscapes,
                                  landscapeSetting=landscapeSetting,
                                  mapWidth=200,
                                  mapHeight=200,
                                  influenceMaps=influenceMaps,
                                  heightMap=heightMap)

    print("LANDSCAPE GENERATION COMPLETED")

    marker_spec_1 = mrk.MarkerSpecification(name="P-HQ",
                                            containerArea="P-BASE",
                                            heightPreference=0,
                                            heightImportance=0,
                                            centerPreference=1,
                                            centerImportance=1,
                                            effectorAreas=[],
                                            effectorImportance=0)

    marker_spec_2 = mrk.MarkerSpecification(name="E-HQ",
                                            containerArea="E-BASE",
                                            heightPreference=0,
                                            heightImportance=0,
                                            centerPreference=1,
                                            centerImportance=1,
                                            effectorAreas=[],
                                            effectorImportance=0)

    marker_spec_3 = mrk.MarkerSpecification(name="O-HQ",
                                            containerArea="O-BASE",
                                            heightPreference=0,
                                            heightImportance=0,
                                            centerPreference=1,
                                            centerImportance=1,
                                            effectorAreas=[],
                                            effectorImportance=0)

    marker_spec_4 = mrk.MarkerSpecification(name="OUTPOST-1",
                                            containerArea="O-BASE",
                                            heightPreference=0,
                                            heightImportance=0,
                                            centerPreference=0,
                                            centerImportance=0,
                                            effectorAreas=["BRDG-1"],
                                            effectorImportance=1)

    marker_spec_5 = mrk.MarkerSpecification(name="OUTPOST-2",
                                            containerArea="O-BASE",
                                            heightPreference=0,
                                            heightImportance=0,
                                            centerPreference=0,
                                            centerImportance=0,
                                            effectorAreas=["BRDG-2"],
                                            effectorImportance=1)

    marker_spec_6 = mrk.MarkerSpecification(name="OUTPOST-3",
                                            containerArea="O-BASE",
                                            heightPreference=0,
                                            heightImportance=0,
                                            centerPreference=0,
                                            centerImportance=0,
                                            effectorAreas=["BRDG-3"],
                                            effectorImportance=1)

    marker_placements = tbx.placeMarkers(markerSpecifications=[marker_spec_1,
                                                               marker_spec_2,
                                                               marker_spec_3,
                                                               marker_spec_4,
                                                               marker_spec_5,
                                                               marker_spec_6],
                                         polygons=polygons,
                                         heightMap=heightMap)

    print("MARKER PLACEMENT COMPLETED")

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
    itemColoring = {"GOLD TRACK": ('gold', "o"),
                    "OIL REFINERY": ('black', "^")}
    jDraw.addMultiAreaPolygons(axes, polygons_ecu, None, drawSeeds=False, drawCells=True)
    jDraw.addDictionaryOfLocations(axes, itemLocations, itemColoring, 200, 200)
    jDraw.addAreaLayoutGraph(axes, layoutSpec, embedding, drawNeighbourhoods=False)
    jDraw.showMap("ITEM LOCATIONS")

    _, axes = jDraw.creatMapPlot()
    jDraw.AddMultipleMaps(axes, surfaceMaps, {"NONE": (1, 1, 1),
                                              "POLLUTION": (0.3, 0.3, 0.3)})
    jDraw.addMultiAreaPolygons(axes, polygons_ecu, layoutColoring, drawSeeds=False, drawCells=False)
    jDraw.addAreaLayoutGraph(axes, layoutSpec, embedding, drawNeighbourhoods=False)
    jDraw.showMap("SURFACE MAPS")
