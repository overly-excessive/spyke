import numpy as np


def pol2cart(rho, phi):
    x = rho * np.cos(phi)
    y = rho * np.sin(phi)
    return np.array((x, y))


def divide_line(Apos, Bpos, n):
    result = np.zeros((n, 2))
    inter_dist_vec = (Bpos - Apos) / (n + 1)
    for i in range(n):
        result[i, 0] = Apos[0] + (i + 1) * inter_dist_vec[0]
        result[i, 1] = Apos[1] + (i + 1) * inter_dist_vec[1]
    return result


def rotate(vec, alpha):
    rot = np.array([[np.cos(alpha), -np.sin(alpha)],
                    [np.sin(alpha), np.cos(alpha)]])
    return np.dot(rot, vec)
