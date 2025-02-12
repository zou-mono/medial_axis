import math

import numpy as np
import shapely
from matplotlib import pyplot as plt
from numpy import linspace
from shapely import LineString
from shapely.geometry import mapping

from MAT.graph.line import Ray, Parabola
from MAT.visualization.visualizer import Visualizer

from MAT.algebra import Algebra
from MAT.graph.segment import Segment
from MAT.graph.vertex import Vertex


def test_ccw():
    points = [
        (4.8, 7),
        (6.5, 6.3), (6.8, 5.6), (9, 5),
        (8.8, 4), (8, 3.2), (8.4, 2.5),
        (5, 1), (3.85, 1.96), (3.85, 3),
        (5.5, 3), (5.5, 4), (4.8, 4.7),
        (3.5, 4.2),
        (2.8, 4.9), (3.2, 5.9), (4.8, 7)
    ]

    print(Algebra.is_ccw(points))


def test_perpendicular_distance():
    pt0 = Vertex(0, 5)
    pt1 = Vertex(1, 1)
    pt2 = Vertex(2, 1)
    seg = Segment(pt1, pt2)

    alg = Algebra()
    print(alg._perpendicular_distance(pt0, seg))


def test_parabola():
    points = [
        (4.8, 7),
        (6.5, 6.3), (6.8, 5.6), (9, 5),
        (8.8, 4), (8, 3.2), (8.4, 2.5),
        (5, 1), (3.85, 1.96), (3.85, 3),
        (5.5, 3), (5.5, 4), (4.8, 4.7),
        (3.5, 4.2),
        (2.8, 4.9), (3.2, 5.9), (4.8, 7)
    ]

    poly = shapely.Polygon(points)

    pt = Vertex(0, 5)
    # pt = Vertex(6, 4)
    # pt = Vertex(7, 3)
    pt2 = Vertex(4, 2)
    pt1 = Vertex(8, 5)
    seg = Segment(pt1, pt2)

    alg = Algebra()
    parabola = alg._parabola(pt, seg)
    f = parabola.focus
    v = parabola.vertex

    x = linspace(-10, 10, 100)
    y = parabola.func(x)

    ax = plt.subplot(aspect=1)
    # x_ticks = np.linspace(-5, 10, 5)
    # plt.xticks(x_ticks)
    # plt.yticks(x_ticks)

    ax.plot(y[:, 0], y[:, 1])
    ax.plot(x, x ** 2 / (2 * float(f)))
    ax.plot(linspace(-2, 10, 100), (3 * linspace(-2, 10, 100) - 4) / 4)
    ax.scatter(pt.x, pt.y)
    ax.scatter(pt1.x, pt1.y)
    ax.scatter(pt2.x, pt2.y)
    # ax.scatter(6.24, 3.68)
    ax.scatter(v.x, v.y)

    pt = Vertex(8, 5)
    pt1 = Vertex(0, 5)
    pt2 = Vertex(4, 2)
    seg = Segment(pt1, pt2)
    parabola = alg._parabola(pt, seg)

    x = linspace(-10, 10, 100)
    y = parabola.func(x)
    ax.plot(y[:, 0], y[:, 1])

    plt.show()


def test_bisector():
    points = [
        (4.8, 7),
        (6.5, 6.3), (6.8, 5.6), (9, 5),
        (8.8, 4), (8, 3.2), (8.4, 2.5),
        (5, 1), (3.85, 1.96), (3.85, 3),
        (5.5, 3), (5.5, 4), (4.8, 4.7),
        (3.5, 4.2),
        (2.8, 4.9), (3.2, 5.9), (4.8, 7)
    ]
    # points.reverse()

    poly = shapely.Polygon(points)

    ax = plt.subplot(aspect=1)

    v0 = Vertex(4.8, 7, 0)
    v1 = Vertex(3.2, 5.9, 1)
    v2 = Vertex(2.8, 4.9, 2)

    e1 = Segment(v0, v1, 1)
    e2 = Segment(v1, v2, 2)

    # e2 = Segment(Vertex(3.2, 5.9), Vertex(2.8, 4.9))

    ray = Algebra.bisector(e1, e2)
    ray_start = ray.start_point
    # x = linspace(0, 10, 100)
    x = 1
    y = ray_start + x * ray.direction
    # y = func(x)
    ax.plot([ray_start[0], y[0]], [ray_start[1], y[1]], color="blue")
    ax.plot([e1.origin.x, e1.end.x], [e1.origin.y, e1.end.y], color="grey")
    ax.plot([e2.origin.x, e2.end.x], [e2.origin.y, e2.end.y], color="grey")

    vector0 = np.array([y[0] - ray_start[0], y[1] - ray_start[1]])
    vector1 = np.array([e1.origin.x - e1.end.x, e1.origin.y - e1.end.y])
    vector2 = np.array([e2.end.x - e2.origin.x, e2.end.y - e2.origin.y])

    alg = Algebra()
    angle1 = alg.angle_between_vecters2(vector1, vector0)
    angle2 = alg.angle_between_vecters2(vector0, vector2)
    angle3 = alg.angle_between_vecters2(vector1, vector2)

    assert (math.isclose(angle1, angle2))

    ray = Algebra.bisector(v1, e2, is_ccw=False)
    ray_start = ray.start_point
    # ray_start = np.array([ray.O.x, ray.O.y])
    y = ray_start + 1 * ray.direction
    ax.plot([ray_start[0], y[0]], [ray_start[1], y[1]], color="red")
    # ax.plot([v1.x, v1.y], [e2.origin.y, e2.end.y])
    ax.scatter(v1.x, v1.y)

    plt.show()


def test_ray_intersection():
    points = [
        (4.8, 7),
        (6.5, 6.3), (6.8, 5.6), (9, 5),
        (8.8, 4), (8, 3.2), (8.4, 2.5),
        (5, 1), (3.85, 1.96), (3.85, 3),
        (5.5, 3), (5.5, 4), (4.8, 4.7),
        (3.5, 4.2),
        (2.8, 4.9), (3.2, 5.9), (4.8, 7)
    ]
    points.reverse()
    points = points[:-1]
    poly = shapely.Polygon(points)

    e1 = Segment(Vertex(4.8, 7), Vertex(3.2, 5.9))
    e2 = Segment(Vertex(3.2, 5.9), Vertex(2.8, 4.9))
    ray = Algebra.bisector(e1, e2)

    _, closest_pt = Algebra.closest_intersection(ray.start_point, ray.direction, points)
    print(closest_pt)

    # .plot_vertices(label=False) \
    Visualizer(poly) \
        .plot_polygon(poly) \
        .plot_vertices([[closest_pt[0], closest_pt[1]]], label=True) \
        .plot_bisector(ray, 10) \
        .show()


# @pytest.mark.parametrize('reverse', [True, False])
def test_bisector_between_segments(simple_polygon):
    polygon, params = simple_polygon

    e1 = Segment(Vertex(4.8, 7, 0), Vertex(3.2, 5.9, 1), 1)
    e2 = Segment(Vertex(3.5, 4.2, 2), Vertex(4.8, 4.7, 3), 2)
    e3 = Segment(Vertex(4.8, 4.7, 4), Vertex(3.5, 4.2, 2), 3)
    e4 = Segment(Vertex(3, 3, 5), Vertex(10, 3, 6), 4)
    e5 = Segment(Vertex(8, 9, 7), Vertex(4, 9, 8), 5)
    e6 = Segment(Vertex(8.8, 4, 9), Vertex(8, 3.2, 10), 6)
    e7 = Segment(Vertex(8.4, 2.5, 11), Vertex(5, 1, 12), 7)
    e8 = Segment(Vertex(3.2, 5.9, 1), Vertex(2.8, 4.9, 13), 8)
    e9 = Segment(Vertex(6.8, 5.6, 14), Vertex(6.5, 6.3, 15), 9)
    e10 = Segment(Vertex(6.5, 6.3, 15), Vertex(4.8, 7, 0), 10)

    e11 = Segment(Vertex(5.5, 4, 16), Vertex(5.5, 3, 17), 11)
    e12 = Segment(Vertex(5, 1, 18), Vertex(8.4, 2.5, 19), 12)

    alg = Algebra()

    print("当前的测试参数:{}".format(params))

    ray0 = alg.bisector(e11, e12, is_ccw=params).geom

    Visualizer(polygon) \
        .plot_polygon(polygon) \
        .plot_bisector(ray0) \
        .show()

    ray1 = alg.bisector(e1, e2).geom
    ray2 = alg.bisector(e2, e1).geom

    Visualizer(polygon) \
        .plot_polygon(polygon) \
        .plot_bisector(ray1) \
        .show()

    Visualizer(polygon) \
        .plot_polygon(polygon) \
        .plot_bisector(ray2) \
        .show()

    ray3 = alg.bisector(e1, e3, is_ccw=params).geom

    if ray3 is not None:
        Visualizer(polygon) \
            .plot_polygon(polygon) \
            .plot_bisector(ray3, [-10, 10]) \
            .show()

    ray4 = alg.bisector(e4, e5, is_ccw=params).geom

    if isinstance(ray4, LineString):
        Visualizer(polygon) \
            .plot_polygon(polygon) \
            .plot_bisector(ray4) \
            .show()
    ray5 = alg.bisector(e6, e7).geom

    Visualizer(polygon) \
        .plot_polygon(polygon) \
        .plot_bisector(ray5, [-10, 10]) \
        .show()

    if params:
        ray6 = alg.bisector(e10, e1, is_ccw=params).geom
    else:
        ray6 = alg.bisector(e1.reverse(), e10.reverse(), is_ccw=params).geom

    Visualizer(polygon) \
        .plot_polygon(polygon) \
        .plot_bisector(ray6) \
        .show()


def test_bisector_between_vertex_and_segment(simple_polygon):
    polygon, params = simple_polygon

    e1 = Vertex(4.8, 7, 0)
    e2 = Segment(Vertex(4.8, 4.7, 4), Vertex(3.5, 4.2, 2), 3)
    e3 = Segment(Vertex(4.8, 4.7, 4), Vertex(5.5, 4, 2), 3)

    ray1 = Algebra.bisector(e1, e2, is_ccw=params).geom
    ray2 = Algebra.bisector(e3.reverse(), e1, is_ccw=params).geom

    Visualizer(polygon) \
        .plot_polygon(polygon) \
        .plot_bisector(ray1) \
        .plot_bisector(ray2) \
        .show()


# @pytest.mark.parametrize('reverse', [True, False])
def test_intersection(five_pointed_star):
    polygon, params = five_pointed_star

    p = mapping(polygon)
    points = list(p['coordinates'][0])

    v0 = Vertex(points[0][0], points[0][1], 0)
    v1 = Vertex(points[1][0], points[1][1], 1)
    v2 = Vertex(points[2][0], points[2][1], 2)
    v3 = Vertex(points[3][0], points[3][1], 3)

    e0 = Segment(v0, v1, 0)
    e1 = Segment(v1, v2, 1)
    e2 = Segment(v2, v3, 2)

    ray1 = Algebra.bisector(e1, e2, is_ccw=params)
    ray2 = Algebra.bisector(v1, e1, is_ccw=params)
    ray3 = Algebra.bisector(e0, v1, is_ccw=params)

    intersection_pt1 = Algebra.intersection(ray1, ray2)
    print(intersection_pt1)
    intersection_pt2 = Algebra.intersection(ray1, ray3)
    print(intersection_pt2)

    Visualizer(polygon) \
        .plot_polygon(polygon) \
        .plot_bisector(ray1.geom) \
        .plot_bisector(ray2, 10) \
        .plot_bisector(ray3, 10) \
        .plot_intersection([intersection_pt1, intersection_pt2]) \
        .show()

    # .plot_intersection([intersection_pt1]) \


def test_parabola_intersection(simple_polygon):
    # pt = Vertex(5, 5)
    pt = Vertex(10, 3)
    pt1 = Vertex(8, 5)
    pt2 = Vertex(4, 2)
    seg = Segment(pt1, pt2)

    # pt = Vertex(0, 5)
    # pt1 = Vertex(4, -5)
    # pt2 = Vertex(8, -5)
    # seg = Segment(pt2, pt1)

    alg = Algebra()
    parabola = alg._parabola(pt, seg)

    # ray = Ray(Vertex(-10, 2.5), np.array([15, 17.5]))
    # ray = Ray(Vertex(-3, 6), np.array([15, 17.5]))
    # ray = Ray(Vertex(2, -5), np.array([15, 17.5]))
    ray = Ray(Vertex(15, 10), np.array([-15, -17.5]))

    r = parabola.rotate_matrix * np.array([[1, -1], [-1, 1]])
    # r = parabola.rotate_matrix

    # start_pt = r @ ray.start_point + np.array([-parabola.vertex.x, -parabola.vertex.y])
    # 先平移再旋转
    start_pt = r @ (ray.start_point + np.array([-parabola.vertex.x, -parabola.vertex.y]))
    direction = r @ ray.direction

    origin_ray = Ray(Vertex(start_pt[0], start_pt[1]), direction)
    origin_parabola = Parabola(parabola.focus, Vertex(0, 0), rotate=False)

    origin_intersection_pt = Algebra.intersection(origin_ray, origin_parabola)

    (Visualizer(simple_polygon, canvas_offset=10, figsize=(10, 10))
     .plot_polygon(simple_polygon)
     .plot_bisector(origin_ray)
     .plot_bisector(origin_parabola, rotate=False)
     .plot_intersection(origin_intersection_pt, color='green', s=100) \
     .show())

    intersection_pt = ((parabola.rotate_matrix @ np.array(origin_intersection_pt).T).T
                       + np.array([parabola.vertex.x, parabola.vertex.y]))

    # ao1 = (np.dot(parabola.rotate_matrix,
    #              np.array([origin_intersection_pt[0][0], origin_intersection_pt[0][1]])).T +
    #  np.array([parabola.vertex.x, parabola.vertex.y]))
    #
    # ao2 = (np.dot(parabola.rotate_matrix,
    #              np.array([origin_intersection_pt[1][0], origin_intersection_pt[1][1]])).T +
    #       np.array([parabola.vertex.x, parabola.vertex.y]))

    # d1 = (ao1[0] - parabola.vertex.x) ** 2 + (ao1[1] - parabola.vertex.y) ** 2
    # d2 = origin_intersection_pt[0][0] ** 2 + origin_intersection_pt[0][1] ** 2

    print(intersection_pt[0])

    (Visualizer(simple_polygon, canvas_offset=10, figsize=(10, 10))
     .plot_polygon(simple_polygon)
     .plot_bisector(ray)
     .plot_bisector(parabola)
     .plot_intersection(intersection_pt, color='green', s=100) \
     .show())


def test_segments_intersection(simple_polygon2):
    polygon, params = simple_polygon2

    coords = list(polygon.exterior.coords)

    v0 = Vertex(coords[0][0], coords[0][1], 0)
    v1 = Vertex(coords[1][0], coords[1][1], 1)
    v2 = Vertex(coords[2][0], coords[2][1], 2)
    v3 = Vertex(coords[3][0], coords[3][1], 3)
    v4 = Vertex(coords[4][0], coords[4][1], 4)
    v5 = Vertex(coords[5][0], coords[5][1], 5)

    e1 = Segment(v0, v1, 1)
    e2 = Segment(v1, v2, 2)

    alg = Algebra()

    ray1 = alg.bisector(e1, e2, is_ccw=params).geom

    if isinstance(ray1, LineString):
        Visualizer(polygon) \
            .plot_polygon(polygon) \
            .plot_bisector(ray1) \
            .show()

