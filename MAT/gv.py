from decimal import Decimal

import numpy as np
from shapely import Point

EQUAL_RELATIVE_TOLERANCE = 1e-5
POINT_PRECISION = 1e-3
EQUAL_TOLERANCE = 10*POINT_PRECISION
PERPENDICULAR_ANGULAR_TOLERANCE = 1  # 判断两条线是否平行的角度容差，如果角度差小于这个值，则认为两条线平行
PI = 3.1415926

def count_decimal_places(num):
    # 将浮点数转换为Decimal对象
    number_decimal = Decimal(str(num))
    # 将Decimal对象转换为字符串
    number_str = format(number_decimal, 'f')

    # 如果字符串中包含小数点
    if '.' in number_str:
        # 获取小数点的位置
        decimal_index = number_str.index('.')
        # 返回小数点后有效数字的个数
        return len(number_str) - decimal_index - 1
    else:
        # 如果没有小数点，返回0
        return 0


POINT_PRECISION_PLACE = count_decimal_places(POINT_PRECISION)   # 点的精度，小数点后保留几位
ANGLE_DIFF_RADIANS = 1 * (PI / 180)
