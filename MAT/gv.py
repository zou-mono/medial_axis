from decimal import Decimal

import numpy as np
from shapely import Point

EQUAL_TOLERANCE = 1e-3
EQUAL_RELATIVE_TOLERANCE = 1e-5
POINT_PRECISION = 1e-3


def point_duplicate(pt1: [np.ndarray, Point], pt2: [np.ndarray, Point], tolerance=POINT_PRECISION):
    if isinstance(pt1, np.ndarray) and isinstance(pt2, np.ndarray):
        pt1 = Point(pt1)
        pt2 = Point(pt2)
    elif (isinstance(pt1, Point) and not isinstance(pt2, Point)) or (isinstance(pt2, Point) and not isinstance(pt1, Point)):
        raise TypeError("Both input points must be either numpy arrays or shapely Points")

    if pt1.distance(pt2) <= tolerance:
        return True
    else:
        return False


def point_equals(pt1: np.ndarray, pt2: np.ndarray, tolerance=POINT_PRECISION):
    if pt1 is None or pt2 is None:
        return False

    pt1 = np.array([round(pt1[0], POINT_PRECISION_PLACE), round(pt1[1], POINT_PRECISION_PLACE)])
    pt2 = np.array([round(pt2[0], POINT_PRECISION_PLACE), round(pt2[1], POINT_PRECISION_PLACE)])
    if np.isclose(pt1, pt2, atol=tolerance).all():
        return True
    else:
        return False

def count_decimal_places(num):
    # 将浮动数转化为 Decimal 类型，避免浮点数精度问题
    num = Decimal(str(num))

    # 获取小数部分的字符串表示
    decimal_str = str(num).split('.')[1] if '.' in str(num) else ""

    return len(decimal_str)

POINT_PRECISION_PLACE = count_decimal_places(POINT_PRECISION)   # 点的精度，小数点后保留几位
