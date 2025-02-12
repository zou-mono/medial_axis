class Node:
    def __init__(self, data=None, prev=None, next=None):
        self.data = data
        self.next = next
        self.prev = prev

    def __str__(self):
        return str(self.data)

    def __repr__(self):
        return f"Node({self.data}, next={self.next}, prev={self.prev})"
