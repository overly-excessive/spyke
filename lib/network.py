import numpy as np
import heapq

from . import neurons


class Network():
    def __init__(self, agent):
        # a refference to the agent object controlled by the network
        self.agent = agent
        self.neuron_count = [0, 0, 0]  # input, output and interneurons respectively
        # the neuron count is accessed and incremented by the neuron init function

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

        # connectome matrix W where wij is the synnapse weight between ith post-synaptic
        # and jth pre-synaptic neuron it is initialized with only the input and output
        # neurons none of which are connected making the connectome an all zero matrix
        self.connectome = np.zeros((self.neuron_count[1] + self.neuron_count[2],
                                    self.neuron_count[0] + self.neuron_count[2]))

        # A flag if the network is being recorded
        self.spike_tracking = False
        # Another queue for spike tracking
        self.recording = []
        heapq.heapify(self.recording)

    def next(self):
        # first, iteration of individual neurons
        # TODO setting for neuron iteration per network iteration. currently it is one
        for neuron in self.inputs:
            neuron.next()
        for neuron in self.interneurons:
            neuron.next()

        # Create an event vector from all the neurons that spiked
        pre_synaptic_vector = np.zeros((self.connectome.shape[1]), dtype=bool)

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
        if not np.all(pre_synaptic_vector is False):
            # Now send the pre-synaptic vector through the connectome matrix to get a
            # post-synaptic vector
            post_synaptic_vector = np.dot(self.connectome, pre_synaptic_vector)
            # TODO add a way of knowing for neurons which neuron excited them
            if not np.all(post_synaptic_vector == 0.0):
                excitations = np.nonzero(post_synaptic_vector)[0]
                for i in excitations:
                    if i < self.neuron_count[1]:
                        self.outputs[i].excite()
                    else:
                        self.interneurons[i - self.neuron_count[1]].excite(post_synaptic_vector[i])

    def add_neuron(self, neuron):
        if neuron.type == "input":
            self.inputs.append(neuron)
            self.connectome = np.hstack((self.connectome[:, 0:len(self.inputs)],
                                        np.zeros(self.connectome.shape[0])[:, None],
                                        self.connectome[:, len(self.inputs):]))
        if neuron.type == "output":
            self.outputs.append(neuron)
            self.connectome = np.vstack((self.connectome[0:len(self.outputs), :],
                                        np.zeros(self.connectome.shape[1]),
                                        self.connectome[len(self.outputs):, :]))
        if neuron.type == "inter":
            self.interneurons.append(neuron)
            self.connectome = np.hstack((self.connectome,
                                        np.zeros(self.connectome.shape[0])[:, None]))
            self.connectome = np.vstack((self.connectome, np.zeros(self.connectome.shape[1])))

    # TODO add ability to load saved network from file
    def load_network(self):
        # load network state from file
        pass

        # this is just for testing TODO rewrite this completely
        # for i in range(3):
        #     self.add_neuron(neurons.Neuron_random(self))
        # self.connectome[0, 0] = 1
        # self.connectome[1, 1] = 1
        # self.connectome[2, 2] = 1
        #
        # for i in range(4):
        #     self.add_neuron(neurons.Neuron_LIF(self))
        #
        # self.connectome[3, 0] = 1
        # self.connectome[0, 3] = 1
        # self.connectome[5, 1] = 1
        # self.connectome[6, 5] = 1
        # self.connectome[2, 6] = 1

    def save_network(self):
        # save network state to file
        pass

    def grow(self, dna):
        # grow network from dna sequence

        # place the frist cell
        self.add_neuron(neurons.Neuron_LIF(self))
