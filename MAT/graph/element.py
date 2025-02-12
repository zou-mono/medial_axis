class Element:
    def __init__(self, num=0):
        super().__init__()
        self._index = num
        self.region = None
        # self.region = VoronoiRegion()
        # self._voronoiEdges = DoubleLinkedList()
        # self._current_edge = None

    # @property
    # def current_edge(self):
    #     return self._current_edge
    #
    # @current_edge.setter
    # def current_edge(self, v):
    #     self._current_edge = v
    def __repr__(self):
        return f"e{self._index}"

    @property
    def index(self):
        return self._index

    @index.setter
    def index(self, v):
        self._index = v

    @property
    def region(self):
        return self._region

    @region.setter
    def region(self, v):
        self._region = v
