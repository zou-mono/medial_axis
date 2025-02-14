import numpy as np
import shapely
from rtree import index
from shapely import LineString, Point

# from MAT.algebra import Algebra
from MAT.graph.element import Element
from MAT.graph.vertex import Vertex
from MAT.gv import POINT_PRECISION, POINT_PRECISION_PLACE, EQUAL_TOLERANCE


class Mesh:
    def __init__(self):
        self.vertices = []  # 存储所有顶点
        # self.edges = []  # 存储voronoi边
        self.faces = []  # 存储所有面
        self.vertex_map = {}  # 使用字典存储顶点的位置到顶点对象的映射
        self.edge_map = {}  # 使用字典将顶点对映射到半边
        self.face_map = {}
        self.vertex_idx = index.Index()

    def add_vertex(self, vertex: Vertex = None):
        if vertex in self.vertex_map:
            return self.vertex_map[vertex]

        new_point = Point(vertex.x, vertex.y)
        new_point_bbox = (new_point.x - EQUAL_TOLERANCE, new_point.y - EQUAL_TOLERANCE, new_point.x + EQUAL_TOLERANCE, new_point.y + EQUAL_TOLERANCE) # 获取点的边框

        # 查询可能与新点重合的点
        possible_matches = list(self.vertex_idx.intersection(new_point_bbox))

        # 检查新点与可能重合的点之间的距离
        for i in possible_matches:
            existing_vertex = self.vertices[i]
            if point_duplicate(new_point, Point(existing_vertex.x, existing_vertex.y)):
                # 如果距离小于容忍度，则认为是重合的
                return existing_vertex

        # 如果没有重合点，则添加新点
        vertex.id = len(self.vertices)
        self.vertices.append(vertex)
        self.vertex_map[vertex] = vertex
        self.vertex_idx.insert(len(self.vertices) - 1, new_point_bbox)
        return vertex

        # # 判断顶点是否已经在mesh中
        # if vertex in self.vertex_map:
        #     vertex = self.vertex_map[vertex]
        # else:
        #     vertex.id = len(self.vertex_map)
        #     self.vertices.append(vertex)
        #     self.vertex_map[vertex] = vertex

        # return vertex

    def add_face(self, e):
        face = VoronoiRegion(self, e)
        e.region = face
        if e.index not in self.face_map:
            self.face_map[face] = face
            self.faces.append(face)
        else:
            return self.face_map[e.index]

        return face

    def add_half_edge_to_map(self, vertex1, vertex2, half_edge):
        self.edge_map[(vertex1, vertex2)] = half_edge
        # self.edge_map[(vertex1.id, vertex2.id)] = half_edge

    def find_half_edge(self, vertex1, vertex2):
        return self.edge_map.get((vertex1, vertex2))
        # return self.edge_map.get((vertex1.id, vertex2.id))

    def find_next_edge(self, vertex):
        if vertex.outgoing_half_edge:
            return vertex.outgoing_half_edge.next

    def find_prev_edge(self, vertex):
        if vertex.outgoing_half_edge:
            return vertex.outgoing_half_edge.prev

    def find_prev_vertex(self, vertex):
        prev_edge = self.find_prev_edge(vertex)
        if prev_edge:
            return prev_edge.origin

    def find_next_vertex(self, vertex):
        next_edge = self.find_next_edge(vertex)
        if next_edge:
            return next_edge.origin


class VoronoiEdge:
    def __init__(self, origin: Vertex = None, end: Vertex = None, geom: LineString = None, left_element: Element = None, right_element: Element = None):
        # Element.__init__(self)
        # Node.__init__(self)
        self._geom = geom
        self._left_element = left_element
        self._right_element = right_element
        self.next = None  # 沿着面逆时针方向的下一个半边
        self.prev = None  # 沿着面逆时针方向的上一个半边
        self.region = None     # 所属区域，或者称为face
        self.twin = None  # 对偶半边
        self._origin = origin  # 半边的起始顶点
        self._end = end  # 半边的终止顶点
        self.is_boundary = False  # 是否为边界边

        # if self._edge is not None:
        #     if isinstance(self._edge, Line) or isinstance(self._edge, Ray):
        #         self._geom: Union[LineString, None] = self.get_segments_from_bounds()
        #     else:
        #         self._geom: Union[LineString, None] = self._edge.geom
        #
        #     self.origin = Vertex(round(self._geom.coords[0][0], POINT_PRECISION), round(self._geom.coords[0][1], POINT_PRECISION))
        #     self.end = Vertex(round(self._geom.coords[-1][0], POINT_PRECISION), round(self._geom.coords[-1][1], POINT_PRECISION))
        # else:
        #     self._geom = None

    def __repr__(self):
        return f"B(e{self.left_element.index}, e{self.right_element.index})"

    def __hash__(self):
        return hash((self.origin.id, self.end.id))

    def __eq__(self, other):
        if self is None or other is None:
            return False

        return self.origin.id == other.origin.id and self.end.id == other.end.id

    @property
    def left_element(self):
        return self._left_element

    @left_element.setter
    def left_element(self, v):
        self._left_element = v

    @property
    def right_element(self):
        return self._right_element

    @right_element.setter
    def right_element(self, v):
        self._right_element = v
    #
    # @property
    # def prev_edge(self):
    #     return self._prevEdge
    #
    # @prev_edge.setter
    # def prev_edge(self, v):
    #     self._prevEdge = v

    # def intersect(self, other: Union[Line, Ray, Parabola, Segment]):
    #     return Algebra.intersection(other, self._edge)

    @property
    def geom(self):
        return self._geom

    @geom.setter
    def geom(self, v):
        self._geom = v

    # def get_segments_from_bounds(self):
    #     x_min, y_min, x_max, y_max = self._bounds
    #
    #     dx, dy = self._edge.direction
    #     start_point = self._edge.start_point
    #
    #     # 如果 start_point 为 None，则处理直线，否则处理射线
    #     # if isinstance(self._edge, Ray):
    #     px, py = start_point
    #
    #     intersections = []
    #
    #     def check_intersection(t, x_bound, y_bound):
    #         if isinstance(self._edge, Ray) and t < 0:
    #             return
    #         x = px + t * dx
    #         y = py + t * dy
    #         if x_min <= x <= x_max and y_min <= y <= y_max:
    #             intersections.append((x, y))
    #
    #     if dx != 0:
    #         check_intersection((x_min - px) / dx, x_min, None)
    #         check_intersection((x_max - px) / dx, x_max, None)
    #
    #     if dy != 0:
    #         check_intersection((y_min - py) / dy, None, y_min)
    #         check_intersection((y_max - py) / dy, None, y_max)
    #
    #     # intersections[0] if isinstance(self._edge, Ray) and intersections else intersections
    #
    #     # 对于直线情况，返回两个交点；对于射线情况，返回起点和射线方向上的第一个交点
    #     if isinstance(self._edge, Ray):
    #         if len(intersections) > 0:
    #             return LineString((start_point, intersections[0]))
    #         else:
    #             return None
    #     else:
    #         if len(intersections) >= 2:
    #             return LineString((intersections[0], intersections[1]))
    #         else:
    #             return None


class VoronoiRegion:
    def __init__(self, mesh, element: Element = None):
        # self.half_edge = None
        # self._edges = DoubleLinkedList()
        # self.edges = DoubleLinkedArray()  # 存储face的所有半边数据
        # self.edge_links = []  # 存储每个半边的前一个和下一个半边的索引（tuple）
        self._current = None
        self.head = None
        self.vertices = set()
        self.edge_map = {}
        self.mesh = mesh  # 关联的 Mesh 对象
        self.element = element  # 关联的 Element 对象

    def __repr__(self):
        if self.element is not None:
            return f"VR{self.element.index}"

    def __hash__(self):
        return hash(f"VR{self.element.index}")

    def __eq__(self, other):
        return self.element.index == other.element.index

    # def add_vertex(self, vertex: Vertex = None):
    #     # position = (vertex.x, vertex.y)
    #     # 判断顶点是否已经在该面中
    #     if vertex in self.mesh.vertex_map:
    #         vertex = self.mesh.vertex_map[vertex]
    #     else:
    #         vertex.id = len(self.mesh.vertices)
    #         self.mesh.vertices.append(vertex)
    #         self.mesh.vertex_map[vertex] = vertex
    #
    #     self.vertices.add(vertex)
    #
    #     return vertex

    # def add_half_edge_to_map(self, vertex1, vertex2, half_edge):
    #     # 顶点对以元组的形式存储，以确保无论输入顺序如何，都可以正确匹配
    #     self.edge_map[(vertex1.id, vertex2.id)] = half_edge
    #
    # def get_half_edge(self, vertex1, vertex2):
    #     # 通过顶点对查找对应的半边
    #     # return self.edge_map.get((vertex1.id, vertex2.id))
    #     return self.edge_map.get((vertex1.id, vertex2.id))

    def add_edge(self, vertex1: Vertex = None, vertex2: Vertex = None,
                 geom: LineString = None, index=None, edge=None, is_boundary=False,
                 add_to_tail=True, only_create=False):

        half_edge1 = half_edge2 = None
        # if ve is not None:
        #     vertex1 = ve.origin
        #     vertex2 = ve.end

        if (vertex1 is None and geom is None) or (vertex2 is None and geom is None):
            return None

        if edge is not None:
            geom = edge.geom

        if vertex1 is None and geom is not None:
            vertex1 = Vertex(round(geom.coords[0][0], POINT_PRECISION), round(geom.coords[0][1], POINT_PRECISION))
        if vertex2 is None and geom is not None:
            vertex2 = Vertex(round(geom.coords[-1][0], POINT_PRECISION), round(geom.coords[-1][1], POINT_PRECISION))

        if (not point_duplicate(vertex1, geom.coords[0])) or (not point_duplicate(vertex2, geom.coords[-1])):
            reversed_coords = list(geom.coords)[::-1]
            reversed_coords[0] = (vertex1.x, vertex1.y)
            reversed_coords[-1] = (vertex2.x, vertex2.y)
            geom = LineString(reversed_coords)

        # 确保顶点存在
        vertex1 = self.mesh.add_vertex(vertex1)
        vertex2 = self.mesh.add_vertex(vertex2)

        if (vertex1, vertex2) in self.edge_map:
            half_edge1 = self.edge_map[(vertex1, vertex2)]
            half_edge1.region = self
            # half_edge1 = self.mesh.edge_map[(vertex1, vertex2)]
        else:
            # 创建一个新的半边
            half_edge1 = VoronoiEdge(geom=geom)
            half_edge1.region = self

            # 设置半边的起点
            half_edge1.origin = vertex1
            half_edge1.end = vertex2

            # 更新顶点的出发半边
            vertex1.outgoing_half_edge = half_edge1

            # 更新半边的面
            half_edge1.region = self

            # if index is None:
            #     if not add_to_tail:
            #         self.prepend(half_edge1)
            #     else:
            #         self.append(half_edge1)
            # else:
            #     self.insert(index, half_edge1)

            # 将半边添加到映射中
            self.mesh.add_half_edge_to_map(vertex1, vertex2, half_edge1)
            # self.edge_map[(vertex1, vertex2)] = half_edge1

        if edge is not None:
            half_edge1.left_element = edge.left_element
            half_edge1.right_element = edge.right_element
        half_edge1.is_boundary = is_boundary

        if not only_create:
            if index is None:
                if not add_to_tail:
                    self.prepend(half_edge1)
                else:
                    self.append(half_edge1)
            else:
                self.insert(index, half_edge1)
        #
        # # 将半边添加到mesh中
        # self.mesh.add_half_edge_to_map(vertex1, vertex2, half_edge1)

        if not is_boundary:
            # Create the twin half-edge for internal edges
            if (vertex2, vertex1) in self.mesh.edge_map:
                half_edge2 = self.mesh.edge_map[(vertex2, vertex1)]
                half_edge2.twin = half_edge1
                half_edge1.twin = half_edge2
            else:
                half_edge2 = VoronoiEdge(edge)
                half_edge2.origin = vertex2
                half_edge2.end = vertex1

                if edge is not None:
                    half_edge2.left_element = edge.left_element
                    half_edge2.right_element = edge.right_element

                reversed_coords = list(half_edge1.geom.coords)[::-1]
                half_edge2.geom = LineString(reversed_coords)

                # 互为对偶半边
                half_edge1.twin = half_edge2
                half_edge2.twin = half_edge1
                vertex2.outgoing_half_edge = half_edge2

                self.mesh.add_half_edge_to_map(vertex2, vertex1, half_edge2)
                # self.edge_map[(vertex2, vertex1)] = half_edge2

            half_edge1.is_boundary = is_boundary
            half_edge2.is_boundary = is_boundary
        else:
            half_edge1.is_boundary = is_boundary

        return half_edge1, half_edge2

    def append(self, half_edge: VoronoiEdge):
        # if (half_edge.origin, half_edge.end) in self.edge_map:
        #     return

        # 如果这是此面的第一条边，设为半边起始
        if self.head is None:
            self.head = half_edge
            self.head.next = self.head
            self.head.prev = self.head
        else:
            if half_edge == self.head:
                return  # 不能将边添加到自身

            tail = self.head.prev
            tail.next = half_edge
            half_edge.prev = tail
            half_edge.next = self.head
            self.head.prev = half_edge

        self.mesh.add_half_edge_to_map(half_edge.origin, half_edge.end, half_edge)
        self.edge_map[(half_edge.origin, half_edge.end)] = half_edge

    def prepend(self, half_edge: VoronoiEdge):
        # if (half_edge.origin, half_edge.end) in self.edge_map:
        #     return

        """在链表的头部（head 位置）添加新节点"""
        if self.head is None:
            # 如果链表为空，创建第一个节点并使其指向自己
            self.head = half_edge
            self.head.prev = self.head
            self.head.next = self.head
        else:
            if half_edge == self.head:
                return  # 不能将边添加到自身

            tail = self.head.prev  # 获取当前的 tail
            half_edge.next = self.head  # 新节点的 next 指向当前 head
            half_edge.prev = tail  # 新节点的 prev 指向当前 tail
            tail.next = half_edge  # tail 的 next 更新为新节点
            self.head.prev = half_edge  # 当前 head 的 prev 更新为新节点
            self.head = half_edge  # 更新链表的 head

        self.mesh.add_half_edge_to_map(half_edge.origin, half_edge.end, half_edge)
        self.edge_map[(half_edge.origin, half_edge.end)] = half_edge

    def insert(self, index, half_edge: VoronoiEdge):
        # if (half_edge.origin, half_edge.end) in self.edge_map:
        #     return

        """在指定位置插入新节点"""
        if index == 0:
            self.prepend(half_edge)
        else:
            current = self.head
            count = 0
            # 查找插入位置的前一个节点
            while count < index - 1 and current.next != self.head:
                current = current.next
                count += 1

            # 如果超出了链表的长度，则在尾部添加
            if current.next == self.head:
                self.append(half_edge)
            else:
                # 插入新节点到链表中间
                next_node = current.next
                current.next = half_edge
                half_edge.prev = current
                half_edge.next = next_node
                next_node.prev = half_edge

                self.mesh.add_half_edge_to_map(half_edge.origin, half_edge.end, half_edge)
                self.edge_map[(half_edge.origin, half_edge.end)] = half_edge

    def insert_after(self, half_edge: VoronoiEdge, new_half_edge: VoronoiEdge):
        # if (new_half_edge.origin, new_half_edge.end) in self.edge_map:
        #     return
        # if (new_half_edge.origin, new_half_edge.end) in self.edge_map:
        #     return

        """在指定节点之后插入新节点"""
        next_node = half_edge.next  # 找到给定节点之后的节点

        # 插入新节点
        half_edge.next = new_half_edge  # 给定节点的 next 指向新节点
        new_half_edge.prev = half_edge  # 新节点的 prev 指向给定节点
        new_half_edge.next = next_node  # 新节点的 next 指向给定节点的下一个节点
        next_node.prev = new_half_edge  # 下一个节点的 prev 指向新节点

        self.mesh.add_half_edge_to_map(new_half_edge.origin, new_half_edge.end, new_half_edge)
        self.edge_map[(new_half_edge.origin, new_half_edge.end)] = new_half_edge

    def insert_before(self, half_edge, new_half_edge: VoronoiEdge):
        # if (new_half_edge.origin, new_half_edge.end) in self.edge_map:
        #     return

        """在指定节点之前插入新节点"""
        prev_node = half_edge.prev  # 找到给定节点之前的节点

        # 插入新节点
        prev_node.next = new_half_edge  # 前一个节点的 next 指向新节点
        new_half_edge.prev = prev_node  # 新节点的 prev 指向前一个节点
        new_half_edge.next = half_edge  # 新节点的 next 指向给定节点
        half_edge.prev = new_half_edge  # 给定节点的 prev 指向新节点

        # 如果 node 是头节点，需要更新 head
        if half_edge == self.head:
            self.head = new_half_edge

        self.mesh.add_half_edge_to_map(new_half_edge.origin, new_half_edge.end, new_half_edge)
        self.edge_map[(new_half_edge.origin, new_half_edge.end)] = new_half_edge

    def is_head(self, half_edge: VoronoiEdge):
        if half_edge is None:
            return False
        else:
            return half_edge == self.head

    def is_tail(self, half_edge):
        if half_edge is None:
            return False
        else:
            return half_edge.next == self.head

    def set_head(self, half_edge: VoronoiEdge):
        """将指定节点设置为头节点"""
        if self.head is None or self.head == half_edge:
            # 如果链表为空，或指定的 node 已经是 head，则不做任何操作
            return

        self.head = half_edge

    def delete_edge(self, half_edge: VoronoiEdge):
        """删除指定节点"""
        if self.head is None:
            return  # 链表为空，无法删除

        # 如果链表只有一个节点
        if self.head == self.head.next:
            if self.head == half_edge:
                self.head = None  # 删除唯一的节点，链表变为空
            return

            # 删除头节点
        if half_edge == self.head:
            tail = self.head.prev  # 获取尾节点
            self.head = self.head.next  # 更新头节点
            tail.next = self.head  # 更新尾节点的 next 指向新的头节点
            self.head.prev = tail  # 更新新头节点的 prev 指向尾节点
        else:
            prev_node = half_edge.prev
            next_node = half_edge.next
            prev_node.next = next_node  # 前节点的 next 指向后节点
            next_node.prev = prev_node  # 后节点的 prev 指向前节点

        self.mesh.edge_map.pop((half_edge.origin, half_edge.end), None)
        self.edge_map.pop((half_edge.origin, half_edge.end), None)
        # self.mesh.edge_map.pop((half_edge.end, half_edge.origin), None)

    def traverse(self, start_edge=None, is_ccw=True):
        """从head节点开始遍历整个双向循环列表"""
        visited = set()  # 用于存储已经访问过的节点

        if start_edge is None:
            start_edge = self.head
        current = start_edge
        # if current.is_boundary:
        #     visited.add(current)
        #     current = current.next  # 跳过边界边

        while current:
            if current in visited:
                # print(f"Node with data {current} encountered again.")
                break  # 遇到第二次遍历时退出循环
            visited.add(current)
            yield current
            if is_ccw:
                current = current.next
            else:
                current = current.prev
            if current == start_edge:  # 到达循环链表的起始点时停止
                break

    @property
    def current(self):
        return self._current

    @current.setter
    def current(self, v):
        # if self._edges is not None:
        #     self._edges.current = v

        self._current = v


def point_duplicate(pt1: [np.ndarray, Point, Vertex, tuple], pt2: [np.ndarray, Point, Vertex, tuple], tolerance=EQUAL_TOLERANCE):
    if isinstance(pt1, Vertex):
        pt1 = Point(pt1.x, pt1.y)
    if isinstance(pt2, Vertex):
        pt2 = Point(pt2.x, pt2.y)

    if isinstance(pt1, np.ndarray):
        pt1 = Point(pt1)
    if isinstance(pt2, np.ndarray):
        pt2 = Point(pt2)

    if isinstance(pt1, tuple):
        pt1 = Point(pt1)
    if isinstance(pt2, tuple):
        pt2 = Point(pt2)

    if (isinstance(pt1, Point) and not isinstance(pt2, Point)) or (isinstance(pt2, Point) and not isinstance(pt1, Point)):
        raise TypeError("Both input points must be either numpy arrays or shapely Points")

    if pt1.distance(pt2) <= tolerance:
        return True
    else:
        return False


def point_equals(pt1: np.ndarray, pt2: np.ndarray, tolerance=POINT_PRECISION):
    if pt1 is None or pt2 is None:
        return False

    pt1 = np.array([round(pt1[0], POINT_PRECISION_PLACE), round(pt1[1], POINT_PRECISION_PLACE)])
    pt2 = np.array([round(pt2[0], POINT_PRECISION_PLACE), round(pt2[1], POINT_PRECISION_PLACE)])
    if np.isclose(pt1, pt2, atol=tolerance).all():
        return True
    else:
        return False