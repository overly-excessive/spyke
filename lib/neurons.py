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

    def __lt__(self, other):
        return self.id < other.id


class InputNeuron(NeuronBase):
    def __init__(self, network):
        super().__init__(network, "input")

    def spike(self):
        heapq.heappush(
            self.network.future_queue,
            (self.network.agent.env.internal_clock, self.id))

        # Spike tracking
        if self.network.spike_tracking:
            heapq.heappush(
                self.network.recording,
                (self.network.agent.env.internal_clock, self))


class OutputNeuron(NeuronBase):
    def __init__(self, network, action):
        self.action = action
        super().__init__(network, "output")

    def excite(self):
        self.action()


class Neuron(NeuronBase):
    def __init__(self, network):
        super().__init__(network, "inter")

        self.axon_length = 10
        self.axon_angle = 0

    def spike(self):
        # spike method called when the neuron fires
        # push a spike event to the network event heap
        heapq.heappush(
            self.network.future_queue,
            (self.network.agent.env.internal_clock + self.axon_length, self.id))

        # Spike tracking
        if self.network.spike_tracking:
            heapq.heappush(
                self.network.recording,
                (self.network.agent.env.internal_clock, self))

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
        self.threshold = 0.9
        self.leak = 0.01

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
    # Neuron that spikes at random times, handled as a type of input neuron
    def __init__(self, network):
        super().__init__(network)

        # the expected value of iterations between consecutive spikes
        self.exp_spike_period = 20
        self.spike_p = 1 / self.exp_spike_period

    def next(self):
        rand = np.random.uniform()
        if rand <= self.spike_p:
            self.spike()


class GrowingNeuron(Neuron_LIF):
    def __init__(self, network, dna):
        super().__init__(network)

        self.dna = dna
        self.pos = np.array((0, 0))
        self.genetic_functions = {"A": self.divide()}

    def read_dna(self):
        reading = True
        instruction = ""
        while reading:
            instruction += self.dna[0]
            break

    def change_pos(self, dx, dy):
        self.pos += np.array((dx, dy))

    def rotate_axon(self, alpha):
        self.axon_angle += alpha

    def divide(self):
        pass

    def next(self):
        super().next()
        self.read_dna()
