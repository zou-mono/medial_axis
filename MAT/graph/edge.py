from MAT.graph.segment import Segment
from MAT.graph.vertex import Vertex


class Edge(Segment):
    def __init__(self, v0: Vertex, v1: Vertex):
        super().__init__(v0, v1)