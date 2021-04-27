import numpy as np


class Neuron():
    # parent class of all Neurons
    def __init__(self, network, id):
        # A refference to the network object that the neuron is a part of
        self.network = network
        self.axon_lenght = 10   # 10 lentgh units means number of iterations it
                                # takes a spike to reach the end

        # ids start from 0. When sorted by id, the input neurons come first,
        # then output, and interneurons last
        self.id = id

    def spike(self):
        # spike method called when the neuron fires
        # append a spike event to the network event queue
        self.network.event_queue.insert(
            self.network.agent.env.internal_clock + self.axon_lenght, self.id)
        if self.network.agent.env.iface.embedding:
            if self.network.agent.env.iface.selected_agent == self.network.agent.id:
                if self.network.agent.env.iface.embedding.spike_visualization:
                    self.network.agent.env.iface.embedding.spike_queue.put(self.id)

    def add_synapse(self):
        # TODO write this function
        pass


class Neuron_LIF(Neuron):
    # Leaky Integrate and fire Neuron
    def __init__(self, network, id):
        super().__init__(network, id)

        # parameters
        self.neuron_count += 1

        self.threshold = 1.0
        self.leak = 0.01

        # state
        self.activation = 0.0

    def next(self):
        if self.activtion >= self.threshold:
            self.spike()
            self.activation = 0.0

    def excite(self, ammount):
        self.activation += ammount


class Neuron_random(Neuron):
    # Neuron that spikes at random times
    def __init__(self, network, id):
        super().__init__(network, id)

        # the expected value of iterations between consecutive spikes
        self.exp_spike_period = 20
        self.spike_p = 1 / self.exp_spike_period

    def next(self):
        rand = np.random.uniform()
        if rand <= self.spike_p:
            self.spike()
