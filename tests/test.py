from shapely.geometry import LineString
from shapely.ops import snap

# 定义两条 LineString
line1 = LineString([(0.309, -0.951), (0.073, -0.225)])
line2 = LineString([(-0.118, -0.363), (2, 1.1750714285714285)])

# 使用 snap 对齐两条线，公差设置为 1e-9
snapped_line1 = snap(line1, line2, tolerance=0.01)

# 求交点
intersection1 = snapped_line1.intersection(line2)

# 使用 snap 对齐两条线，公差设置为 1e-9
snapped_line2 = snap(line2, line1, tolerance=0.01)

# 求交点
intersection2 = snapped_line2.intersection(line1)

# 检查是否有交点
if not intersection1.is_empty:
    print(f"交点坐标: {intersection1}")
elif not intersection2.is_empty:
    print(f"交点坐标: {intersection2}")
else:
    print("没有找到交点")