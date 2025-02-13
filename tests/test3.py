from decimal import Decimal

def count_decimal_places(number):
    # 将浮点数转换为Decimal对象
    number_decimal = Decimal(str(number))
    # 将Decimal对象转换为定点格式字符串
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

# 示例
num = 1e-9
decimal_places = count_decimal_places(num)
print(f"数字 {num} 小数点后有 {decimal_places} 位有效数字。")