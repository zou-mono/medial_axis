import decimal
import math
from typing import Union

import numpy as np
from numpy.linalg import norm
from shapely import LineString, Point, set_precision
from shapely.ops import split, snap, nearest_points

from MAT.graph.element import Element
# from MAT.graph.element import Element
from MAT.graph.line import Line, Ray, Parabola
from MAT.graph.segment import Segment
from MAT.graph.vertex import Vertex
from MAT.graph.voronoi import VoronoiEdge

from MAT.gv import EQUAL_TOLERANCE, EQUAL_RELATIVE_TOLERANCE, POINT_PRECISION, POINT_PRECISION_PLACE


class Algebra:
    def __init__(self, bounds=None):
        self._bounds = bounds

    @staticmethod
    def is_in_range(x_min, x, x_max, rel_tol=EQUAL_RELATIVE_TOLERANCE, abs_tol=EQUAL_TOLERANCE):
        # return (math.isclose(x_min, x, rel_tol=rel_tol, abs_tol=abs_tol) or x_min < x) and \
        #     (math.isclose(x, x_max, rel_tol=rel_tol, abs_tol=abs_tol) or x < x_max)
        return (math.isclose(x_min, x, abs_tol=abs_tol) or x_min < x) and \
            (math.isclose(x, x_max, abs_tol=abs_tol) or x < x_max)

    # @staticmethod
    def bisector(self, e1: Union[Element, Vertex, Segment], e2: Union[Element, Vertex, Segment], is_ccw=True):
        geom = None

        if e1.index == 4 and e2.index == 11:  # 17 6
            print("bisector-debug:{}-{}".format(e1.index, e2.index))
        else:
            pass

        if isinstance(e1, Vertex) and isinstance(e2, Segment):
            edge = Algebra._handle_vertex_segment(e1, e2, is_ccw)
        elif isinstance(e1, Segment) and isinstance(e2, Vertex):
            edge = Algebra._handle_vertex_segment(e2, e1, is_ccw)
        elif isinstance(e1, Segment) and isinstance(e2, Segment):
            edge = Algebra._handle_segment_segment(self._bounds, e1, e2, is_ccw)
        elif isinstance(e1, Vertex) and isinstance(e2, Vertex):
            edge = Algebra._handle_vertex_vertex(e1, e2, is_ccw)
        else:
            return None

        if edge is not None:
            if isinstance(edge, Line) or isinstance(edge, Ray):
                geom = Algebra.get_segments_from_bounds(self._bounds, edge)
            else:
                geom = edge.geom

        if geom is not None:
            if geom.is_empty or geom.length == 0 or (geom.coords[0] == geom.coords[-1] and len(geom.coords) == 2):
                return None

            p_geom = set_precision(geom, POINT_PRECISION, mode='pointwise')
            ve = VoronoiEdge(geom=p_geom, left_element=e1, right_element=e2)
            return ve
        else:
            return None

    @staticmethod
    def get_segments_from_bounds(bounds, edge):
        x_min, y_min, x_max, y_max = bounds

        dx, dy = edge.direction
        start_point = edge.start_point

        # 如果 start_point 为 None，则处理直线，否则处理射线
        if isinstance(edge, Ray):
            px, py = start_point
        elif isinstance(edge, Line):
            px, py = start_point

        intersections = []

        def check_intersection(t, x_bound, y_bound):
            if isinstance(edge, Ray) and t < 0:
                return
            x = px + t * dx
            y = py + t * dy
            if Algebra.is_in_range(x_min, x, x_max) and Algebra.is_in_range(y_min, y, y_max):
                intersections.append((x, y))

        if dx != 0:
            check_intersection((x_min - px) / dx, x_min, None)
            check_intersection((x_max - px) / dx, x_max, None)

        if dy != 0:
            check_intersection((y_min - py) / dy, None, y_min)
            check_intersection((y_max - py) / dy, None, y_max)

        # intersections[0] if isinstance(self._edge, Ray) and intersections else intersections

        # 对于直线情况，返回两个交点；对于射线情况，返回起点和射线方向上的第一个交点
        if isinstance(edge, Ray):
            if len(intersections) > 0:
                return LineString((start_point, intersections[0]))
            else:
                return None
        else:
            if len(intersections) == 2:
                if np.dot(edge.direction,
                          np.array([intersections[0][0] - intersections[1][0], intersections[0][1] - intersections[1][1]])) > 0:
                    return LineString((intersections[1], intersections[0]))
                else:
                    return LineString((intersections[0], intersections[1]))
            else:
                return None

    @staticmethod
    def _handle_segment_segment(bounds, segment1, segment2, is_ccw):
        def calculate_bisector(origin, seg1_origin, seg2_end):
            vector1 = np.array([seg1_origin.x - origin.x, seg1_origin.y - origin.y])
            vector2 = np.array([seg2_end.x - origin.x, seg2_end.y - origin.y])
            direction = Algebra.normalize(Algebra.normalize(vector1) + Algebra.normalize(vector2))

            b_collinear = False

            # 如果是两条边夹角180度的共线情况
            if np.isnan(direction).all():
                b_collinear = True
                if is_ccw:
                    direction = np.array([0, 1])
                else:
                    direction = np.array([0, -1])

            return b_collinear, Ray(origin, direction)

        if segment1.end.key == segment2.origin.key or segment1.origin.key == segment2.end.key:
            # 根据情况确定起始点和对称线段的端点
            if segment1.end.key == segment2.origin.key:
                start_vertex, pt_A, pt_B = segment1.end, segment1.origin, segment2.end
            else:
                start_vertex, pt_A, pt_B = segment1.origin, segment1.end, segment2.origin

            origin = np.array([start_vertex.x, start_vertex.y])

            # 计算距离并生成角平分线
            distance_A = np.linalg.norm(np.array([pt_A.x, pt_A.y]) - origin)
            distance_B = np.linalg.norm(np.array([pt_B.x, pt_B.y]) - origin)

            b_collinear, bisector_ray = calculate_bisector(start_vertex, pt_A, pt_B)

            # # 选择较短的线段
            # short_pt, short_seg = (pt_A, segment1) if distance_A <= distance_B else (pt_B, segment2)
            #
            # # 计算交点
            # ray2 = Algebra._handle_vertex_segment(short_pt, short_seg, is_ccw)
            # intersection_point = Algebra.intersection(ray2, bisector_ray)
            #
            # if intersection_point is not None:
            #     if segment1.end.key == segment2.origin.key:
            #         return Segment(Vertex(origin[0], origin[1]), Vertex(intersection_point[0], intersection_point[1]))
            #     else:
            #         return Segment(Vertex(intersection_point[0], intersection_point[1]), Vertex(origin[0], origin[1]))
            # else:
            #     return None

            if not b_collinear:
                # 选择较短的线段
                short_pt, short_seg = (pt_A, segment1) if distance_A <= distance_B else (pt_B, segment2)

                # 计算交点
                ray2 = Algebra._handle_vertex_segment(short_pt, short_seg, is_ccw)
                intersection_point = Algebra.intersection(ray2, bisector_ray)

                if intersection_point is not None:
                    if segment1.end.key == segment2.origin.key:
                        return Segment(Vertex(origin[0], origin[1]), Vertex(intersection_point[0], intersection_point[1]))
                    else:
                        return Segment(Vertex(intersection_point[0], intersection_point[1]), Vertex(origin[0], origin[1]))
                else:
                    return None
            else:
                geom = Algebra.get_segments_from_bounds(bounds, bisector_ray)
                if isinstance(geom, LineString):
                    return Segment(Vertex(origin[0], origin[1]), Vertex(geom.coords[-1][0], geom.coords[-1][1]))
                else:
                    return None

        start_vertex = Algebra.intersection_between_segments(segment1, segment2)
        sorted_points = None
        if start_vertex is None:  # 两条线平行
            M = [(segment1.origin.x + segment1.end.x + segment2.origin.x + segment2.end.x) / 4,
                 (segment1.origin.y + segment1.end.y + segment2.origin.y + segment2.end.y) / 4]
            start_vertex = Vertex(M[0], M[1])
            direction = np.array([segment1.end.x - segment1.origin.x, segment1.end.y - segment1.origin.y])

            bisector_ray = Line(start_vertex, direction)
            sorted_points = Algebra.range_of_bisector_ray(segment1, segment2, bisector_ray, is_ccw)
        else:
            _, bisector_ray = calculate_bisector(start_vertex, segment1.origin, segment2.end)
            in_segment, _ = Algebra._find_in_segment(segment1, segment2, start_vertex)

            if in_segment is None:
                # 两条线段不平行且不共点，则取四个端点到平分射线交点的中间段作为bisector的范围
                sorted_points = Algebra.range_of_bisector_ray(segment1, segment2, bisector_ray, is_ccw)

        if sorted_points is None:
            return None
        else:
            new_seg = Segment(Vertex(sorted_points[1][0], sorted_points[1][1]),
                              Vertex(sorted_points[2][0], sorted_points[2][1]))
            return new_seg

    @staticmethod
    def _find_in_segment(segment1, segment2, start_vertex):
        for segment in [segment1, segment2]:
            vector1 = np.array([segment.origin.x - start_vertex.x, segment.origin.y - start_vertex.y])
            vector2 = np.array([segment.end.x - start_vertex.x, segment.end.y - start_vertex.y])
            if math.isclose(abs(Algebra.angle_between_vecters2(vector1, vector2)), 180, abs_tol=EQUAL_TOLERANCE):
                return segment, segment1 if segment == segment2 else segment2
        return None, None

    @staticmethod
    def compute_direction(vector, is_ccw):
        rotation_matrix = np.array([[0, 1], [-1, 0]]) if is_ccw else np.array([[0, -1], [1, 0]])
        return np.dot(rotation_matrix, vector)

    @staticmethod
    def _handle_vertex_vertex(vertex1: Vertex, vertex2: Vertex, is_ccw):
        # 计算中点
        midpoint = [(vertex1.x + vertex2.x) / 2, (vertex1.y + vertex2.y) / 2]

        # 计算连线的方向向量
        direction_vector = np.array([vertex2.x - vertex1.x, vertex2.y - vertex1.y])

        # 计算垂直方向向量
        if is_ccw:
            perpendicular_direction = np.array([-direction_vector[1], direction_vector[0]])
        else:
            perpendicular_direction = np.array([direction_vector[1], -direction_vector[0]])

        return Line(Vertex(midpoint[0], midpoint[1]), perpendicular_direction)

    @staticmethod
    def _handle_vertex_segment(vertex, segment, is_ccw):
        if vertex.key == segment.origin.key:
            vector = np.array([segment.end.x - segment.origin.x, segment.end.y - segment.origin.y])
            direction = Algebra.compute_direction(vector, is_ccw)
            return Ray(vertex, -direction)
        elif vertex.key == segment.end.key:
            vector = np.array([segment.origin.x - segment.end.x, segment.origin.y - segment.end.y])
            direction = Algebra.compute_direction(vector, is_ccw)
            return Ray(vertex, direction)
        else:
            parabola = Algebra._parabola(vertex, segment)
            r = parabola.rotate_matrix * np.array([[1, -1], [-1, 1]])
            o, d = np.array([segment.origin.x, segment.origin.y]), np.array([segment.end.x, segment.end.y])

            r_o = r @ (o + np.array([-parabola.vertex.x, -parabola.vertex.y]))
            r_d = r @ (d + np.array([-parabola.vertex.x, -parabola.vertex.y]))

            x = np.linspace(r_o[0], r_d[0], 100)
            y = parabola.func(x)

            mat = (parabola.rotate_matrix @ np.vstack((x, y))).T + np.array([parabola.vertex.x, parabola.vertex.y])
            coords = list(map(tuple, mat))
            parabola.geom = LineString(coords)
            return parabola

    # 计算每个点在直线上的参数值 t
    @staticmethod
    def calculate_line_t(point, r0, direction):
        diff = np.array(point) - np.array(r0)
        t = np.dot(diff, direction) / np.dot(direction, direction)
        return t

    @staticmethod
    def range_of_bisector_ray(segment1, segment2, bisector_ray, is_ccw):
        o_ray1 = Algebra._handle_vertex_segment(segment1.origin, segment1, is_ccw)
        d_ray1 = Algebra._handle_vertex_segment(segment1.end, segment1, is_ccw)
        o_ray2 = Algebra._handle_vertex_segment(segment2.origin, segment2, is_ccw)
        d_ray2 = Algebra._handle_vertex_segment(segment2.end, segment2, is_ccw)

        o_pt1 = Algebra.intersection(o_ray1, bisector_ray)
        d_pt1 = Algebra.intersection(d_ray1, bisector_ray)
        o_pt2 = Algebra.intersection(o_ray2, bisector_ray)
        d_pt2 = Algebra.intersection(d_ray2, bisector_ray)

        if o_pt1 is None:
            o_pt1 = bisector_ray.start_point
        if d_pt1 is None:
            d_pt1 = bisector_ray.start_point
        if o_pt2 is None:
            o_pt2 = bisector_ray.start_point
        if d_pt2 is None:
            d_pt2 = bisector_ray.start_point

        # if o_pt1 is None or d_pt1 is None or o_pt2 is None or d_pt2 is None:
        #     return None

        if isinstance(bisector_ray, Ray):
            origin = bisector_ray.start_point

            distance_A = np.linalg.norm(o_pt1 - origin)
            distance_B = np.linalg.norm(d_pt1 - origin)
            distance_C = np.linalg.norm(o_pt2 - origin)
            distance_D = np.linalg.norm(d_pt2 - origin)

            points_with_distances = [
                (o_pt1, distance_A),
                (d_pt1, distance_B),
                (o_pt2, distance_C),
                (d_pt2, distance_D)
            ]

            # 根据距离对点进行排序
            sorted_points_with_distances = sorted(points_with_distances, key=lambda x: x[1])

            # 提取排序后的点
            sorted_points = [point for point, _ in sorted_points_with_distances]

            return sorted_points

        elif isinstance(bisector_ray, Line):
            # 构造直线的参数方程
            # 直线方程：x = x0 + t * a, y = y0 + t * b
            # 选择一个点作为基准点 (x0, y0)
            direction = bisector_ray.direction
            points = [o_pt1, d_pt1, o_pt2, d_pt2]

            # 计算每个点的参数值 t
            t_values = [Algebra.calculate_line_t(point, bisector_ray.start_point, direction) for point in points]
            # 根据参数值 t 对点进行排序
            sorted_points = [point for _, point in sorted(zip(t_values, points), key=lambda pair: pair[0])]

            return sorted_points

    @staticmethod
    def is_point_on_segment(pt: Vertex, segment: Segment):
        # 提取坐标
        x1, y1 = segment.origin.x, segment.origin.y
        x2, y2 = segment.end.x, segment.end.y
        x, y = pt.x, pt.y

        # 计算向量 AB 和 AP
        AB_x, AB_y = x2 - x1, y2 - y1
        AP_x, AP_y = x - x1, y - y1

        # 计算叉积
        cross_product = AB_x * AP_y - AB_y * AP_x

        # 如果叉积不为零，则点不共线
        if abs(cross_product) > EQUAL_TOLERANCE:  # 允许一定的浮点数误差
            return False

        # 计算向量长度
        def vector_length(x, y):
            return math.sqrt(x**2 + y**2)

        # 检查距离关系
        AB_length = vector_length(AB_x, AB_y)
        AP_length = vector_length(AP_x, AP_y)
        BP_length = vector_length(x - x2, y - y2)

        # 验证 P 是否在 A 和 B 之间
        return math.isclose(AP_length + BP_length, AB_length, abs_tol=EQUAL_TOLERANCE)

    @staticmethod
    def is_point_on_ray(pt: Vertex, ray: Ray):

        ray_origin, ray_direction = ray.start_point, ray.direction

        # 计算点到射线起点的向量
        vector_to_point = np.array([pt.x, pt.y]) - ray_origin
        # 计算向量与射线方向的点积
        dot_product = np.dot(vector_to_point, ray_direction)
        # 检查点是否在射线上
        if dot_product >= 0:
            # 计算向量的模长
            vector_length = np.linalg.norm(vector_to_point)
            # 计算射线方向的模长
            direction_length = np.linalg.norm(ray_direction)
            # 检查向量是否与射线方向平行
            if np.isclose(vector_length * direction_length, dot_product):
                return True
        return False

    @staticmethod
    def get_intersection_point(geom1, geom2):
        snapped_geom1 = snap(geom1, geom2, tolerance=POINT_PRECISION)

        # 求交点
        intersection1 = snapped_geom1.intersection(geom2)

        # 使用 snap 对齐两条线，公差设置为 1e-9
        snapped_geom2 = snap(geom2, geom1, tolerance=POINT_PRECISION)

        # 求交点
        intersection2 = snapped_geom2.intersection(geom1)

        # 检查是否有交点
        if not intersection1.is_empty:
            if isinstance(intersection1, Point):
                intersection1 = Point(round(intersection1.x, POINT_PRECISION_PLACE),
                                      round(intersection1.y, POINT_PRECISION_PLACE))
                return intersection1
            else:
                return None
        elif not intersection2.is_empty:
            if isinstance(intersection2, Point):
                intersection2 = Point(round(intersection2.x, POINT_PRECISION_PLACE),
                                      round(intersection2.y, POINT_PRECISION_PLACE))
                return intersection2
            else:
                return None
        else:
            return None

    @staticmethod
    def intersection(e1: Union[Ray, Line, Parabola, Segment], e2: Union[Ray, Line, Parabola, Segment]):
        def _ray_line_intersection(ray: Ray, line: Line):
            x0, y0 = ray.start_point
            a, b = ray.direction

            A = line.direction[1]
            B = -line.direction[0]
            C = -(A * line.start_point[0] + B * line.start_point[1])

            # 直线方程：Ax + By + C = 0
            # 射线方程：x = x0 + t * a, y = y0 + t * b
            # 将射线方程代入直线方程，求解 t
            denominator = A * a + B * b
            if denominator == 0:
                return None  # 直线和射线平行，无交点

            t = -(A * x0 + B * y0 + C) / denominator

            # 判断 t 是否在射线的范围内（t >= 0）
            if t < 0:
                return None  # 交点在射线起点之前，不在射线范围内

            # 计算交点坐标
            return np.array([x0 + t * a, y0 + t * b])

        def _ray_ray_intersection(ray1: Ray, ray2: Ray):
            # 起点和方向
            x1, y1 = ray1.start_point
            dx1, dy1 = ray1.direction
            x2, y2 = ray2.start_point
            dx2, dy2 = ray2.direction

            # 构建方程组的矩阵表示
            A = np.array([[dx1, -dx2], [dy1, -dy2]])
            B = np.array([x2 - x1, y2 - y1])

            try:
                # 求解 t1 和 t2
                t1, t2 = np.linalg.solve(A, B)
            except np.linalg.LinAlgError:
                return None  # 无解，射线平行或重合

            # 确保交点在射线的正方向上
            if t1 >= 0 and t2 >= 0:
                intersection_x = x1 + t1 * dx1
                intersection_y = y1 + t1 * dy1
                return np.array([intersection_x, intersection_y])
            else:
                return None  # 交点不在正方向上

        def _ray_parabola_intersection(ray: Ray, parabola: Parabola):
            x0, y0 = ray.start_point
            a, b = ray.direction
            f = float(parabola.focus)

            # 计算参数 t 的方程： y0 + bt = (1/(4f))*(x0 + at)^2
            A = 1 / (4 * f) * a ** 2
            B = 1 / (2 * f) * x0 * a - b
            C = 1 / (4 * f) * x0 ** 2 - y0

            # 判别式
            discriminant = B ** 2 - 4 * A * C

            if discriminant < 0:
                return None
            elif discriminant <= EQUAL_TOLERANCE:
                t = -B / (2 * A)
                x, y = x0 + a * t, y0 + b * t
                return [(x, y)]
            else:
                t1 = (-B + np.sqrt(discriminant)) / (2 * A)
                t2 = (-B - np.sqrt(discriminant)) / (2 * A)

                # 确保交点在射线的正方向上
                sorts = sorted([t for t in [t1, t2] if t > 0])

                # t = min(t for t in [t1, t2] if t >= 0)

                # x1, y1 = x0 + a * t1, y0 + b * t1
                # x2, y2 = x0 + a * t2, y0 + b * t2
                # x_min, y_min = x0 + a * t, y0 + b * t

                res = [np.array([x0 + a * s, y0 + b * s]) for s in sorts]

                return res

        def _ray_segment_intersection(ray: Ray, segment: Segment):
            r0 = np.array([ray.start_point[0], ray.start_point[1]])
            d = ray.direction
            p0 = np.array([segment.origin.x, segment.origin.y])
            p1 = np.array([segment.end.x, segment.end.y])

            if Algebra.is_point_on_ray(segment.origin, ray):
                return p0
            elif Algebra.is_point_on_ray(segment.end, ray):
                return p1

            # 计算线段的方向向量
            p1_p0 = segment.direction

            # 构建方程组的系数矩阵和常数向量
            A = np.array([[-d[0], p1_p0[0]], [-d[1], p1_p0[1]]])
            b = np.array([p0[0] - r0[0], p0[1] - r0[1]])

            # 解方程组
            try:
                t, s = np.linalg.solve(A, b)
            except np.linalg.LinAlgError:
                return None  # 无解或无穷多解

            # 检查解的有效性
            if t >= 0 and 0 <= s <= 1:
                intersection_point = r0 + t * d
                return intersection_point
            else:
                return None

        if isinstance(e1, Ray) and isinstance(e2, Ray):
            return _ray_ray_intersection(e1, e2)
        elif isinstance(e1, Ray) and isinstance(e2, Parabola):
            return _ray_parabola_intersection(e1, e2)
        elif isinstance(e1, Parabola) and isinstance(e2, Ray):
            return _ray_parabola_intersection(e2, e1)
        elif isinstance(e1, Ray) and isinstance(e2, Line):
            return _ray_line_intersection(e1, e2)
        elif isinstance(e2, Ray) and isinstance(e1, Line):
            return _ray_line_intersection(e2, e1)
        elif isinstance(e1, Ray) and isinstance(e2, Segment):
            return _ray_segment_intersection(e1, e2)
        elif isinstance(e2, Ray) and isinstance(e1, Segment):
            return _ray_segment_intersection(e2, e1)

    # @njit(cache=True, nogil=True)
    @staticmethod
    def normalize(vector):
        return vector / np.linalg.norm(vector)

    @staticmethod
    def angle_between_vecters(v1, v2, is_ccw=True):
        # print(np.linalg.det(np.stack((v1[-2:], v2[-2:]))))
        # print(np.dot(v1, v2))
        if not is_ccw:
            angle = np.math.atan2(np.linalg.det(np.stack((v1[-2:], v2[-2:]))), np.dot(v1, v2))
        else:
            angle = np.math.atan2(np.linalg.det(np.stack((v2[-2:], v1[-2:]))), np.dot(v2, v1))
            # if not orientation:
        # angle = abs(angle)

        # res = abs(np.degrees(angle))
        res = np.degrees(angle)

        if res < 0:
            res = 360 + res

        return res

    @staticmethod
    def angle_between_vecters2(v1, v2):
        # v1和v2的夹角，如果为正则是逆时针夹角，为负是顺时针夹角
        # print(np.linalg.det(np.stack((v1[-2:], v2[-2:]))))
        # print(np.dot(v1, v2))
        angle = np.math.atan2(np.linalg.det(np.stack((v1[-2:], v2[-2:]))), np.dot(v1, v2))
        res = np.degrees(angle)
        return res

    @staticmethod
    def angle_between_lines(self, line1, line2, deg=True):
        coords_1 = line1.coords
        coords_2 = line2.coords

        line1_vertical = (coords_1[1][0] - coords_1[0][0]) == 0.0
        line2_vertical = (coords_2[1][0] - coords_2[0][0]) == 0.0

        # Vertical lines have undefined slope, but we know their angle in rads is = 90° * π/180
        if line1_vertical and line2_vertical:
            # Perpendicular vertical lines
            return 0.0
        if line1_vertical or line2_vertical:
            # 90° - angle of non-vertical line
            non_vertical_line = line2 if line1_vertical else line1

            _arc = abs((90.0 * np.pi / 180.0) - np.arctan(self._slope(non_vertical_line)))
            if deg:
                return np.degrees(_arc)
            else:
                return _arc

        m1 = self._slope(line1)
        m2 = self._slope(line2)

        _arc = np.arctan((m1 - m2)/(1 + m1*m2))

        if deg:
            return np.degrees(_arc)
        else:
            return _arc

    def _slope(self, line: LineString):
        # Assignments made purely for readability. One could opt to just one-line return them
        x0 = line.coords[0][0]
        y0 = line.coords[0][1]
        x1 = line.coords[1][0]
        y1 = line.coords[1][1]
        return (y1 - y0) / (x1 - x0)

    @staticmethod
    def is_ccw(pr: list):
        """Return the signed area enclosed by a ring using the linear time
        algorithm at http://www.cgafaq.info/wiki/Polygon_Area. A value >= 0
        indicates a counter-clockwise oriented ring."""
        xs, ys = map(list, zip(*pr))
        xs.append(xs[1])
        ys.append(ys[1])
        signed_area = sum(xs[i]*(ys[i+1]-ys[i-1]) for i in range(1, len(pr))) / 2.0

        if signed_area >= 0:
            return True
        else:
            return False

    # @staticmethod
    # def bisector(self, a, b):
    #     if a is Segment and b is Segment:

    # def _bisector_between_point_and_segment(self, pt: Vertex, seg: Segment):
    #
    #
    @staticmethod
    def _parabola(pt: Vertex, seg: Segment):
        #  点是否在线的左边
        is_left = Algebra._check_side(pt, seg)

        focus: Vertex = pt

        vector_u = np.array([seg.end.x - seg.origin.x, seg.end.y - seg.origin.y])

        f = float(Algebra._perpendicular_distance(focus, seg) / 2)

        # sin_theta = 2 * f / decimal.Decimal.sqrt((pt.xd - seg.origin.xd) ** 2 + (pt.yd - seg.origin.yd) ** 2)
        # l = decimal.Decimal.sqrt(1 - sin_theta ** 2) * norm(np.array([pt.xd - seg.origin.xd, pt.yd - seg.origin.yd]))
        # unit_u = norm(vector_u)

        if is_left > 0:
            vector_v = np.array([vector_u[1] * -1, vector_u[0]])
        elif is_left < 0:
            vector_v = np.array([vector_u[1], vector_u[0] * -1])
        else:
            raise ValueError("focus is on the directrix, cannot create parabola!")

        unit_v = norm(vector_v)
        vertex = Vertex(-1 * vector_v[0] * f / unit_v + focus.x, -1 * vector_v[1] * f / unit_v + focus.y)

        # if self._check_foot_position([pt.x - seg.origin.x, pt.y - seg.origin.y],
        #                              [float(vector_u[0]), float(vector_u[1])], is_left) < 0:
        #     foot_point = Vertex(-l * vector_u[0] / unit_u + seg.origin.xd, -l * vector_u[1] / unit_u + seg.origin.yd)
        # else:
        #     foot_point = Vertex(l * vector_u[0] / unit_u + seg.origin.xd, l * vector_u[1] / unit_u + seg.origin.yd)

        vector_vertical = [0, float(f)]
        rotate_angle = Algebra.angle_between_vecters2([float(focus.x - vertex.x), float(focus.y - vertex.y)], vector_vertical)
        # rotate_angle = Algebra.angle_between_vecters2([(vertex.x - focus.x),  (vertex.y - focus.y)], vector_vertical)

        rotate_angle = math.radians(rotate_angle)
        rotate_matrix = np.array([[math.cos(rotate_angle), math.sin(rotate_angle)],
                                  [-1 * math.sin(rotate_angle), math.cos(rotate_angle)]])

        # reverse_rotate_matrix = np.array([[math.cos(rotate_angle), -1 * math.sin(rotate_angle)],
        #                                   [math.sin(rotate_angle), math.cos(rotate_angle)]])

        return Parabola(focus=f, vertex=vertex, rotate=False, rotate_matrix=rotate_matrix,
                        vector_x=vector_u, vector_y=vector_v)

    @staticmethod
    def _check_side(pt: Vertex, seg: Segment):
        return (seg.end.xd - seg.origin.xd) * (pt.yd - seg.origin.yd) - \
            (seg.end.yd - seg.origin.yd) * (pt.xd - seg.origin.xd)

    # @staticmethod
    # def check_side(pt: np.array, seg: np.array):
    #     return (seg[1][0] - seg[0][0]) * (pt[1] - seg[0][1]) - \
    #         (seg[1][1] - seg[0][1]) * (pt[0] - seg[0][0])

    @staticmethod
    def check_side(pt: Point, seg: LineString):
        coords = list(seg.coords)
        total_cross = 0

        # 将 LineString 分成每个线段
        for i in range(len(coords) - 1):
            # 取每个线段的两个端点
            A = coords[i]
            B = coords[i + 1]

            # 计算向量 AB 和 AP
            AB = (B[0] - A[0], B[1] - A[1])
            AP = (pt.x - A[0], pt.y - A[1])

            # 计算二维叉积
            cross = AB[0] * AP[1] - AB[1] * AP[0]

            # 计算叉积并累加
            total_cross += cross

        if total_cross != 0:
            return total_cross  # 点在线的右边
        else:
            # 如果点不在任何线段的左边或右边，可能在同一直线上
            return 0

    @staticmethod
    def _perpendicular_distance(pt: Vertex, line: Segment):
        p1 = np.array([pt.xd, pt.yd])
        p2 = np.array([line.origin.xd, line.origin.yd])
        p3 = np.array([line.end.xd, line.end.yd])

        return np.abs(norm(np.cross(p3 - p2, p3 - p1))) / norm(p3 - p2)

    #  判断垂足是否落在线段外部
    def _check_foot_position(self, v1, v2, is_left):
        if is_left > 0:
            included_angle = self.angle_between_vecters(v1, v2)
        else:
            included_angle = self.angle_between_vecters(v1, v2, is_ccw=False)

        return True if (included_angle > 90) else False

    @staticmethod
    def intersection_between_segments(segment1: Segment, segment2: Segment):
        x1, y1 = segment1.origin.x, segment1.origin.y
        x2, y2 = segment1.end.x, segment1.end.y
        x3, y3 = segment2.origin.x, segment2.origin.y
        x4, y4 = segment2.end.x, segment2.end.y

        # 计算方向向量
        d1 = np.array([x2 - x1, y2 - y1])
        d2 = np.array([x4 - x3, y4 - y3])

        # 设置矩阵方程
        A = np.array([
            [d1[0], -d2[0]],
            [d1[1], -d2[1]]
        ])
        b = np.array([x3 - x1, y3 - y1])

        try:
            # 求解线性方程组
            t, s = np.linalg.solve(A, b)

            # 计算交点
            px = x1 + t * d1[0]
            py = y1 + t * d1[1]

            return Vertex(px, py)
        except np.linalg.LinAlgError:
            # 线性方程组没有解，表示线段平行或重合
            return None

    @staticmethod
    def intersect_ray_segment(O, direction, P1, P2):
        """
        计算射线O + t*d与线段P1P2的交点。
        返回t和交点坐标。如果没有交点，返回None。
        """
        # 边向量
        v = P2 - P1
        # 射线与边的参数解
        denom = np.cross(direction, v)

        if np.abs(denom) < EQUAL_TOLERANCE:
            return None

        t = np.cross((P1 - O), v) / denom
        u = np.cross((P1 - O), direction) / denom

        if t <= 0 or u < 0 or u > 1:
            return None

        intersection = O + t * direction
        return t, intersection

    @staticmethod
    def closest_intersection(O, direction, polygon):
        """
        找出射线O + t*d与凹多边形最近的交点
        """
        closest_t = float('inf')
        closest_point = None

        n = len(polygon)
        for i in range(n):
            P1 = np.array([polygon[i][0], polygon[i][1]])
            P2 = np.array([polygon[(i + 1) % n][0], polygon[(i + 1) % n][1]])

            result = Algebra.intersect_ray_segment(O, direction, P1, P2)
            if result is not None:
                t, intersection = result
                print(intersection)
                if t < closest_t:
                    closest_t = t
                    closest_point = intersection

        return closest_t, closest_point

    @staticmethod
    def euclidean_dist_points(pt1, pt2):
        return ((pt1[0] - pt2[0]) ** 2 + (pt1[1] - pt2[1]) ** 2) ** 0.5

    @staticmethod
    def line_merge(line1: LineString, line2: LineString, reverse=False):
        line1_coords = list(line1.coords)
        line2_coords = list(line2.coords)

        if reverse:
            line2_coords.reverse()

        merged_coords = line1_coords[:-1] + line2_coords
        return LineString(merged_coords)

    @staticmethod
    def origin_and_end_point(geom: LineString):
        # geom = set_precision(geom, POINT_PRECISION, mode='pointwise)
        return Vertex(geom.coords[0][0], geom.coords[0][1]), Vertex(geom.coords[-1][0], geom.coords[-1][1])
        # return Vertex(round(geom.coords[0][0], POINT_PRECISION_PLACE), round(geom.coords[0][1], POINT_PRECISION_PLACE)), \
        #     Vertex(round(geom.coords[-1][0], POINT_PRECISION_PLACE), round(geom.coords[-1][1], POINT_PRECISION_PLACE))

    @staticmethod
    def foot_of_perpendicular(point, line):
        # 获取线段的两个端点
        A = np.array(line.coords[0])  # 线段起点
        B = np.array(line.coords[1])  # 线段终点
        P = np.array([point.x, point.y])  # 点的坐标

        # 向量 AB 和 AP
        AB = B - A
        AP = P - A

        # 计算 t 值（投影比例系数）
        t = np.dot(AP, AB) / np.dot(AB, AB)

        # 根据 t 计算垂足坐标 H
        H = A + t * AB

        # 返回垂足坐标和 t 值
        return Point(H), t

    @staticmethod
    def split_line_by_point(split_point, line, tor=POINT_PRECISION):
        minimum_distance = nearest_points(split_point, line)[0]
        res = split(snap(line, minimum_distance, tor*10), minimum_distance)

        return res

    @staticmethod
    def split_bisector(split_point, bisector: VoronoiEdge, last_bisector: VoronoiEdge, left_element, right_element):
        # bisector_geom = bisector.geom
        split_point = Point(split_point)
        split_lines = Algebra.split_line_by_point(split_point, bisector.geom).geoms

        if len(split_lines) == 1:
            if split_lines[0].length > 0:
                bisector.geom = split_lines[0]
                return bisector
            else:
                return None

        if len(split_lines) != 2:
            return None

        after_point = split_lines[1].interpolate(0.001, normalized=True)

        def _create_line(point, elem: Element):
            if isinstance(elem, Vertex):
                return LineString([point.coords[0], [elem.x, elem.y]])
            elif isinstance(elem, Segment):
                foot_point, _ = Algebra.foot_of_perpendicular(point, elem.geom)
                return LineString([point.coords[0], foot_point])

        after_line1 = _create_line(after_point, left_element)
        after_line2 = _create_line(after_point, right_element)

        if ((not after_line1.intersection(last_bisector.geom).is_empty) or
                (not after_line2.intersection(last_bisector.geom).is_empty)):
            bisector.geom = split_lines[0]
            # return split_lines[0]
        else:
            bisector.geom = split_lines[1]
            # return split_lines[1]
        return bisector