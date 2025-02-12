import os.path
from typing import Literal

import numpy as np
from shapely import Polygon, Point, LineString
from shapely.geometry import mapping
from shapely.ops import substring

from MAT.algebra import Algebra
from MAT.graph.element import Element
from MAT.graph.segment import Segment
from MAT.graph.vertex import Vertex
from MAT.graph.voronoi import Mesh, VoronoiEdge, VoronoiRegion
from MAT.gv import POINT_PRECISION_PLACE, point_equals
from MAT.visualization.visualizer import Visualizer
import copy

from chains.DoubleLinkedList import DoubleLinkedList
from chains.chain import Chain
from chains.node import Node

outpath = os.path.abspath("./output/")

if not os.path.exists(outpath):
    os.makedirs(outpath)


class Algorithm:
    def __init__(self):
        self.bisector_dict = {}
        self.min_x = self.max_x = self.min_y = self.max_y = None
        self.bounds = None
        self.mesh = Mesh()
        self.is_ccw = True

    def create_voronoi_diagram(self, poly: Polygon, offset: float = 1):
        self.min_x, self.min_y, self.max_x, self.max_y = poly.bounds
        self.bounds = (self.min_x - offset, self.min_y - offset,
                       self.max_x + offset, self.max_y + offset)

        p = mapping(poly)
        points = list(p['coordinates'][0])

        self.is_ccw = True if Algebra.is_ccw(points) else False

        chains = self.generate_chains(points, self.is_ccw)

        for chain in chains:
            elements = chain.elements

            for e in elements:

                # 添加凹节点处的ve边
                if isinstance(e, Vertex):
                    vr = e.region

                    alg = Algebra(self.bounds)
                    bs1 = alg.bisector(e.prev_segment, e, self.is_ccw)
                    bs2 = alg.bisector(e, e.next_segment, self.is_ccw)

                    bs1_origin, bs1_end = Algebra.origin_and_end_point(bs1.geom)
                    bs2_origin, bs2_end = Algebra.origin_and_end_point(bs2.geom)

                    ve, _ = vr.add_edge(bs1_end, e, edge=bs1)
                    vr.add_edge(e, bs2_end, edge=bs2)
                    vr.current = ve

                    if e.prev_segment.region is None:
                        vr = self.mesh.add_face(e.prev_segment)
                    else:
                        vr = e.prev_segment.region
                    ve, _ = vr.add_edge(bs1_origin, bs1_end, edge=bs1)
                    vr.current = ve

                    if e.next_segment.region is None:
                        vr = self.mesh.add_face(e.next_segment)
                    else:
                        vr = e.next_segment.region
                    ve, _ = vr.add_edge(bs2_end, bs2_origin, edge=bs2)
                    vr.current = ve

                    self.bisector_dict.setdefault((e.prev_segment.index, e.index), bs1)
                    self.bisector_dict.setdefault((e.index, e.next_segment.index), bs2)

                # elif isinstance(e, Segment):
                #     if e.region is None:
                #         vr = self.mesh.add_face(e)
                #     else:
                #         vr = e.region

                # vr.add_edge(e.origin, e.end, geom=e.geom, is_boundary=True)
                # vr.current = 0
        # chains.append(chains.head.data)
        icount = 1
        while len(chains) > 1:
            if len(chains) == 1:
                print("debug")

            c1 = chains.popleft()
            c2 = chains.popleft()

            print("step:{}-{}. Left chain: {}; Right chain: {}".format(icount, icount + 1, c1, c2))

            merged_chain = self.merge_chains(c1, c2)

            if merged_chain is not None:
                chains.prepend(merged_chain)

            Visualizer(poly) \
                .plot_polygon(poly) \
                .plot_edges(self.mesh.edge_map) \
                .savefig(outpath, "{}_{}".format(icount, icount + 1))

            icount += 2

        # print("step:{}-{}. Left chain: {}; Right chain: {}".format(icount, icount + 1, ))
        # self.merge_chains(chains[0], first_chain)
        # Visualizer(poly) \
        #     .plot_polygon(poly) \
        #     .plot_edges(self.mesh.edge_map) \
        #     .savefig(outpath, "{}_{}".format(icount, icount + 1))

        for vr in self.mesh.faces:
            str  = ""
            for ve in vr.traverse():
                str = str + "[{},{}]-".format(ve.origin, ve.end)
            print("Region: {}({}); Edges: {}".format(vr, vr.element, str))

        print(chains)

    def merge_chains(self, c1: Chain, c2: Chain):
        e_left: Element = c1.elements.tail.data
        e_right: Element = c2.elements.head.data

        extend_point = None

        if len(c1.elements) == 1 and len(c2.elements) == 1:
            print("Left: [{}:{}], Right: [{}:{}]".format(e_left.index, e_left, e_right.index,
                                                         e_right))

            alg = Algebra(self.bounds)
            bisector = self.bisector_dict.setdefault((e_left.index, e_right.index),
                                                     alg.bisector(e_left, e_right, is_ccw=self.is_ccw))

            if bisector is None:
                return None

            self.add_bisector_to_region(bisector.geom, e_left, e_right)
        else:
            last_bisector = bisector = None

            self.init_voronoi_edges(c1)
            self.init_voronoi_edges(c2)

            while (e_left.index != c1.elements.head.data.index or
                   e_right.index != c2.elements.tail.data.index):

                # self.update_voronoi_polygon_head(e_left)
                # self.update_voronoi_polygon_head(e_right)

                if e_left.index == 10 and e_right.index == 13:
                    print("debug:{}-{}".format(e_left.index, e_right.index))
                else:
                    pass

                for vr in self.mesh.faces:
                    str  = ""
                    for ve in vr.traverse():
                        str = str + "[{},{}]-".format(ve.origin, ve.end)
                    print("Region: {}({}); Edges: {}".format(vr, vr.element, str))

                print("Left: [{}:{}], Right: [{}:{}]".format(e_left.index, e_left, e_right.index,
                                                             e_right))

                alg = Algebra(self.bounds)

                if bisector is not None:
                    last_bisector = bisector

                bisector = self.bisector_dict.setdefault((e_left.index, e_right.index),
                                                         alg.bisector(e_left, e_right, is_ccw=self.is_ccw))

                if bisector is None:
                    break

                # 从上一个相交点开始，延伸bisector
                if extend_point is None:
                    extend_point = np.array([round(bisector.geom.coords[0][0], POINT_PRECISION_PLACE),
                                             round(bisector.geom.coords[0][1], POINT_PRECISION_PLACE)])
                else:
                    _ = Algebra.split_bisector(extend_point, bisector, last_bisector, e_left, e_right)

                    if _ is not None:
                        bisector = _

                        if point_equals(np.array([bisector.geom.coords[-1][0], bisector.geom.coords[-1][1]]), extend_point):
                            reversed_coords = list(bisector.geom.coords)[::-1]
                            bisector.geom = LineString(reversed_coords)

                        self.bisector_dict.setdefault((e_left.index, e_right.index), bisector)
                    else:
                        bisector = None

                if bisector is None:
                    break

                ve_left, ve_right, intersect_left, intersect_right = self.select_voronoi_edge(bisector, e_left, e_right, extend_point)
                b_continue, e_left, e_right, bisector, extend_point = self.update_voronoi(bisector, ve_left, ve_right, intersect_left, intersect_right, e_left, e_right, extend_point)

                if not b_continue:
                    break

        return c1.merge(c2)

    def select_voronoi_edge(self, bisector, e_left, e_right, extend_point):
        # 定义和bisector的左交点和右交点
        intersect_left = intersect_right = None
        ve_left = ve_right = None

        ve = e_left.region.current
        for ve_left in e_left.region.traverse(ve):
            intersect_left = Algebra.get_intersection_point(ve_left.geom, bisector.geom)
            if not intersect_left is None:
                if not point_equals(np.array([intersect_left.x, intersect_left.y]), extend_point):
                    e_left.region.current = ve_left.next
                    break
                else:
                    intersect_left = None

        ve = e_right.region.current
        for ve_right in e_right.region.traverse(ve, is_ccw=False):
            intersect_right = Algebra.get_intersection_point(ve_right.geom, bisector.geom)
            if not intersect_right is None:
                if not point_equals(np.array([intersect_right.x, intersect_right.y]), extend_point):
                    e_right.region.current = ve_right.prev
                    break
                else:
                    intersect_right = None

        return ve_left, ve_right, intersect_left, intersect_right

    def update_voronoi(self, bisector, ve_left, ve_right, intersect_left, intersect_right, e_left, e_right, extend_point):
        if intersect_left is None and intersect_right is None:
            # self.add_bisector_to_region(bisector, e_left.data.region, e_right.data.region)
            # if last_bisector is None:
            self.add_bisector_to_region(bisector.geom, e_left, e_right)
            return False, None, None, None, None

        elif intersect_left is None and intersect_right is not None:
            if point_equals(np.array([intersect_right.x, intersect_right.y]), extend_point):
                intersect_right = extend_point
            else:
                intersect_right = np.array([intersect_right.x, intersect_right.y])

            if self.is_ccw:
                bisector = self.update_voronoi_edges(bisector, ve_right, intersect_right, e_left, e_right, 'R')
            else:
                bisector = self.update_voronoi_edges(bisector, ve_right, intersect_right, e_left, e_right, 'L')

            extend_point = intersect_right

            if bisector.right_element.index == ve_right.right_element.index:
                e_right = ve_right.right_element
            else:
                e_right = ve_right.left_element

        elif intersect_right is None and intersect_left is not None:
            if point_equals(np.array([intersect_left.x, intersect_left.y]), extend_point):
                intersect_left = extend_point
            else:
                intersect_left = np.array([intersect_left.x, intersect_left.y])

            if self.is_ccw:
                bisector = self.update_voronoi_edges(bisector, ve_left, intersect_left, e_left, e_right, 'L')
            else:
                bisector = self.update_voronoi_edges(bisector, ve_left, intersect_left, e_left, e_right, 'R')

            extend_point = intersect_left

            if bisector.left_element.index == ve_left.right_element.index:
                e_left = ve_left.left_element
            elif bisector.left_element.index == ve_left.left_element.index:
                e_left = ve_left.right_element

        elif intersect_left is not None and intersect_right is not None:
            # 判断哪条边先与延伸bisector相交
            distance_left = bisector.geom.project(Point(intersect_left))
            distance_right = bisector.geom.project(Point(intersect_right))

            if round(distance_left,  POINT_PRECISION_PLACE - 1) == round(distance_right, POINT_PRECISION_PLACE - 1):
                if point_equals(np.array([intersect_left.x, intersect_left.y]), extend_point):
                    intersect_pt = extend_point
                else:
                    intersect_pt = np.array([intersect_left.x, intersect_left.y])

                if self.is_ccw:
                    self.update_voronoi_edges(bisector, ve_left, intersect_pt, e_left, e_right,
                                              'L')
                    bisector = self.update_voronoi_edges(bisector, ve_right, intersect_pt, e_left, e_right,
                                                         'R')
                else:
                    self.update_voronoi_edges(bisector, ve_left, intersect_pt, e_left, e_right,
                                              'R')
                    bisector = self.update_voronoi_edges(bisector, ve_right, intersect_pt, e_left, e_right,
                                                         'L')

                if bisector.left_element.index == ve_left.right_element.index:
                    e_left = ve_left.left_element
                elif bisector.left_element.index == ve_left.left_element.index:
                    e_left = ve_left.right_element

                if bisector.right_element.index == ve_right.right_element.index:
                    e_right = ve_right.left_element
                else:
                    e_right = ve_right.right_element

                extend_point = intersect_pt
            else:
                if (distance_left < distance_right and distance_left > 0) or (distance_right == 0):
                    if point_equals(np.array([intersect_left.x, intersect_left.y]), extend_point):
                        intersect_left = extend_point
                    else:
                        intersect_left = np.array([intersect_left.x, intersect_left.y])

                    if self.is_ccw:
                        bisector = self.update_voronoi_edges(bisector, ve_left, intersect_left, e_left, e_right,
                                                             'L')
                    else:
                        bisector = self.update_voronoi_edges(bisector, ve_left, intersect_left, e_left, e_right,
                                                             'R')

                    extend_point = intersect_left

                    if bisector.left_element.index == ve_left.right_element.index:
                        e_left = ve_left.left_element
                    elif bisector.left_element.index == ve_left.left_element.index:
                        e_left = ve_left.right_element

                elif (distance_right < distance_left and distance_right > 0) or (distance_left == 0):
                    if point_equals(np.array([intersect_right.x, intersect_right.y]), extend_point):
                        intersect_right = extend_point
                    else:
                        intersect_right = np.array([intersect_right.x, intersect_right.y])

                    if self.is_ccw:
                        bisector = self.update_voronoi_edges(bisector, ve_right, intersect_right, e_left, e_right,
                                                             'R')
                    else:
                        bisector = self.update_voronoi_edges(bisector, ve_right, intersect_right, e_left, e_right,
                                                             'L')

                    extend_point = intersect_right

                    if bisector.right_element.index == ve_right.right_element.index:
                        e_right = ve_right.left_element
                    else:
                        e_right = ve_right.right_element

        return True, e_left, e_right, bisector, extend_point

    def init_voronoi_edges(self, chain: Chain):
        for node in chain.elements.traverse():
            current_ve = None

            if isinstance(node.data, Segment):
                start_vertex = node.data.end
            else:
                start_vertex = node.data

            for ve in node.data.region.traverse():
                # if is_segment:
                if ve.origin == start_vertex:
                    node.data.region.current = ve
                    node.data.region.set_head(ve)
                    break
                # else:
                #     if ve.end == start_vertex:
                #         node.data.region.current = ve
                #         node.data.region.set_head(ve)
                #         break
                current_ve = ve

            if current_ve is not None:
                node.data.region.current = current_ve
                node.data.region.set_head(current_ve)

    def update_voronoi_polygon_head(self, ele: Element):
        if isinstance(ele, Segment):
            start_vertex = ele.end
        else:
            start_vertex = ele

        for start_ve in ele.region.traverse():
            if start_ve.origin == start_vertex:
                ele.region.set_head(start_ve)
                break

    def add_bisector_to_region(self, bisector, e_left, e_right):
        if bisector is None:
            return

        if e_left.index == 49 and e_right.index == 10:
            print("debug:{}-{}".format(e_left.index, e_right.index))
        else:
            pass

        bs_origin, bs_end = Algebra.origin_and_end_point(bisector)

        ve_left, _ = e_left.region.add_edge(bs_origin, bs_end, geom=bisector, only_create=True)
        ve_right, _ = e_right.region.add_edge(bs_end, bs_origin, geom=bisector, only_create=True)

        ve_left.left_element = e_left
        ve_left.right_element = e_right
        ve_right.left_element = e_left
        ve_right.right_element = e_right

        left_head = e_left.region.head
        if left_head is None:
            left_tail = None
        else:
            left_tail = e_left.region.head.prev

        right_head = e_right.region.head
        if right_head is None:
            right_tail = None
        else:
            right_tail = e_right.region.head.prev

        if left_head is not None:
            if left_head.origin == ve_left.end:
                e_left.region.prepend(ve_left)
            elif left_head.end == ve_left.origin:
                e_left.region.insert_after(left_head, ve_left)
            elif left_tail.end == ve_left.origin:
                e_left.region.append(ve_left)
            elif left_tail.origin == ve_left.end:
                e_left.region.insert_before(left_tail, ve_left)
            else:
                e_left.region.append(ve_left)
        else:
            e_left.region.append(ve_left)

        if right_head is not None:
            if right_head.origin == ve_right.end:
                e_right.region.prepend(ve_right)
            elif right_head.end == ve_right.origin:
                e_right.region.insert_after(right_head, ve_right)
            elif right_tail.end == ve_right.origin:
                e_right.region.append(ve_right)
            elif right_tail.origin == ve_right.end:
                e_right.region.insert_before(right_tail, ve_right)
            else:
                e_right.region.prepend(ve_right)
        else:
            e_right.region.prepend(ve_right)

        return ve_left, ve_right

    # 经过intersection和split之后，更新相关的的Voronoi边
    # left_or_right表示ve是在bisector左侧还是右侧
    def update_voronoi_edges(self, bisector, split_ve, intersect_point, e_left, e_right,
                             left_or_right: Literal['L', 'R'], add_to_tail=True):
        if e_left.index == 7 and e_right.index == 10:
            print("debug:{}-{}".format(e_left.index, e_right.index))
        else:
            pass

        print("update:[{}]-[{}]".format(split_ve.left_element, split_ve.right_element))

        if not point_equals(np.array([bisector.geom.coords[0][0], bisector.geom.coords[0][1]]), intersect_point):
            bisector.geom = substring(bisector.geom, 0, bisector.geom.project(Point(intersect_point)))

        if not isinstance(bisector.geom, LineString):
            return None

        v_intersect = Vertex(round(intersect_point[0], POINT_PRECISION_PLACE),
                             round(intersect_point[1], POINT_PRECISION_PLACE))

        _bside = Algebra.check_side(Point([split_ve.origin.x, split_ve.origin.y]), bisector.geom)

        if (_bside > 0 and left_or_right == 'L') or (_bside < 0 and left_or_right == 'R'):
            origin_dist, end_dist = 0, split_ve.geom.project(Point([v_intersect.x, v_intersect.y]))
            origin, end = (split_ve.origin, v_intersect)
            # del self.mesh.vertex_map[ve.end]
        else:
            origin_dist, end_dist = split_ve.geom.project(Point([v_intersect.x, v_intersect.y])), split_ve.geom.length
            origin, end = (v_intersect, split_ve.end)
            # del self.mesh.vertex_map[ve.origin]

        # 更新 ve.geom
        geom = substring(split_ve.geom, origin_dist, end_dist)
        region_main = split_ve.region
        region_twin = split_ve.twin.region

        bs_origin, bs_end = Algebra.origin_and_end_point(bisector.geom)
        bs_ve_left, _ = e_left.region.add_edge(bs_origin, bs_end, bisector.geom, only_create=True)
        bs_ve_right, _ = e_right.region.add_edge(bs_end, bs_origin, bisector.geom, only_create=True)
        bs_ve_left.left_element = e_left
        bs_ve_left.right_element = e_right
        bs_ve_right.left_element = e_left
        bs_ve_right.right_element = e_right

        if geom.length > 0:
            # 有可能由于精度导致错误，所以手动更新首末节点
            coords = list(geom.coords)
            coords[0] = (origin.x, origin.y)  # 修改第一个点
            coords[-1] = (end.x, end.y)  # 修改最后一个点
            geom = LineString(coords)

            new_ve, _ = region_main.add_edge(origin, end, geom=geom, only_create=True)
            new_twin_ve, _ = region_twin.add_edge(end, origin, geom=geom, only_create=True)

            new_ve.left_element = split_ve.left_element
            new_ve.right_element = split_ve.right_element
            new_twin_ve.left_element = split_ve.twin.left_element
            new_twin_ve.right_element = split_ve.twin.right_element

            if new_ve != split_ve and new_ve != split_ve.twin:
                region_main.insert_after(split_ve, new_ve)
                region_twin.insert_after(split_ve.twin, new_twin_ve)
                region_main.delete_edge(split_ve)
                region_twin.delete_edge(split_ve.twin)

                if new_ve.end == bs_ve_left.origin:
                    if new_ve.prev.origin == bs_ve_left.origin:
                        ve = new_ve.prev
                        region_main.delete_edge(ve)
                        ve.twin.region.delete_edge(ve.twin)
                        del self.mesh.edge_map[(ve.origin, ve.end)]
                        del self.mesh.edge_map[(ve.end, ve.origin)]
                    if add_to_tail:
                        region_main.insert_after(new_ve, bs_ve_left)

                if bs_ve_left.end == new_ve.origin:
                    if new_ve.prev.origin == bs_ve_left.origin:
                        ve = new_ve.prev
                        region_main.delete_edge(ve)
                        ve.twin.region.delete_edge(ve.twin)
                        del self.mesh.edge_map[(ve.origin, ve.end)]
                        del self.mesh.edge_map[(ve.end, ve.origin)]
                    if add_to_tail:
                        region_main.insert_before(new_ve, bs_ve_left)

                if new_ve.end == bs_ve_right.origin:
                    if new_ve.prev.origin == bs_ve_right.origin:
                        ve = new_ve.prev
                        region_main.delete_edge(ve)
                        ve.twin.region.delete_edge(ve.twin)
                        del self.mesh.edge_map[(ve.origin, ve.end)]
                        del self.mesh.edge_map[(ve.end, ve.origin)]
                    if add_to_tail:
                        region_main.insert_after(new_ve, bs_ve_right)

                if bs_ve_right.end == new_ve.origin:
                    if new_ve.prev.origin == bs_ve_right.origin:
                        ve = new_ve.prev
                        region_main.delete_edge(ve)
                        ve.twin.region.delete_edge(ve.twin)
                        del self.mesh.edge_map[(ve.origin, ve.end)]
                        del self.mesh.edge_map[(ve.end, ve.origin)]
                    if add_to_tail:
                        region_main.insert_before(new_ve, bs_ve_right)

                # ve_left, ve_right = self.add_bisector_to_region(bisector, e_left.data.region, e_right.data.region)
                # del self.mesh.edge_map[(split_ve.origin, split_ve.end)]
                # del self.mesh.edge_map[(split_ve.end, split_ve.origin)]
                if (split_ve.origin, split_ve.end) in self.mesh.edge_map:
                    del self.mesh.edge_map[(split_ve.origin, split_ve.end)]
                if (split_ve.end, split_ve.origin) in self.mesh.edge_map:
                    del self.mesh.edge_map[(split_ve.end, split_ve.origin)]
            else:
                if split_ve.end == bs_ve_left.origin:
                    split_ve.region.insert_after(split_ve, bs_ve_left)
                if split_ve.end == bs_ve_right.origin:
                    split_ve.region.insert_after(split_ve, bs_ve_right)
                if split_ve.origin == bs_ve_left.end:
                    split_ve.region.insert_before(split_ve, bs_ve_left)
                if split_ve.origin == bs_ve_right.end:
                    split_ve.region.insert_before(split_ve, bs_ve_right)
                # else:
                #     raise ValueError("current_edge is not in the same region as e_left and e_right")

            if region_main.current == split_ve:
                region_main.current = new_ve
            if region_twin.current == split_ve.twin:
                region_twin.current = new_twin_ve
        else:
            print("debug: geom.length == 0")
            if split_ve.origin == bs_ve_left.origin:
                split_ve.region.insert_after(split_ve, bs_ve_left)
            if split_ve.origin == bs_ve_right.origin:
                split_ve.region.insert_after(split_ve, bs_ve_right)
            if split_ve.end == bs_ve_left.end:
                split_ve.region.insert_before(split_ve, bs_ve_left)
            if split_ve.end == bs_ve_right.end:
                split_ve.region.insert_before(split_ve, bs_ve_right)

            region_main.delete_edge(split_ve)
            region_twin.delete_edge(split_ve.twin)
            del self.mesh.edge_map[(split_ve.origin, split_ve.end)]
            del self.mesh.edge_map[(split_ve.end, split_ve.origin)]

        if add_to_tail:
            left_head = e_left.region.head
            if left_head is None:
                left_tail = None
            else:
                left_tail = e_left.region.head.prev

            right_head = e_right.region.head
            if right_head is None:
                right_tail = None
            else:
                right_tail = e_right.region.head.prev

            if region_main != e_left.region and e_left.region != region_twin:
                # e_left.region.append(bs_ve_left)
                if left_head is None:
                    e_left.region.append(bs_ve_left)
                else:
                    if left_head.origin == bs_ve_left.end:
                        e_left.region.prepend(bs_ve_left)

                    elif left_head.end == bs_ve_left.origin:
                        e_left.region.insert_after(left_head, bs_ve_left)

                    elif left_tail.end == bs_ve_left.origin:
                        e_left.region.append(bs_ve_left)

                    elif left_tail.origin == bs_ve_left.end:
                        e_left.region.insert_before(left_tail, bs_ve_left)

            if region_twin != e_right.region and e_right.region != region_main:
                if right_head is None:
                    e_right.region.append(bs_ve_right)
                else:
                    if right_head.origin == bs_ve_right.end:
                        e_right.region.prepend(bs_ve_right)

                    elif right_head.end == bs_ve_right.origin:
                        e_right.region.insert_after(right_head, bs_ve_right)

                    elif right_tail.end == bs_ve_right.origin:
                        e_right.region.append(bs_ve_right)

                    elif right_tail.origin == bs_ve_right.end:
                        e_right.region.insert_before(right_tail, bs_ve_right)

                # e_right.region.append(bs_ve_right)
            # else:
            #     print("region_twin == e_right.data.region")

        # self.add_bisector_to_region(bisector, region_main, region_twin, new_ve)

        # for ve in e_right.region.traverse():

        self.bisector_dict.setdefault((e_left.index, e_right.index), bisector)

        return bisector

    def generate_chains(self, points, is_ccw=True):
        chains = DoubleLinkedList()
        elements = DoubleLinkedList()
        origin = None
        points = points[:-1]
        included_angle = -1

        iterate_index, first_no = self.find_first_element(points, is_ccw=is_ccw)

        # iterate_index.append(first_no)
        first_vertex = None
        icount = 0
        for idx, idx_pt in enumerate(iterate_index):
            current = iterate_index[idx]
            prev = iterate_index[idx - 1]
            next = iterate_index[(idx + 1) % len(iterate_index)]

            vector1 = np.array((points[prev][0] - points[current][0],
                                points[prev][1] - points[current][1]), dtype=float)
            vector2 = np.array((points[next][0] - points[current][0],
                                points[next][1] - points[current][1]), dtype=float)

            included_angle = Algebra.angle_between_vecters(vector1, vector2, is_ccw=is_ccw)
            # print("{}: {}".format(idx, included_angle))

            if idx == 0:
                first_vertex = Vertex(points[current][0], points[current][1], 0, current, included_angle)
                self.mesh.add_vertex(first_vertex)
                origin = first_vertex
                continue

            end = Vertex(points[current][0], points[current][1], idx, current, included_angle)
            self.mesh.add_vertex(end)
            seg = Segment(origin, end, num=idx)
            origin.next_segment = seg
            end.prev_segment = seg
            # he = HalfEdge(seg, origin=origin, twin=Segment(end, origin, num=idx))
            if included_angle < 180:
                seg.index = icount
                elements.append(seg)

                vr = self.mesh.add_face(seg)
                # vr.current = seg
                # vr.add_edge(seg.origin, seg.end, geom=seg.geom, is_boundary=True)

                icount += 1

                chain = Chain(elements)
                chains.append(chain)
                elements = DoubleLinkedList()
            else:
                seg.index = icount
                elements.append(seg)
                vr = self.mesh.add_face(seg)
                # vr.current = seg
                # vr.add_edge(seg.origin, seg.end, geom=seg.geom, is_boundary=True)

                icount += 1
                end.index = icount
                elements.append(end)

                vr = self.mesh.add_face(end)
                # vr.current = end

                icount += 1

            origin = end

        # end = Vertex(points[iterate_index[0]][0], points[iterate_index[0]][1], iterate_index[0], included_angle)
        # seg = Segment(origin, first_vertex, num= len(iterate_index))
        seg = Segment(origin, first_vertex, num=len(iterate_index))
        origin.next_segment = seg
        seg.index = icount
        first_vertex.prev_segment = seg

        elements.append(seg)
        vr = self.mesh.add_face(seg)
        # vr.current = seg
        # vr.add_edge(seg.origin, seg.end, geom=seg.geom, is_boundary=True)

        chain = Chain(elements)
        chains.append(chain)

        return chains

    @staticmethod
    def find_first_element(points, is_ccw=True, bfirst=True):
        first_no = -1

        for idx, point in enumerate(points):
            pt1 = points[idx - 1]
            pt0 = points[idx]
            pt2 = points[(idx + 1) % len(points)]

            vector1 = np.array([pt1[0] - pt0[0], pt1[1] - pt0[1]], dtype=float)
            vector2 = np.array([pt2[0] - pt0[0], pt2[1] - pt0[1]], dtype=float)

            included_angle = Algebra.angle_between_vecters(vector1, vector2, is_ccw=is_ccw)

            if included_angle < 180:
                first_no = idx
                break

        # 重新调整节点顺序
        total = len(points)
        new_index = list(range(first_no, total)) + list(range(0, first_no))

        if bfirst:
            return new_index, first_no
        else:
            return new_index
