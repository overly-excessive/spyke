import numpy as np
import pygame

from . import network
from .util2d import rotate, divide_line


# Object that generates a 2D representation of a network
class Embedding():

    input_color = (93, 147, 181)  # kinda blue
    output_color = (70, 180, 78)  # kinda green
    node_color = (121, 149, 117)  # light gray
    spike_color = (228, 221, 52)  # bright yellow
    neuron_radius = 8   # circles represent neurons
    spike_radius = 3    # smaller circles represent spikes

    def __init__(self, net: network.Network, surface):
        self.network = net
        self.surface = surface.copy()
        self.size = surface.get_size()

        self.input_positions = np.zeros((self.network.neuron_count[0], 2))
        self.output_positions = np.zeros((self.network.neuron_count[1], 2))
        self.neuron_positions = np.zeros((self.network.neuron_count[2], 2))
        self.dendrite_count = np.count_nonzero(self.network.connectome)
        self.dendrite_positions = np.zeros((self.dendrite_count, 2, 2))

        top = np.array((self.size[0] / 2, 0))
        center = np.array(self.size) / 2

        # draw the inputs on the surface, while saving their positions:
        arc = np.pi / (self.network.neuron_count[0] + 1)
        for i in range(self.network.neuron_count[0]):
            rot = (i + 1) * arc + np.pi / 2
            pos = rotate(top, rot) + center
            pygame.draw.circle(
                self.surface,
                Embedding.input_color,
                pos,
                Embedding.neuron_radius)
            self.input_positions[i] = pos

        # draw outputs
        arc = np.pi / (self.network.neuron_count[1] + 1)
        for i in range(self.network.neuron_count[1]):
            rot = -(i + 1) * arc + np.pi / 2
            pos = rotate(top, rot) + center
            pygame.draw.circle(
                self.surface,
                Embedding.output_color,
                pos,
                Embedding.neuron_radius)
            self.output_positions[i] = pos

        # brain cavity
        pygame.draw.circle(
            self.surface,
            (32, 38, 36),
            (self.size[0] // 2, self.size[1] // 2),
            self.size[0],
            self.size[0] // 2)

        # The surface in its curent state is the background to every future render, therefore it is
        # saved into an instance variable so it does not need to be drawn more than this one time
        self.cavity = self.surface.copy()

    def compute(self):
        # neuron positions
        # TODO for now they are in a straight line down the middle
        # but other topologies should be possible
        self.neuron_positions = divide_line(
            np.array((self.size[0] / 2, 0)),
            np.array((self.size[0] / 2, self.size[1])),
            self.network.neuron_count[2])

    def draw(self):
        # Draw the current state of the network embedding onto the surface
        self.sufrace = self.cavity.copy()   # reset to background

        # draw neurons
        for pos in self.neuron_positions:
            pygame.draw.circle(
                self.surface,
                "gray",
                pos,
                Embedding.neuron_radius,
                1)
