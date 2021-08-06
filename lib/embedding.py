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
        self.dendrite_lookup_dict = {}
        # this is for easily finding dendrite ids based on neuron ids

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
            rot = -(i + 1) * arc - np.pi / 2
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
            rot = (i + 1) * arc - np.pi / 2
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
                np.array((self.size[0] / 2 - 100, 0)),
                np.array((self.size[0] / 2 - 100, self.size[1])),
                self.network.neuron_count[2])
        else:
            pass
            # TODO for now they are in a straight line down the middle
            # but other topologies should be possible

    def compute_dendrite_positions(self):
        # Computes all dendrite positions based on the connectome and neuron positions

        dendrite_id = 0  # keep track, increment when dendrite computed

        # TODO following for loops can be merged

        # INPUT to OUTPUT dendrites:
        for ip in range(self.network.neuron_count[0]):
            for op in range(self.network.neuron_count[1]):
                if self.network.connectome[op, ip]:
                    pos1 = self.input_positions[ip, :]
                    pos2 = self.output_positions[op, :]
                    pos1, pos2 = Embedding.shorten_synapse(pos1, pos2, "both")
                    self.dendrite_positions[dendrite_id, 0, :] = pos1
                    self.dendrite_positions[dendrite_id, 1, :] = pos2
                    if (0, ip) in self.dendrite_lookup_dict:
                        self.dendrite_lookup_dict[(0, ip)].append(dendrite_id)
                    else:
                        self.dendrite_lookup_dict[(0, ip)] = [dendrite_id]
                    dendrite_id += 1

        # INPUT to INTERNEURON dendrites:
        for ip in range(self.network.neuron_count[0]):
            for inter in range(self.network.neuron_count[2]):
                if self.network.connectome[inter + self.network.neuron_count[1], ip]:
                    pos1 = self.input_positions[ip, :]
                    pos2 = self.neuron_positions[inter, :]
                    pos1, pos2 = Embedding.shorten_synapse(pos1, pos2, "both")
                    self.dendrite_positions[dendrite_id, 0, :] = pos1
                    self.dendrite_positions[dendrite_id, 1, :] = pos2
                    if (0, ip) in self.dendrite_lookup_dict:
                        self.dendrite_lookup_dict[(0, ip)].append(dendrite_id)
                    else:
                        self.dendrite_lookup_dict[(0, ip)] = [dendrite_id]
                    dendrite_id += 1

        # INTERNEURON to OUTPUT dendrites:
        for op in range(self.network.neuron_count[1]):
            for inter in range(self.network.neuron_count[2]):
                if self.network.connectome[op, inter + self.network.neuron_count[0]]:
                    pos1 = self.neuron_positions[inter, :] + np.array((200, 0))
                    # TODO fix this, only works with fixed axons
                    pos2 = self.output_positions[op, :]
                    pos1, pos2 = Embedding.shorten_synapse(pos1, pos2, "output")
                    self.dendrite_positions[dendrite_id, 0, :] = pos1
                    self.dendrite_positions[dendrite_id, 1, :] = pos2
                    if (2, inter) in self.dendrite_lookup_dict:
                        self.dendrite_lookup_dict[(2, inter)].append(dendrite_id)
                    else:
                        self.dendrite_lookup_dict[(2, inter)] = [dendrite_id]
                    dendrite_id += 1

        # INTER-INTER dendrites: TODO

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
            (pos[0], pos[1]),
            Embedding.neuron_radius,
            2)

        # draw axon
        pygame.draw.line(
            self.surface,
            Embedding.axon_color,
            (pos[0], pos[1]),
            (pos[0] + neuron.axon_lenght * axon_scale, pos[1]),
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

    def draw_spikes(self):
        self.spike_vis_overlay = pygame.Surface(self.size, pygame.SRCALPHA)

        # every iteration, check the recording queue and register all spike events that happened
        # the spikes will be stored in the list self.spikes_in_progress in the format:
        # [start of event, end of event, type: "d"endrite/"a"xon, neuron id]
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
                        event[2]])
                # if event is from interneuron:
            else:
                self.spikes_in_progress.append([
                    event[0],
                    event[0] + self.network.interneurons[event[2][1]].axon_lenght,
                    "a",
                    event[2]])
                self.spikes_in_progress.append([
                    event[0] + self.network.interneurons[event[2][1]].axon_lenght,
                    event[0] + self.network.interneurons[event[2][1]].axon_lenght
                    + Embedding.flash_duration,
                    "d",
                    event[2]])

        except IndexError:
            pass

        # Remove spent events from list # TODO figure out how to remove and draw in one pass
        self.spikes_in_progress = [x for x in self.spikes_in_progress if
                                   x[1] > self.network.agent.env.internal_clock]
        # Draw
        for spike in self.spikes_in_progress:
            if spike[2] == "d":
                # get dendrite ids
                if spike[3] in self.dendrite_lookup_dict:
                    ids = self.dendrite_lookup_dict[spike[3]]
                    for id in ids:
                        pygame.draw.line(
                            self.spike_vis_overlay,
                            Embedding.spike_color,
                            self.dendrite_positions[id, 0],
                            self.dendrite_positions[id, 1],
                            1)
            else:
                pos1 = self.neuron_positions[spike[3][1]]
                pos2 = pos1 + np.array((200, 0))  # TODO only works with fixed axons, generalize
                time = self.network.agent.env.internal_clock - spike[0]
                pos = pos1 + (pos2 - pos1) * time / (spike[1] - spike[0])
                pygame.draw.circle(
                    self.spike_vis_overlay,
                    Embedding.spike_color,
                    pos,
                    Embedding.spike_radius)
