from chains.DoubleLinkedList import DoubleLinkedList


class Chain:
    def __init__(self, elements: DoubleLinkedList):
        self.elements = elements
        # self.region = None

    def merge(self, other):
        self.elements.merge(other.elements)
        return self

    def __str__(self):
        s = "["

        count = 0
        for e in self.elements:
            s += str(e)

            if count < len(self.elements) - 1:
                s += "<-->"

            count += 1
        s += "]"
        return s
    # @property
    # def region(self):
    #     return self._region
    #
    # @region.setter
    # def region(self, v):
    #     self._region = v




