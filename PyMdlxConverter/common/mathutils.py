import math
import random


def sign(num):
    if num == 0:
        return 0
    elif num < 0:
        return -1
    elif num > 0:
        return 1


def deg_to_rad(degrees):
    return degrees * (math.pi / 180)


def rad_to_deg(radians):
    return radians * (180 / math.pi)


def random_in_range(a, b):
    return a + random.random() * (b - a)


def clamp(x, min_val, max_val):
    return min(max(x, min_val), max_val)


def lerp(a, b, t):
    return a + t * (b - a)


def hermite(a, b, c, d, t):
    factor_times2 = t * t
    factor_1 = factor_times2 * (2 * t - 3) + 1
    factor_2 = factor_times2 * (t - 2) + t
    factor_3 = factor_times2 * (t - 1)
    factor_4 = factor_times2 * (3 - 2 * t)
    return (a * factor_1) + (b * factor_2) + (c * factor_3) + (d * factor_4)


def bezier(a, b, c, d, t):
    invt = 1 - t
    factor_times2 = t * t
    inverse_factor_times2 = invt * invt
    factor_1 = inverse_factor_times2 * invt
    factor_2 = 3 * t * inverse_factor_times2
    factor_3 = 3 * factor_times2 * invt
    factor_4 = factor_times2 * t
    return (a * factor_1) + (b * factor_2) + (c * factor_3) + (d * factor_4)


def copy_sign(x, y):
    sign_y = sign(y)
    if sign_y == 0:
        return 0
    sign_x = sign(x)
    if sign_x != sign_y:
        return -x
    return x


def power_of_two(x):
    x -= 1
    x |= x >> 1
    x |= x >> 2
    x |= x >> 4
    x |= x >> 8
    x |= x >> 16
    x += 1
    return x


def is_power_of_two(x):
    if x == 0:
        return False
    return (x & (x - 1)) == 0


def float_decimals(num, precision):
    return str(math.trunc(num * precision) / precision)


def float_array_decimals(arr, precision):
    data = [str(i) if isinstance(i, int) else str(i) if i == 0.00 or i == 1.00 else float_decimals(i,
                                                                                                    precision)
            for i in \
            arr]
    values = ', '.join(data)
    return values
