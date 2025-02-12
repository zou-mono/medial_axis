import os

import shapely

from MAT.visualization.visualizer import Visualizer

# points = [
#     (5.5, 4), (4.8, 4.7),
#     (3.5, 4.2),
#     (2.8, 4.9), (3.2, 5.9), (4.8, 7),
#     (6.5, 6.3), (6.8, 5.6), (9, 5),
#     (8.8, 4), (8, 3.2), (8.4, 2.5),
#     (5, 1), (3.85, 1.96), (3.85, 3),
#     (5.5, 3), (5.5, 4)
# ]

# points = [
#     (4.8, 7),
#     (6.5, 6.3), (6.8, 5.6), (9, 5),
#     (8.8, 4), (8, 3.2), (8.4, 2.5),
#     (5, 1), (3.85, 1.96), (3.85, 3),
#     (5.5, 3), (5.5, 4), (4.8, 4.7),
#     (3.5, 4.2),
#     (2.8, 4.9), (3.2, 5.9), (4.8, 7)
# ]
# points = [
#     (6.5, 6.3), (6.8, 5.6), (9, 5),
#     (8.8, 4), (8, 3.2), (8.4, 2.5),
#     (5, 1), (3.85, 1.96), (3.85, 3),
#     (5.5, 3), (5.5, 4), (4.8, 4.7),
#     (3.5, 4.2),
#     (2.8, 4.9), (3.2, 5.9), (4.8, 7),(6.5, 6.3)
# ]
# points.reverse()
#
# poly = shapely.Polygon(points)

# poly = shapely.Polygon(shell=((0, 0),(10, 0),(10, 10),(0, 10)),
#                   holes=(((1,3),(5,3),(5,1),(1,1)),
#                          ((9,9),(9,8),(8,8),(8,9))))

def test_plot_five_points_star(five_pointed_star):
    poly, params = five_pointed_star

    Visualizer(poly) \
        .plot_polygon(poly) \
        .plot_vertices(label=True) \
        .show()


def test_plot_polygon(simple_polygon):
    poly, params = simple_polygon

    if not params:
        Visualizer(poly)\
            .plot_polygon(poly)\
            .plot_vertices(label=True)\
            .show()
