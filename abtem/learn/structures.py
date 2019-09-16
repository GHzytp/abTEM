import numpy as np
from matplotlib.path import Path
from scipy.signal import resample
from scipy.spatial import ConvexHull

from abtem.points import LabelledPoints, repeat
from abtem.learn.augment import bandpass_noise


def graphene_like(a=2.46, n=1, m=1, labels=None):
    if labels is None:
        labels = np.zeros(2, dtype=np.int)

    basis = [(0, 0), (2 / 3., 1 / 3.)]
    cell = [[a, 0], [-a / 2., a * 3 ** 0.5 / 2.]]
    positions = np.dot(np.array(basis), np.array(cell))

    points = LabelledPoints(positions, cell=cell, labels=labels)
    points = repeat(points, n, m)
    return points


def random_swap_labels(points, label, new_label, probability):
    idx = np.where(points.labels == label)[0]
    points.labels[idx[np.random.rand(len(idx)) < probability]] = new_label
    return points


def random_strain(points, scale, amplitude):
    shape = np.array((128, 128))
    sampling = np.linalg.norm(points.cell, axis=1) / shape
    outer = 1 / scale * 2
    noise = bandpass_noise(inner=0, outer=outer, shape=shape, sampling=sampling)
    indices = np.floor((points.scaled_positions % 1.) * shape).astype(np.int)

    for i in [0, 1]:
        points.positions[:, i] += amplitude * noise[indices[:, 0], indices[:, 1]]

    return points


def make_blob():
    points = np.random.rand(10, 2)
    points = points[ConvexHull(points).vertices]
    x = resample(points[:, 0], 50)
    y = resample(points[:, 1], 50)
    return np.array([x, y]).T


def random_paint_blob(points, new_label, size):
    blob = size * (make_blob() - .5)

    position = np.random.rand() * points.cell[0] + np.random.rand() * points.cell[1]
    path = Path(blob + position)

    inside = path.contains_points(points.positions)

    points.labels[inside] = new_label

    return points