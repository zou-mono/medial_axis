from shapely.geometry import Polygon
from shapely import geometry, set_precision


def test_precision():
    # 创建一个多边形
    # polygon = Polygon([(0.123456, 0.654321), (1.123456, 0.654321), (1.123456, 1.654321), (0.123456, 1.654321)])
    polygon = Polygon([(0.123456, 1.654321), (1.123456, 1.654321), (1.123456, 0.654321), (0.123456, 0.654321)])

    print(list(polygon.exterior.coords))

    # 使用 set_precision 来设置精度
    polygon_precise = set_precision(polygon, grid_size=0.0001, mode="pointwise")

    print(list(polygon_precise.exterior.coords))

    polygon_precise = set_precision(polygon, grid_size=0.0001, mode="keep_collapsed")

    print(list(polygon_precise.exterior.coords))
