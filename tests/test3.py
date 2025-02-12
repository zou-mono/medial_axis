class Node:
    def __init__(self, data):
        self.data = data
        self.prev = None
        self.next = None

class CircularDoublyLinkedList:
    def __init__(self):
        self.head = None

    def append(self, data):
        """在链表的末尾添加新节点，head 保持不变"""
        new_node = Node(data)
        if self.head is None:
            # 如果链表为空，创建第一个节点并设置为 head
            self.head = new_node
            self.head.prev = self.head
            self.head.next = self.head
        else:
            self.append_to_tail(new_node)

    def append_to_tail(self, new_node):
        """在尾部添加新节点，head 保持不变"""
        tail = self.head.prev  # 获取当前的 tail
        tail.next = new_node  # 当前 tail 的 next 指向新节点
        new_node.prev = tail  # 新节点的 prev 指向当前 tail
        new_node.next = self.head  # 新节点的 next 指向 head
        self.head.prev = new_node  # head 的 prev 更新为新节点

    def set_head(self, node):
        # """将指定节点设置为 head，重新调整链表顺序"""
        # if self.head is None or self.head == node:
        #     # 如果链表为空，或指定的 node 已经是 head，则不做任何操作
        #     return
        #
        # # 处理一般情况，重新排列节点顺序
        # current = self.head
        # while current != node:
        #     # 把当前 head 节点移动到尾部，继续循环，直到新的 head 为指定节点
        #     current = current.next
        self.head = node

    def traverse(self):
        """生成器函数，遍历链表的所有节点，每次返回一个节点"""
        if self.head is None:
            return  # 链表为空，直接返回

        current = self.head
        first_pass = True

        while not (current == self.head and not first_pass):
            yield current  # 返回当前节点
            current = current.next
            first_pass = False

    def display(self):
        """使用 traverse 函数显示链表中的所有元素"""
        for node in self.traverse():
            print(node.data, end=" ")
        print()

# 使用示例
cdll = CircularDoublyLinkedList()
cdll.append(1)
cdll.append(2)
# cdll.append(3)
# cdll.append(4)

# 遍历并打印所有节点
print("初始链表:")
cdll.display()  # 输出: 1 2 3 4

# 将节点 2 设置为 head
cdll.set_head(cdll.head.next)

# 遍历并打印所有节点
print("将节点 2 设置为 Head 后:")
cdll.display()  # 输出: 2 3 4 1