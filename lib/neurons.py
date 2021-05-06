import numpy as np
import heapq


class NeuronBase():
    # parent class of all Neurons
    def __init__(self, network, type):
        # A refference to the network object that the neuron is a part of
        self.network = network
        self.type = type

        if type == "input":
            self.id = (0, network.neuron_count[0])
            network.neuron_count[0] += 1
        elif type == "output":
            self.id = (1, network.neuron_count[1])
            network.neuron_count[1] += 1
        elif type == "inter":
            self.id = (2, network.neuron_count[2])
            network.neuron_count[2] += 1
        else:
            raise ValueError


class InputNeuron(NeuronBase):
    def __init__(self, network):
        super().__init__(network, "input")

    def spike(self):
        heapq.heappush(
            self.network.future_queue,
            [self.network.agent.env.internal_clock + 1, self.id])


class OutputNeuron(NeuronBase):
    def __init__(self, network, action):
        self.action = action
        super().__init__(network, "output")

    def excite(self):
        self.action()


class Neuron(NeuronBase):
    def __init__(self, network):
        super().__init__(network, "inter")

        self.axon_lenght = 10

    def spike(self):
        # spike method called when the neuron fires
        # push a spike event to the network event heap
        heapq.heappush(
            self.network.future_queue,
            [self.network.agent.env.internal_clock + 1, self.id])

        # TODO spike tracking disabled
        # if self.network.agent.env.iface.embedding:
        #     if self.network.agent.env.iface.selected_agent == self.network.agent.id:
        #         if self.network.agent.env.iface.embedding.spike_visualization:
        #             self.network.agent.env.iface.embedding.spike_queue.put(self.id)

    def excite(self, value):
        pass

    def add_synapse(self):
        # TODO write this function
        pass


class Neuron_LIF(Neuron):
    # Leaky Integrate and fire Neuron
    def __init__(self, network):
        super().__init__(network)

        # parameters
        self.threshold = 1.0
        self.leak = 0.1

        # state
        self.activation = 0.0

    def next(self):
        if self.activation >= self.threshold:
            self.spike()
            self.activation = 0.0
        elif self.activation > 0.0:
            self.activation = self.activation * (1 - self.leak)
        else: self.activation = 0.0

    def excite(self, value):
        self.activation += value


class Neuron_random(InputNeuron):
    # Neuron that spikes at random times
    def __init__(self, network):
        super().__init__(network)

        # the expected value of iterations between consecutive spikes
        self.exp_spike_period = 20
        self.spike_p = 1 / self.exp_spike_period

    def next(self):
        rand = np.random.uniform()
        if rand <= self.spike_p:
            self.spike()
