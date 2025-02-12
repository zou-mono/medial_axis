class DoubleLinkedArray:
    def __init__(self):
        self.data = []
        self.prev = []
        self.next = []
        self.head = -1
        self.tail = -1
        self.size = 0

    def __len__(self):
        return self.size

    def __getitem__(self, index):
        """Allow accessing elements by index using square bracket notation."""
        if index < 0 or index >= len(self.data):
            raise IndexError("DoubleLinkedArray assignment index out of range!")
        return self.data[index]

    def append(self, value):
        index = len(self.data)
        self.data.append(value)
        self.prev.append(self.tail)
        self.next.append(self.head)  # 在循环链表中，新的尾部元素指向头部

        if self.tail != -1:
            self.next[self.tail] = index
        else:
            self.head = index

        self.tail = index
        self.prev[self.head] = self.tail  # 更新头部的 prev 指向新 tail

        # self.next.append(-1)
        # if self.tail != -1:
        #     self.next[self.tail] = index
        # self.tail = index
        #
        # if self.head == -1:
        #     self.head = index

        self.size += 1

    def prepend(self, value):
        index = len(self.data)
        self.data.append(value)
        self.prev.append(-1)
        self.next.append(self.head)  # 新的头部的 next 指向当前头部

        if self.head != -1:
            self.prev[self.head] = index
        else:
            self.tail = index

        self.head = index
        self.next[self.tail] = self.head  # 更新尾部的 next 指向新 head

        # self.next.append(self.head)
        #
        # if self.head != -1:
        #     self.prev[self.head] = index
        # self.head = index
        #
        # if self.tail == -1:
        #     self.tail = index

        self.size += 1

    def insert(self, index, value):
        if index < 0 or index > len(self.data):
            raise IndexError("Index out of bounds")

        new_index = len(self.data)
        self.data.append(value)
        self.prev.append(-1)
        self.next.append(-1)

        if index == 0:
            # 在头部插入
            self.prepend(value)
        elif index == self.size:
            # 在尾部插入
            self.append(value)
        else:
            # 中间插入
            current = self.head
            for _ in range(index):
                current = self.next[current]

            prev_index = self.prev[current]
            self.prev[new_index] = prev_index
            self.next[new_index] = current
            self.prev[current] = new_index
            self.next[prev_index] = new_index

        # if index > 0:
        #     prev_index = self.prev[index - 1]
        #     self.prev[new_index] = prev_index
        #     self.next[new_index] = index
        #     self.prev[index] = new_index
        #     if prev_index != -1:
        #         self.next[prev_index] = new_index
        #     else:
        #         self.head = new_index
        # else:
        #     self.prev[new_index] = -1
        #     self.next[new_index] = index
        #     if self.head != -1:
        #         self.prev[self.head] = new_index
        #     self.head = new_index
        #
        # if index < len(self.data):
        #     self.next[new_index] = index
        #     self.prev[index] = new_index

        self.size += 1

    def delete(self, index):
        if index < 0 or index >= len(self.data):
            raise IndexError("Index out of bounds")

        if self.size == 1:
            # 特殊情况：只有一个元素时
            self.data = []
            self.prev = []
            self.next = []
            self.head = self.tail = -1
            self.size = 0
            return

        current = self.head
        for _ in range(index):
            current = self.next[current]

        prev_index = self.prev[current]
        next_index = self.next[current]

        if current == self.head:
            self.head = next_index
        if current == self.tail:
            self.tail = prev_index

        self.next[prev_index] = next_index
        self.prev[next_index] = prev_index

        self.data[current] = None
        self.size -= 1

        # prev_index = self.prev[index]
        # next_index = self.next[index]
        #
        # if prev_index != -1:
        #     self.next[prev_index] = next_index
        # else:
        #     self.head = next_index
        #
        # if next_index != -1:
        #     self.prev[next_index] = prev_index
        # else:
        #     self.tail = prev_index
        #
        # self.data[index] = None
        # self.prev[index] = -1
        # self.next[index] = -1
        #
        # self.size -= 1

    def get_next(self, index):
        """返回索引为 index 的元素的下一个元素的值"""
        if index < 0 or index >= len(self.data):
            raise IndexError("Index out of bounds")

        next_index = self.next[index]

        if next_index != -1:
            return self.data[next_index]
        else:
            return None  # 如果没有下一个元素，返回 None

    def get_prev(self, index):
        """返回索引为 index 的元素的前一个元素的值"""
        if index < 0 or index >= len(self.data):
            raise IndexError("Index out of bounds")

        prev_index = self.prev[index]

        if prev_index != -1:
            return self.data[prev_index]
        else:
            return None  # 如果没有前一个元素，返回 None

