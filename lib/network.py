import numpy as np
import heapq

from . import neurons


class Network():
    def __init__(self, agent):
        # a refference to the agent object controlled by the network
        self.agent = agent
        self.neuron_count = [0, 0, 0]  # input, output and interneurons respectively

        # TODO add sensory neurons
        self.inputs = []

        # the outputs are always the possible actions the agent can take
        self.outputs = []
        for action in agent.actions:
            self.outputs.append(neurons.OutputNeuron(self, action))

        # TODO put this in some more suitable datastructure
        self.interneurons = []

        # events are the ids of the neurons that spiked
        # TODO add other things into the event later like, axon coordinates,
        # maybe neurotransmitter type
        self.future_queue = []
        heapq.heapify(self.future_queue)

        # connectome matrix W where wij is the synnapse weight between ith pre-synaptic
        # and jth post-synaptic neuron it is initialized with only the input and output
        # neurons none of which are connected making the connectome an all zero matrix
        self.connectome = np.zeros((self.neuron_count[1] + self.neuron_count[2],
                                    self.neuron_count[0] + self.neuron_count[2]))

    def next(self):
        # Create an event vector from all the neurons that spiked
        pre_synaptic_vector = np.zeros((self.connectome.shape[0]), dtype=bool)

        # Fetch all events for current iteration from the future queue and add them to the vector
        try:
            while self.future_queue[0][0] == self.agent.env.internal_clock:
                spike_id = heapq.heappop(self.future_queue)[1]
                if spike_id[0] == 0:
                    pre_synaptic_vector[spike_id[1]] = 1
                else:
                    pre_synaptic_vector[self.neuron_count[0] + spike_id[1]] = 1
        except IndexError:
            pass

        # check if any spikes happened this iteration, because otherwise nothing needs to be done
        if not np.all(pre_synaptic_vector == 0):
            # Now send the pre-synaptic vector through the connectome matrix to get a
            # post-synaptic vector
            post_synaptic_vector = np.dot(self.connectome, pre_synaptic_vector)
            # TODO add a way of knowing for neurons which neuron excited them
            if not np.all(post_synaptic_vector == 0):
                excitations = np.nonzero(post_synaptic_vector)
                for i in excitations:
                    if i < self.neuron_count[1]:
                        self.outputs[i].excite()
                    else:
                        self.interneurons[i - self.neuron_count[1]].excite(post_synaptic_vector[i])

        # iteration of individual neurons
        # TODO setting for neuron iteration per network iteration. currently it is one
        for neuron in self.interneurons:
            neuron.next()

    def add_neuron(self):
        # TODO this only adds random neurons for the moment, make it work with other types
        n = neurons.Neuron_random(self)
        self.inputs.append(n)
        if n.type == "input":
            self.connectome = np.c_[np.zeros(self.connectome.shape[0]), self.connectome]

    # TODO add ability to load saved network from file
    def load_network(self):
        # this is just for testing TODO rewrite this completely
        for i in range(3):
            self.add_neuron()
        self.connectome[0, 0] = 1
        self.connectome[1, 1] = 1
        self.connectome[2, 2] = 1
