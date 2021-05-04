import numpy as np
import pygame

from . import network
from .util2d import rotate


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

        top = np.array((self.size[0] / 2, 0))
        center = np.array(self.size) / 2

        # TODO save input and output positions to an instance variable

        # draw the inputs on the surface:
        arc = np.pi / (self.network.neuron_count[0] + 1)
        for i, neuron in zip(range(self.network.neuron_count[0]), self.network.inputs):
            rot = (i + 1) * arc + np.pi / 2
            pygame.draw.circle(
                self.surface,
                Embedding.input_color,
                rotate(top, rot) + center,
                Embedding.neuron_radius)

        # draw outputs
        arc = np.pi / (self.network.neuron_count[1] + 1)
        for i, neuron in zip(range(self.network.neuron_count[1]), self.network.outputs):
            rot = -(i + 1) * arc + np.pi / 2
            pygame.draw.circle(
                self.surface,
                Embedding.output_color,
                rotate(top, rot) + center,
                Embedding.neuron_radius)

        # brain cavity
        pygame.draw.circle(
            self.surface,
            (32, 38, 36),
            (self.size[0] // 2, self.size[1] // 2),
            self.size[0],
            self.size[0] // 2)
