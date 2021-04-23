import numpy as np

from . import network
from .util2d import divide_line


# Object that generates a 2D representation of a network
class Embedding():

    square_size = 15    # squares represent inputs and outputs
    circle_radius = 8   # circles represent neurons

    def __init__(self, net: network.Network, size):
        self.network = net
        self.size = size
        self.input_count = len(self.network.inputs)
        self.output_count = len(self.network.outputs)
        self.neuron_count = len(self.network.interneurons)
        self.synapse_count = np.count_nonzero(self.network.connectome)

        self.input_positions = np.zeros((self.input_count, 2))
        self.output_positions = np.zeros((self.output_count, 2))
        self.neuron_positions = np.zeros((self.neuron_count, 2))
        self.synapse_positions = np.zeros((self.synapse_count, 2, 2))

    @ staticmethod
    def shorten_synapse(pos1, pos2):
        direction_vec = pos2 - pos1
        unit_vec = (direction_vec) / np.linalg.norm(direction_vec)
        pos1_new = pos1 + Embedding.circle_radius * unit_vec
        pos2_new = pos2 - Embedding.circle_radius * unit_vec
        return np.concatenate((pos1_new, pos2_new))

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
        # compute neurons (for now they are in a line) TODO different configurations
        self.neuron_positions = divide_line(
            np.array((self.size[0] / 2, 0)),
            np.array((self.size[0] / 2, self.size[1])),
            self.neuron_count)
        # compute synapses
        node_positions = np.concatenate((
            self.input_positions,
            self.output_positions,
            self.neuron_positions))
        node_count = len(node_positions)
        count = 0
        for i, pos in zip(range(node_count), node_positions):
            e1 = np.zeros(node_count)
            e1[i] = 1
            e2 = np.dot(self.network.connectome, e1)
            if np.count_nonzero(e2):
                connected = np.where(e2 == 1)
                for i2 in connected:
                    pos2 = node_positions[i2]
                    self.synapse_positions[count, :, :] = Embedding.shorten_synapse(pos, pos2)
                    count += 1
