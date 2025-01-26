from math import atan2

import numpy as np


def rotate_x(angle):
    return np.array([
        [1, 0, 0, 0],
        [0, np.cos(angle), -np.sin(angle), 0],
        [0, np.sin(angle), np.cos(angle), 0],
        [0, 0, 0, 1]
    ])


def rotate_y(angle):
    return np.array([
        [np.cos(angle), 0, np.sin(angle), 0],
        [0, 1, 0, 0],
        [-np.sin(angle), 0, np.cos(angle), 0],
        [0, 0, 0, 1]
    ])


def rotate_z(angle):
    return np.array([
        [np.cos(angle), -np.sin(angle), 0, 0],
        [np.sin(angle), np.cos(angle), 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ])


def translate_z(amount):
    np.array([
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, amount],
        [0, 0, 0, 1]
    ])


def identity():
    np.array([
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ])


def create_transform_matrix(a: np.array, b: np.array):
    d = b - a
    d = d / np.linalg.norm(d)
    d = np.array([d[0], d[1], d[2], 0])

    unit_y = np.array([0, 1, 0, 0])

    if all(d[i] == unit_y[i] for i in range(len(d))):
        return identity()

    # 1. Twist around y to align the rotation
    a_y = np.arctan2(d[2], d[0])
    r_1 = rotate_y(a_y)

    d_1 = np.dot(r_1, d)

    # TODO: Figure this formula out...
    # 2. Rotate around z to align the slope
    a_z = np.arctan2(d[1], d[0])
    r_2 = rotate_z(a_z)

    # 3. Twist back around y to not introduce twist
    r_3 = rotate_y(-a_y)

    return np.matmul(r_1, r_2, r_3)


a = np.array([0, 0, 0])
b = np.array([1, 0.5, 0.5])

mat = create_transform_matrix(a, b)

test = [0, 1, 0, 0]

result = np.dot(mat, test)

print(result)
