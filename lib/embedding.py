import numpy as np
import pygame
import heapq

from . import network
from .util2d import rotate, divide_line


# Object that generates a 2D representation of a network
class Embedding():

    input_color = (93, 147, 181)  # kinda blue
    output_color = (70, 180, 78)  # kinda green
    node_color = (121, 149, 117)  # light gray
    axon_color = (185, 144, 89)   # pale orange
    dendrite_color = "white"
    spike_color = (228, 221, 52)  # bright yellow
    neuron_radius = 8   # circles represent neurons
    spike_radius = 3    # smaller circles represent spikes
    flash_duration = 5  # if a pointlike event occurs, its representation lasts this many frames

    def __init__(self, net: network.Network, surface, type="line"):
        self.type = type
        self.network = net
        self.surface = surface.copy()
        self.size = surface.get_size()

        self.input_positions = np.zeros((self.network.neuron_count[0], 2))
        self.output_positions = np.zeros((self.network.neuron_count[1], 2))
        self.neuron_positions = np.zeros((self.network.neuron_count[2], 2))
        self.dendrite_count = np.count_nonzero(self.network.connectome)
        self.dendrite_positions = np.zeros((self.dendrite_count, 2, 2))
        # (dendrite id, input/output end, x/y coordinate)

        # An extra transparent surface to draw spikes on a separate layer
        self.spike_vis_overlay = pygame.Surface(self.size, pygame.SRCALPHA)
        # Storage list for spike events in progress. The events are of the form:
        # [start of event, end of event, type: "d"endrite/"a"xon, dendrite id/neuron id]
        self.spikes_in_progress = []

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

    @ staticmethod
    def shorten_synapse(pos1, pos2, side="output"):
        # shorten the synapse representation for aesthetic purposes
        direction_vec = pos2 - pos1
        unit_vec = (direction_vec) / np.linalg.norm(direction_vec)

        pos2_new = pos2 - Embedding.neuron_radius * unit_vec
        pos1_new = pos1 + Embedding.neuron_radius * unit_vec

        if side == "output":
            return pos1, pos2_new
        elif side == "both":
            return pos1_new, pos2_new

    def compute_neuron_positions(self):
        if self.type == "line":
            self.neuron_positions = divide_line(
                np.array((self.size[0] / 2, 0)),
                np.array((self.size[0] / 2, self.size[1])),
                self.network.neuron_count[2])
        else:
            pass
            # TODO for now they are in a straight line down the middle
            # but other topologies should be possible

    def compute_dendrite_positions(self):
        # Computes all dendrite positions based on the connectome and neuron positions

        dendrite_id = 0  # keep track, increment when dendrite computed

        # INPUT to OUTPUT dendrites:
        for ip in range(self.network.neuron_count[0]):
            for op in range(self.network.neuron_count[1]):
                if self.network.connectome[op, ip]:
                    pos1 = self.input_positions[ip, :]
                    pos2 = self.output_positions[op, :]
                    pos1, pos2 = Embedding.shorten_synapse(pos1, pos2, "both")
                    self.dendrite_positions[dendrite_id, 0, :] = pos1
                    self.dendrite_positions[dendrite_id, 1, :] = pos2
                    dendrite_id += 1

    def compute(self):
        # Compute or recompute the embedding.
        # This is a wrapper funcion for the subfunctions that compute the embedding together
        self.compute_neuron_positions()
        self.compute_dendrite_positions()

    def draw_neuron(self, neuron, pos):
        axon_scale = 20

        # draw soma
        pygame.draw.circle(
            self.surface,
            Embedding.node_color,
            (pos[0] - neuron.axon_lenght * axon_scale / 2, pos[1]),
            Embedding.neuron_radius,
            2)

        # draw axon
        pygame.draw.line(
            self.surface,
            Embedding.axon_color,
            (pos[0] - neuron.axon_lenght * axon_scale / 2, pos[1]),
            (pos[0] + neuron.axon_lenght * axon_scale / 2, pos[1]),
            2)

    def draw(self):
        # Draw the current state of the network embedding onto the surface
        self.sufrace = self.cavity.copy()   # reset to background

        # draw inter neurons
        for i, pos in zip(range(self.network.neuron_count[2]), self.neuron_positions):
            self.draw_neuron(self.network.interneurons[i], pos)

        # draw dendrites
        for pos in self.dendrite_positions:
            pygame.draw.line(
                self.surface,
                Embedding.dendrite_color,
                pos[0],
                pos[1],
                1)

    def find_dendrite(self):
        pass

    def draw_spikes(self):
        self.spike_vis_overlay = pygame.Surface(self.size, pygame.SRCALPHA)

        # every iteration, check the recording queue and register all events that happened
        # the events will be stored in the list self.spikes_in_progress in the format:
        # [start of event, end of event, type: "d"endrite/"a"xon, dendrite id/neuron id]
        try:
            event = heapq.heappop(self.network.recording)
            # if event is a dendrite flash
            if not event[1]:
                # if the flash is from an input neuron
                if event[2][0] == 0:
                    self.spikes_in_progress.append([
                        event[0],
                        event[0] + Embedding.flash_duration,
                        "d",
                        event[2][1]])  # TODO the dendrite id is only equal to neuron id in some
                                # very specific circumstances, this code needs to be generalized

        except IndexError:
            pass

        # Remove spent events from list
        self.spikes_in_progress = [x for x in self.spikes_in_progress if
                                   x[1] > self.network.agent.env.internal_clock]

        # Draw
        for event in self.spikes_in_progress:
            pygame.draw.line(
                self.spike_vis_overlay,
                Embedding.spike_color,
                self.dendrite_positions[event[3], 0],
                self.dendrite_positions[event[3], 1],
                1)
