import numpy as np

from . import neurons
from .util2d import EventQueue


class Network():
    def __init__(self, agent):
        # a refference to the agent object controlled by the network
        self.agent = agent

        # TODO add sensory neurons
        self.inputs = []

        self.outputs = agent.actions

        # For keeping internal time. Increment by one each iteration
        self.clock = 0

        # TODO put this in some more suitable datastructure
        self.interneurons = []

        # events are the ids of the neurons that spiked
        # TODO add other things into the event later like, axon coordinates, maybe neurotransmitter type
        # TODO think about possible maxsize value
        # TODO check if maybe priority que is better for this
        self.event_queue = EventQueue()

        # connectome matrix W where wij is the synnapse weight between ith pre-synaptic and jth post-synaptic neuron
        # it is initialized with only the input and output neurons none of which are connected making the connectome an all zero matrix
        self.neuron_count = len(self.inputs) + len(self.outputs)
        self.connectome = np.zeros((self.neuron_count, self.neuron_count))

    def next(self):
        self.clock += 1
        while self.event_queue.check(self.clock):
            event = self.event_queue.get()

            # make event vector
            e = np.zeros(self.neuron_count)
            e[event] = 1

            result = np.dot(self.connectome, e)
            actions = np.where(result == 1)
            for action in actions[0]:
                self.outputs[action]()
                # TODO only works on output neurons for now, expand to all other types

        # iteration of individual neurons
        for neuron in self.interneurons:
            neuron.next()

    def add_neuron(self):
        # TODO this only adds random neurons for the moment, make it work with other types
        n = neurons.Neuron_random(self, self.neuron_count)
        self.neuron_count += 1
        self.interneurons.append(n)
        # TODO extend connectome matrix when neuron is added

    # TODO add ability to load saved network from file
    def load_network(self):
        # this is just for testing TODO rewrite this completely
        for i in range(3):
            self.add_neuron()
        self.connectome = np.zeros((6, 6))
        self.connectome[0, 3] = 1
        self.connectome[1, 4] = 1
        self.connectome[2, 5] = 1
