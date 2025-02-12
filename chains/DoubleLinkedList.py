from chains.node import Node


class DoubleLinkedList:
    def __init__(self):
        self.length = 0

        # 初始化头节点
        # head_node = Node()
        self.head = None
        self.tail = None
        self._current = None

    @property
    def current(self):
        return self._current

    @current.setter
    def current(self, value):
        self._current = value

    def __len__(self):
        return self.length

    def __getitem__(self, index):
        if index > self.length - 1 or index < 0:
            raise IndexError("DoubleLinkedList assignment index out of range!")
        else:
            current = self.head
            count = 0

            while current:
                if count == index:
                    return current.data
                current = current.next
                count += 1

        return current.data

    def __setitem__(self, index, value):
        if index > self.length - 1 or index < 0:
            raise IndexError("DoubleLinkedList assignment index out of range!")
        else:
            count = -1
            current = self.head
            while count < index:
                current = current.next
                count += 1

            current.data = value

    def locate(self, value):
        count = -1
        current = self.head
        while current is not None and current.data != value:
            count += 1
            current = current.next
        if current and current.data == value:
            return count
        else:
            raise ValueError("{} is not in sequential list!".format(value))

    def insert(self, index, data):
        count = 0
        prev = self.head

        if index > self.length - 1 or index < 0:
            raise IndexError("DoubleLinkedList assignment index out of range!")
        else:
            new_node = Node(data)
            while count < index:
                prev = prev.next
                count += 1
            new_node.prev = prev
            self.length += 1

            if prev.next:
                # 链表中间插入节点
                new_node.next = prev.next
                prev.next.prev = new_node
                prev.next = new_node
            else:
                # 链表尾部插入节点
                prev.next = new_node

    def find(self, index):
        """辅助函数，用于根据位置返回节点"""
        if index > self.length - 1 or index < 0:
            raise IndexError("DoubleLinkedList assignment index out of range!")
        count = -1
        current = self.head
        while count < index:
            current = current.next
            count += 1

        return current

    def __delitem__(self, index):
        if index > self.length - 1 or index < 0:
            raise IndexError("DoubleLinkedList assignment index out of range!")
        else:
            current = self.find(index)
            if current:
                current.prev.next = current.next

            if current.next:
                current.next.prev = current.prev
            self.length -= 1
            del current

    def delete(self, node):
        if node is self.head:
            self.head = node.next
            if self.head:
                self.head.prev = None
        elif node is self.tail:
            self.tail = node.prev
            if self.tail:
                self.tail.next = None
        else:
            node.prev.next = node.next
            node.next.prev = node.prev
        self.length -= 1

    def append(self, data):
        new_node = Node(data)
        if self.head is None:
            self.head = new_node
            self.tail = new_node
        else:
            new_node.prev = self.tail
            self.tail.next = new_node
            self.tail = new_node

        self.length += 1

    def prepend(self, data):
        """在链表头部添加一个新节点"""
        new_node = Node(data)
        if self.head is None:
            self.head = new_node
            self.tail = new_node
        else:
            new_node.next = self.head
            self.head.prev = new_node
            self.head = new_node

        self.length += 1

    def popleft(self):
        if not self.head:
            return None
            # raise IndexError("pop from empty list")
        data = self.head.data
        self.head = self.head.next
        if self.head:
            self.head.prev = None
        else:
            self.tail = None
        self.length -= 1  # 更新长度计数器
        return data

    def pop(self):
        if not self.tail:
            return None
            # raise IndexError("pop from empty list")
        data = self.tail.data
        self.tail = self.tail.prev
        if self.tail:
            self.tail.next = None
        else:
            self.head = None
        self.length -= 1  # 更新长度计数器
        return data

    def insert_after(self, target_node_data, new_data):
        current = self.head
        while current:
            if current.data == target_node_data:
                new_node = Node(new_data)
                new_node.next = current.next
                new_node.prev = current
                if current.next:
                    current.next.prev = new_node
                current.next = new_node
                if new_node.next is None:
                    self.tail = new_node
                self.size += 1  # 更新长度计数器
                return
            current = current.next
        raise ValueError(f"Node with data {target_node_data} not found")

    def insert_before(self, target_node_data, new_data):
        current = self.head
        while current:
            if current.data == target_node_data:
                new_node = Node(new_data)
                new_node.next = current
                new_node.prev = current.prev
                if current.prev:
                    current.prev.next = new_node
                current.prev = new_node
                if new_node.prev is None:
                    self.head = new_node
                self.size += 1  # 更新长度计数器
                return
            current = current.next
        raise ValueError(f"Node with data {target_node_data} not found")

    def is_empty(self):
        return self.head is None

    def __iter__(self):
        current = self.head
        while current is not None:
            yield current.data
            current = current.next

    def traverse(self, start_node=None):
        if start_node is None:
            start_node = self.head
        current = start_node
        while current:
            yield current
            current = current.next
        # self._current = current

    def continue_traverse(self):
        if self._current is None:
            return self.traverse()
        return self.traverse(self._current)

    def get_current_node(self):
        if self._current is None:
            return None
        next_node = self._current.next
        self._current = next_node  # 更新上一次访问的节点
        return next_node

    # def __iter__(self):
    #     self._current = self.head
    #     return self
    #
    # def __next__(self):
    #     if self._current is None:
    #         raise StopIteration
    #     else:
    #         data = self._current.data
    #         self._current = self._current.next
    #         return data

    def is_head(self, node):
        return node == self.head

    def is_tail(self, node):
        return node == self.tail

    def merge(self, b):
        if self.is_empty():  # 如果a为空
            self.head = b.head
            self.tail = b.tail
            self.length = b.length
        elif not b.is_empty():  # 如果a和b都不为空
            self.tail.next = b.head  # a的尾节点指向b的头节点
            b.head.prev = self.tail  # b的头节点的前驱指向a的尾节点
            self.tail = b.tail  # 更新a的尾节点为b的尾节点
            self.length += b.length  # 更新a的长度
        return self

    def __str__(self):
        s = "["
        current = self.head
        count = 0
        while current is not None:
            count += 1
            s += str(current)
            current = current.next
            if count < self.length:
                s += "<-->"
        s += "]"
        return s

