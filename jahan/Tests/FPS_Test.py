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
    layoutSpec.addArea("BASE-A")
    layoutSpec.addArea("BASE-B")
    layoutSpec.addArea("CHOKE")
    layoutSpec.addArea("S-CORR-A")
    layoutSpec.addArea("L-CORR-A")
    layoutSpec.addArea("S-CORR-B")
    layoutSpec.addArea("L-CORR-B")
    layoutSpec.connectAreas("BASE-A", "S-CORR-A")
    layoutSpec.connectAreas("BASE-A", "L-CORR-A")
    layoutSpec.connectAreas("S-CORR-A", "CHOKE")
    layoutSpec.connectAreas("L-CORR-A", "CHOKE")
    layoutSpec.connectAreas("BASE-B", "S-CORR-B")
    layoutSpec.connectAreas("BASE-B", "L-CORR-B")
    layoutSpec.connectAreas("S-CORR-B", "CHOKE")
    layoutSpec.connectAreas("L-CORR-B", "CHOKE")

    #squareSeeds = cnv.SquareCanvasSeedGenerator(20, 20).generate()
    #hexSeeds = cnv.HexagonCanvasSeedGenerator(20, 20).generate()
    radialSeeds = cnv.RadialCanvasSeedGenerator(0.05, 150).generate()
    #loosSeeds = cnv.LooseSquareCanvasSeedGenerator(20, 20, 0.33).generate()
    #randSeeds = cnv.UniformRandomCanvasSeedGenerator(400).generate()
    canvas = cnv.Canvas2D(radialSeeds)

    stretchWeights = {"BASE-A": 0.75,
                      "BASE-B": 0.75,
                      "CHOKE": 1,
                      "S-CORR-A": 1,
                      "L-CORR-A": 2.5,
                      "S-CORR-B": 1,
                      "L-CORR-B": 2.5
                      }

    embedding, skeletons = \
        tbx.generateLayoutSkeletons(layoutSpec=layoutSpec,
                                    embeddingMethod=lyt.DefaultEmbedding(iteration=40000),
                                    skeletonGenerator=lyt.StraightHalfEdgeSkeletonGenerator(stretchWeights))

    boundRadiusValues = {"BASE-A": 0.2,
                         "BASE-B": 0.2,
                         "CHOKE": 0.1,
                         "S-CORR-A": 0.04,
                         "L-CORR-A": 0.04,
                         "S-CORR-B": 0.04,
                         "L-CORR-B": 0.04
                         }

    polygons_ecu = tbx.GeneratePolygonsFromAreaSkeletons(canvas=canvas,
                                                         layoutSpec=layoutSpec,
                                                         skeletons=skeletons,
                                                         BoundRadiusValues=boundRadiusValues,
                                                         distanceFunction=tbx.EuclideanDistanceCalculator(),
                                                         deletionDepth=1)

    #polygons_man = tbx.GeneratePolygonsFromAreaSkeletons(canvas=canvas,
    #                                                     layoutSpec=layoutSpec,
    #                                                     skeletons=skeletons,
    #                                                     BoundRadiusValues=boundRadiusValues,
    #                                                     distanceFunction=tbx.ManhattanDistanceCalculator())

    #polygons_che = tbx.GeneratePolygonsFromAreaSkeletons(canvas=canvas,
    #                                                     layoutSpec=layoutSpec,
    #                                                     skeletons=skeletons,
    #                                                     BoundRadiusValues=boundRadiusValues,
    #                                                     distanceFunction=tbx.ChebyshevDistanceCalculator())
    polygons = polygons_ecu

    heightMap = GridMap(200, 200)

    landscapeProfiles = {
        "NO_COVER":   lnd.LandscapeProfile(surfaceType="NONE", itemDensity=0.0, itemTypes=lnd.NONE_ITEM),
        "COVER":      lnd.LandscapeProfile(surfaceType="NONE", itemDensity=0.01, itemTypes={"COVER": 1})
    }

    landscapeGenerator_cover = lnd.SingleProfileLandscapeGenerator(desiredLandscapeName="COVER")
    landscapeGenerator_empty = lnd.SingleProfileLandscapeGenerator(desiredLandscapeName="NO_COVER")

    landscapeSetting = {"BASE-A": landscapeGenerator_empty,
                        "BASE-B": landscapeGenerator_empty,
                        "CHOKE": landscapeGenerator_cover,
                        "S-CORR-A": landscapeGenerator_empty,
                        "L-CORR-A": landscapeGenerator_empty,
                        "S-CORR-B": landscapeGenerator_empty,
                        "L-CORR-B": landscapeGenerator_empty}

    influenceMaps = tbx.generateAreaInfluenceMapFromPolygons(polygons=polygons,
                                                             fadeRadius=0.001,
                                                             mapWidth=200,
                                                             mapHeight=200)

    landscapeMaps, surfaceMaps, itemDensityMap, itemTypeMaps, itemLocations = \
        tbx.generateLandscapeData(landscapes=landscapeProfiles,
                                  landscapeSetting=landscapeSetting,
                                  mapWidth=200,
                                  mapHeight=200,
                                  influenceMaps=influenceMaps,
                                  heightMap=heightMap)

    marker_spec_1 = mrk.MarkerSpecification(name="SPAWN-A",
                                            containerArea="BASE-A",
                                            heightPreference=0,
                                            heightImportance=0,
                                            centerPreference=0,
                                            centerImportance=0,
                                            effectorAreas=["S-CORR-A"],
                                            effectorImportance=1)

    marker_spec_2 = mrk.MarkerSpecification(name="SPAWN-B",
                                            containerArea="BASE-B",
                                            heightPreference=0,
                                            heightImportance=0,
                                            centerPreference=0,
                                            centerImportance=0,
                                            effectorAreas=["S-CORR-B"],
                                            effectorImportance=1)

    marker_spec_3 = mrk.MarkerSpecification(name="BOMB",
                                            containerArea="CHOKE",
                                            heightPreference=0,
                                            heightImportance=0,
                                            centerPreference=1,
                                            centerImportance=1,
                                            effectorAreas=[],
                                            effectorImportance=0)

    marker_spec_4 = mrk.MarkerSpecification(name="TOWER-A",
                                            containerArea="L-CORR-A",
                                            heightPreference=0,
                                            heightImportance=0,
                                            centerPreference=1,
                                            centerImportance=1,
                                            effectorAreas=["CHOKE"],
                                            effectorImportance=1.5)

    marker_spec_5 = mrk.MarkerSpecification(name="TOWER-B",
                                            containerArea="L-CORR-B",
                                            heightPreference=0,
                                            heightImportance=0,
                                            centerPreference=1,
                                            centerImportance=1,
                                            effectorAreas=["CHOKE"],
                                            effectorImportance=1.5)

    marker_placements = tbx.placeMarkers(markerSpecifications=[marker_spec_1,
                                                               marker_spec_2,
                                                               marker_spec_3,
                                                               marker_spec_4,
                                                               marker_spec_5],
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
    itemColoring = {"COVER": ('red', "s")}
    jDraw.addMultiAreaPolygons(axes, polygons_ecu, None, drawSeeds=False, drawCells=True)
    jDraw.addDictionaryOfLocations(axes, itemLocations, itemColoring, 200, 200)
    jDraw.addAreaLayoutGraph(axes, layoutSpec, embedding, drawNeighbourhoods=False)
    jDraw.showMap("ITEM LOCATIONS")
