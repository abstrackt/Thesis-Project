from math import sqrt


def determinant_3x3(m):
    return (m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1]) -
            m[1][0] * (m[0][1] * m[2][2] - m[0][2] * m[2][1]) +
            m[2][0] * (m[0][1] * m[1][2] - m[0][2] * m[1][1]))



def norm(a):
    return sqrt(a[0] * a[0] + a[1] * a[1] + a[2] * a[2])


def add(a, b):
    return (a[0] + b[0],
            a[1] + b[1],
            a[2] + b[2])


def subtract(a, b):
    return (a[0] - b[0],
            a[1] - b[1],
            a[2] - b[2])


def volume(a, b, c, d):
    return (abs(determinant_3x3((subtract(a, b),
                                 subtract(b, c),
                                 subtract(c, d),
                                 ))) / 6.0)


def distance(a, b):
    return abs(norm(subtract(a, b)))




