import os

from shapely import LineString
from shapely.geometry import mapping

from MAT.algebra import Algebra
from MAT.algorithm import Algorithm as Voronoi
from osgeo import ogr
from shapely.geometry import Polygon

from MAT.graph.segment import Segment
from MAT.graph.vertex import Vertex
from MAT.visualization.visualizer import Visualizer

outpath = os.path.abspath("./output/")

def test_create_voronoi_five_star(five_pointed_star):
    algo = Voronoi()
    poly, param = five_pointed_star

    if not param:
        algo.create_voronoi_diagram(poly)


def test_create_voronoi_simple_polygon(simple_polygon):
    algo = Voronoi()
    poly, param = simple_polygon

    if not param:
        algo.create_voronoi_diagram(poly)


def test_shapefile_polygon():
    # 加载Shapefile
    shapefile_path = "../data/polygons.shp"
    driver = ogr.GetDriverByName('ESRI Shapefile')
    dataSource = driver.Open(shapefile_path, 0)  # 0 means read-only

    # 获取图层
    layer = dataSource.GetLayer()

    icount = 0
    # 假设我们读取第一个Polygon
    for feature in layer:
        # 获取几何对象
        geom = feature.GetGeometryRef()

        if icount != 3:
            icount += 1
            continue

        # 检查是否为Polygon类型
        if geom.GetGeometryType() == ogr.wkbPolygon:
            # 获取Polygon的外环（边界）
            exterior_ring = geom.GetGeometryRef(0)

            # 提取外环的点坐标
            coordinates = []
            for i in range(exterior_ring.GetPointCount()):
                point = exterior_ring.GetPoint(i)
                coordinates.append((point[0], point[1]))

            # 创建Shapely Polygon对象
            shapely_polygon = Polygon(coordinates)

            # Visualizer(shapely_polygon) \
            #     .plot_polygon(shapely_polygon) \
            #     .plot_vertices(label=True) \
            #     .savefig(outpath, "{}_{}".format(icount, icount + 1))

            algo = Voronoi()
            algo.create_voronoi_diagram(shapely_polygon)

            print(icount)
            icount += 1

    # 关闭数据源
    dataSource = None


def test_shapefile_polygon2():
    # 加载Shapefile
    shapefile_path = "../data/polygons.shp"
    driver = ogr.GetDriverByName('ESRI Shapefile')
    dataSource = driver.Open(shapefile_path, 0)  # 0 means read-only

    # 获取图层
    layer = dataSource.GetLayer()

    icount = 0
    # 假设我们读取第一个Polygon
    for feature in layer:
        # 获取几何对象
        geom = feature.GetGeometryRef()

        if icount != 0:
            icount += 1
            continue

        # 检查是否为Polygon类型
        if geom.GetGeometryType() == ogr.wkbPolygon:
            # 获取Polygon的外环（边界）
            exterior_ring = geom.GetGeometryRef(0)

            # 提取外环的点坐标
            coordinates = []
            for i in range(exterior_ring.GetPointCount()):
                point = exterior_ring.GetPoint(i)
                coordinates.append((point[0], point[1]))

            # 创建Shapely Polygon对象
            shapely_polygon = Polygon(coordinates)

            # Visualizer(shapely_polygon) \
            #     .plot_polygon(shapely_polygon) \
            #     .plot_vertices(label=True) \
            #     .savefig(outpath, "{}_{}".format(icount, icount + 1))

            min_x, min_y, max_x, max_y = shapely_polygon.bounds
            bounds = (min_x - 1, min_y - 1, max_x + 1, max_y + 1)

            alg = Algebra(bounds)

            # algo.create_voronoi_diagram(shapely_polygon)
            e1 = Segment(Vertex(10.9, 61.832, 4), Vertex(10.642, 59.946, 5), 0)
            e2 = Segment(Vertex(9.699, 61.489, 10), Vertex(11.9, 66.404, 0), 1)

            ray1 = alg.bisector(e2, e1, is_ccw=False).geom

            if isinstance(ray1, LineString):
                Visualizer(shapely_polygon) \
                    .plot_polygon(shapely_polygon) \
                    .plot_bisector(ray1) \
                    .show()

            print(icount)
            icount += 1

    # 关闭数据源
    dataSource = None

