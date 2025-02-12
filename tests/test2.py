import numpy as np

def ray_intersection(P1, d1, P2, d2):
    # 构造系数矩阵
    A = np.array([[d1[0], -d2[0]],
                  [d1[1], -d2[1]]])

    # 构造右边的常数项
    b = np.array([P2[0] - P1[0], P2[1] - P1[1]])

    # 解线性方程组以求解 t1 和 t2
    try:
        t1, t2 = np.linalg.solve(A, b)
    except np.linalg.LinAlgError:
        # 如果矩阵不可逆，表示射线平行或重合
        return None

    # 检查 t1 和 t2 是否都大于等于0（确保交点在射线的正方向上）
    if t1 >= 0 and t2 >= 0:
        # 计算交点
        intersection = P1 + t1 * d1
        return intersection
    else:
        # 如果 t1 或 t2 小于0，表示交点在射线的反方向，不是有效交点
        return None

# # 示例：输入射线的起点和方向向量
P1 = np.array([0.309, -0.225])
d1 = np.array([0.726, 0])

P2 = np.array([0.309, -0.951])
d2 = np.array([0.9510921179292213, -0.3089074023277982])

P1 = np.array([0.309, -0.225])
d1 = np.array([-1, 0])

P2 = np.array([0.309, -0.951])
d2 = np.array([-0.2, 0])

# 计算射线交点
intersection = ray_intersection(P1, d1, P2, d2)

if intersection is not None:
    print(f"射线的交点坐标为: {intersection}")
else:
    print("射线没有交点或交点在射线的反方向")