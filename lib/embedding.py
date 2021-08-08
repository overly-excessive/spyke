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
        self.scale = 20

        self.input_positions = np.zeros((self.network.neuron_count[0], 2))
        self.output_positions = np.zeros((self.network.neuron_count[1], 2))
        self.neuron_positions = np.zeros((self.network.neuron_count[2], 2, 2))
        # (neuron_id, x/y coordinate, soma/hillock)
        self.dendrite_count = np.count_nonzero(self.network.connectome)
        self.dendrite_positions = np.zeros((self.dendrite_count, 2, 2))
        # (dendrite id, input/output end, x/y coordinate)
        self.dendrite_lookup_dict = {}
        # this is for easily finding dendrite ids based on neuron ids

        # An extra transparent surface to draw spikes on a separate layer
        self.spike_vis_overlay = pygame.Surface(self.size, pygame.SRCALPHA)
        # Storage heap for spike events in progress. The events are of the form:
        # [start of event, end of event, type: "d"endrite/"a"xon, dendrite id/neuron id]
        self.spikes_in_progress = []
        heapq.heapify(self.spikes_in_progress)
        self.spike_frame_num = 0  # to keep track of number of frames computed so far

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
            soma_positions = divide_line(
                np.array((self.size[0] / 2 - 100, 0)),
                np.array((self.size[0] / 2 - 100, self.size[1])),
                self.network.neuron_count[2])
            for i in range(self.network.neuron_count[2]):
                self.neuron_positions[i, 0, 0] = soma_positions[i, 0]
                self.neuron_positions[i, 1, 0] = soma_positions[i, 1]
                displacement = np.array((self.network.interneurons[i].axon_length * self.scale, 0))
                hillock_pos = soma_positions[i] + displacement
                hillock_pos = rotate(hillock_pos, self.network.interneurons[i].axon_angle)
                self.neuron_positions[i, 0, 1] = hillock_pos[0]
                self.neuron_positions[i, 1, 1] = hillock_pos[1]

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
                    pos2 = self.neuron_positions[inter, :, 0]
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
                    pos1 = self.neuron_positions[inter, :, 1]
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
            (pos[0, 0], pos[1, 0]),
            Embedding.neuron_radius,
            2)

        # draw axon
        hillock_pos = pos + np.array((neuron.axon_length * axon_scale, 0))
        hillock_pos = rotate(hillock_pos, neuron.axon_angle)
        pygame.draw.line(
            self.surface,
            Embedding.axon_color,
            (pos[0, 0], pos[1, 0]),
            (pos[0, 1], pos[1, 1]),
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
        self.spike_frame_num += 1

        # every iteration, check the recording queue and register all spike events that happened
        # then transform them into visualization events
        # the spike vis events will be stored in the heap self.spikes_in_progress in the format:
        # (frame number of event, type: dendrite - True/axon - False, dendrite/inter-neuron id)
        # for axon spikes there is a fourth element: internal clock time of spike
        try:
            spike = heapq.heappop(self.network.recording)
            # if spike is from input neuron
            if spike[1].type == "input":
                # get ids of dendrites connecting to neuron
                dendrites = self.dendrite_lookup_dict.get(spike[1].id, [])
                for dendrite_id in dendrites:
                    for i in range(Embedding.flash_duration):
                        heapq.heappush(self.spikes_in_progress,
                                       (self.spike_frame_num + i, True, dendrite_id))

            # if event is from interneuron:
            else:
                heapq.heappush(self.spikes_in_progress,
                               (self.spike_frame_num, False, spike[1].id[1], spike[0]))

        except IndexError:
            pass

        # make note of the environment internal clock time
        env_time = self.network.agent.env.internal_clock

        # Draw
        try:
            while self.spikes_in_progress[0][0] == self.spike_frame_num:
                vis_event = heapq.heappop(self.spikes_in_progress)
                if vis_event[1]:
                    pygame.draw.line(
                        self.spike_vis_overlay,
                        Embedding.spike_color,
                        self.dendrite_positions[vis_event[2], 0],
                        self.dendrite_positions[vis_event[2], 1],
                        1)
                else:
                    time = env_time - vis_event[3]
                    pos1 = self.neuron_positions[vis_event[2], :, 0]
                    pos2 = self.neuron_positions[vis_event[2], :, 1]
                    duration = self.network.interneurons[vis_event[2]].axon_length
                    pos = pos1 + (pos2 - pos1) * time / duration
                    if np.linalg.norm(pos - pos1) <= np.linalg.norm(pos2 - pos1):
                        pygame.draw.circle(
                            self.spike_vis_overlay,
                            Embedding.spike_color,
                            pos,
                            Embedding.spike_radius)

                        heapq.heappush(self.spikes_in_progress,
                                       (self.spike_frame_num + 1,
                                        False,
                                        vis_event[2],
                                        vis_event[3]))

                    else:
                        dendrites = self.dendrite_lookup_dict.get((2, vis_event[2]), [])
                        for dendrite_id in dendrites:
                            for i in range(Embedding.flash_duration):
                                heapq.heappush(self.spikes_in_progress,
                                               (self.spike_frame_num + i + 1, True, dendrite_id))

                    # TODO, propagate spike recursively add next vis event to spikes in progress
                    # Bug: time sometimes set to -1
        except IndexError:
            pass
