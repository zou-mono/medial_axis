import numpy as np
from shapely import LineString

from MAT.graph.vertex import Vertex
from MAT.graph.element import Element


class Segment(Element):
    def __init__(self, v0: Vertex, v1: Vertex, num=0):
        Element.__init__(self, num)
        self._origin = v0
        self._end = v1
        self._num = num

    def __repr__(self):
        return f"s{self._num}: {self._origin}->{self._end}"

    @property
    def geom(self):
        return LineString([[self._origin.x, self._origin.y],
                          [self._end.x, self._end.y]])

    @property
    def direction(self):
        return np.array([self._end.x - self._origin.x, self._end.y - self._origin.y])

    def reverse(self):
        return Segment(self._end, self._origin, self._num)

    @property
    def num(self):
        return self._num

    @property
    def key(self):
        # return (self._origin.index, self._end.index)
        return f"e{self._num}"

    @property
    def origin(self):
        return self._origin

    @property
    def end(self):
        return self._end

    # @property
    # def edges(self):
    #     return self._edges
    #
    # @edges.setter
    # def edges(self, v):
    #     self._edges = v


