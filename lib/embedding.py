import numpy as np
import queue

from . import network
from .util2d import divide_line, EventQueue


# Object that generates a 2D representation of a network
class Embedding():

    square_size = 15    # squares represent inputs and outputs
    circle_radius = 8   # circles represent neurons
    spike_radius = 3    # smaller circles represent spikes

    def __init__(self, net: network.Network, size):
        self.network = net
        self.size = size
        self.spike_visualization = False
        self.spike_queue = queue.Queue()
        self.input_count = len(self.network.inputs)
        self.output_count = len(self.network.outputs)
        self.neuron_count = len(self.network.interneurons)
        self.synapse_count = np.count_nonzero(self.network.connectome)

        self.input_positions = np.zeros((self.input_count, 2))
        self.output_positions = np.zeros((self.output_count, 2))
        self.neuron_positions = np.zeros((self.neuron_count, 2))
        self.synapse_positions = np.zeros((self.synapse_count, 2, 2))
        self.active_nodes = np.zeros(
            self.input_count + self.output_count + self.neuron_count,
            dtype=bool)
        self.spike_positions = EventQueue()
        self.synapse_indices = {}

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
            np.array((Embedding.square_size / 2, 0)),
            np.array((Embedding.square_size / 2, self.size[1])),
            self.input_count)
        # compute outputs
        self.output_positions = divide_line(
            np.array((self.size[0] - Embedding.square_size / 2, 0)),
            np.array((self.size[0] - Embedding.square_size / 2, self.size[1])),
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
                    # Maintain a dict of synapse indices connected to a node
                    if i in self.synapse_indices:
                        self.synapse_indices[i].append(count)
                    else:
                        self.synapse_indices[i] = [count]
                    count += 1

    def update_spikes(self):
        self.active_nodes[:] = 0
        while not self.spike_queue.empty():
            node = self.spike_queue.get(False)
            self.active_nodes[node] = 1
            # get all outgoing synapses
            connected_synapses = []
            if node in self.synapse_indices:
                connected_synapses = self.synapse_indices[node]
            # put spike positions in spike pos queue
            # TODO axon length of 10 hardcoded, needs update after in/out neuron problem is fixed
            for syn in connected_synapses:
                synapse_coords = self.synapse_positions[syn]
                spikes = divide_line(synapse_coords[0], synapse_coords[1], 10)
                delay = 0
                for spike in spikes:
                    self.spike_positions.insert(
                        self.network.agent.env.internal_clock + delay,
                        spike)
                    delay += 1
