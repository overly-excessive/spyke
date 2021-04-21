import numpy as np

from . import network


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


# Object that generates a 2D representation of a network
class Embedding():

    square_size = 15    # squares represent inputs and outputs
    circle_radius = 8   # circles represent neurons

    def __init__(self, net: network.Network, size):
        self.size = size
        self.input_count = len(net.inputs)
        self.output_count = len(net.outputs)
        self.neuron_count = len(net.interneurons)

        self.input_positions = np.zeros((self.input_count, 2))
        self.output_positions = np.zeros((self.output_count, 2))
        self.neuron_positions = np.zeros((self.neuron_count, 2))

    def compute(self):
        # compute inputs
        self.input_positions = divide_line(
            np.array((0, - Embedding.square_size / 2)),
            np.array((0, self.size[1] - Embedding.square_size / 2)),
            self.input_count)
        # compute outputs
        self.output_positions = divide_line(
            np.array((self.size[0] - Embedding.square_size, - Embedding.square_size / 2)),
            np.array((self.size[0] - Embedding.square_size, self.size[1] - Embedding.square_size / 2)),
            self.output_count)
