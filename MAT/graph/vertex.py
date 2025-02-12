from MAT.graph.coordinate import Coordinate
from MAT.graph.element import Element
from MAT.gv import POINT_PRECISION_PLACE


class Vertex(Coordinate, Element):
    _id_counter = 0  # 自增ID计数器

    def __init__(self, x, y, num=-1, included_angle=-1, connected_edges=None):
        Coordinate.__init__(self, x, y)
        Element.__init__(self, num)

        self.connected_edges = connected_edges or []
        self._num = num
        self._included_angle = included_angle
        self._next_segment = None
        self._prev_segment = None
        self.outgoing_half_edge = None  # 从此顶点出发的半边
        self.x = round(x, POINT_PRECISION_PLACE)
        self.y = round(y, POINT_PRECISION_PLACE)
        self.origin = self
        self.end = self
        # self._edges = super().edges
        # self.id = Vertex._id_counter  # 分配唯一的ID
        # Vertex._id_counter += 1
        if num > -1:
            self.id = num

    def __repr__(self):
        return f"v{self.id}"

    def __hash__(self):
        return hash((round(self.x, POINT_PRECISION_PLACE), round(self.y, POINT_PRECISION_PLACE)))

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    @property
    def num(self):
        return self._num

    @property
    def key(self):
        return f"v{self._num}"

    @property
    def included_angle(self):
        return self._included_angle

    @property
    def next_segment(self):
        return self._next_segment

    @next_segment.setter
    def next_segment(self, v):
        self._next_segment = v

    @property
    def prev_segment(self):
        return self._prev_segment

    @prev_segment.setter
    def prev_segment(self, v):
        self._prev_segment = v

    # @Element.edges.setter
    # def edges(self, v):
    #     return super().edges.__set__(self, v)




