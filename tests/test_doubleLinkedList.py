import numpy as np

from MAT.algorithm import find_first_element
from MAT.graph.segment import Segment
from chains.DoubleLinkedList import DoubleLinkedList
from MAT.graph.vertex import Vertex
from MAT.algebra import Algebra


def test_doubleLinkedList():
    dllist = DoubleLinkedList()
    dllist.append('apple')
    dllist.append('banana')
    dllist.prepend('watermelon')
    dllist.insert(2, '0')

    print(dllist)
    print(dllist[1])


def test_chains():
    points = [
        (6.5, 6.3), (6.8, 5.6), (9, 5),
        (8.8, 4), (8, 3.2), (8.4, 2.5),
        (5, 1), (3.85, 1.96), (3.85, 3),
        (5.5, 3), (5.5, 4), (4.8, 4.7),
        (3.5, 4.2),
        (2.8, 4.9), (3.2, 5.9), (4.8, 7),(6.5, 6.3)
    ]
    points.reverse()

    # dllist = DoubleLinkedList()
    # for idx, point in enumerate(points):
    #     if idx == 0:
    #         dllist.append(point)
    #         dllist.prepend(points[len(points) - 1])
    #     else:
    #         dllist.append(point)

    is_ccw = True if Algebra.is_ccw(points) else False

    chains = []
    chain = []
    origin = None
    points = points[:-1]
    included_angle = -1

    iterate_index, first_no = find_first_element(points, is_ccw=is_ccw)

    # iterate_index.append(first_no)
    for idx, idx_pt in enumerate(iterate_index):
        current = iterate_index[idx]
        prev = iterate_index[idx - 1]
        next = iterate_index[(idx + 1) % len(iterate_index)]

        vector1 = np.array((points[prev][0] - points[current][0],
                            points[prev][1] - points[current][1]), dtype=float)
        vector2 = np.array((points[next][0] - points[current][0],
                            points[next][1] - points[current][1]), dtype=float)

        included_angle = Algebra.angle_between_vecters(vector1, vector2, is_ccw=is_ccw)
        print("{}: {}".format(idx, included_angle))

        if idx == 0:
            origin = Vertex(points[current][0], points[current][1], current, included_angle)
            continue

        end = Vertex(points[current][0], points[current][1], current, included_angle)
        seg = Segment(origin, end, num=idx)

        if included_angle < 180:
            chain.append(seg)
            chains.append(chain)
            chain = []
        else:
            # chain = chains.pop()
            chain.append(seg)
            chain.append(end)

        origin = end

    end = Vertex(points[iterate_index[0]][0], points[iterate_index[0]][1], iterate_index[0], included_angle)
    seg = Segment(origin, end)
    chain.append(seg)
    chains.append(chain)

    print(chains)


def calculate_pairs(input_list):
    result_list = []
    length = len(input_list)

    # 遍历列表中的每一对元素
    for i in range(0, length - 1, 2):
        sum_result = input_list[i] + input_list[i + 1]
        result_list.append(sum_result)

    # 如果列表中有奇数个元素，则将最后一个元素直接加入结果列表
    if length % 2 != 0:
        result_list.append(input_list[-1])

    return result_list


def test_pair():
    # 示例列表
    input_list = [1, 2, 3, 4, 5]
    result = calculate_pairs(input_list)
    print(result)  # 输出: [3, 7, 5]


            
