import numpy as np
from MAT.graph.vertex import Vertex


class Line:
    def __init__(self, start_pt: Vertex, direction: np.array):
        # super().__init__(start_pt, direction)
        self._O = start_pt
        self._d = direction

    @property
    def start_point(self):
        return np.array([self._O.x, self._O.y])

    @property
    def direction(self):
        return self._d


class Ray(Line):
    def __init__(self, start_pt: Vertex, direction: np.array):
        super().__init__(start_pt, direction)
        self._O = start_pt
        self._d = direction

    @property
    def start_point(self):
        return np.array([self._O.x, self._O.y])

    @property
    def direction(self):
        return self._d


class Parabola:
    def __init__(self, focus, vertex, rotate_matrix=None, rotate=True, vector_x=None, vector_y=None):
        self.focus = focus
        self.vertex = vertex
        self.x = vector_x
        self.y = vector_y
        self.rotate_matrix = rotate_matrix
        self.rotate = rotate
        self._geom = None

    def func(self, x):
        if self.rotate:
            return (np.dot(self.rotate_matrix, np.array([x, x ** 2 / (4 * self.focus)])).T +
                    np.array([self.vertex.x, self.vertex.y]))
        else:
            # return np.array([x, x ** 2 / (4 * self.focus)]).T + np.array([self.vertex.x, self.vertex.y])
            return np.array(x ** 2 / (4 * self.focus)).T

    @property
    def geom(self):
        return self._geom

    @geom.setter
    def geom(self, value):
        self._geom = value
