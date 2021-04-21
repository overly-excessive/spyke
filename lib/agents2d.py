import math
import numpy as np

from . import util2d as u2d
from . import network


class Agent1():
    def __init__(self, position, env):
        self.type = "manual"
        self.env = env
        self.id = self.env.agent_count
        self.pos = position

        self.vel = np.zeros(2)

        self.angle = 0

        self.mass = 1
        self.force = 0
        self.friction = 0.1

        self.radius = 10
        self.color = "blue"

        self.actions = [self.move, self.turn_left, self.turn_right]

    def next(self):

        # If force is applied, the body accelerates
        if self.force > 0:
            accX, accY = u2d.pol2cart(self.force / self.mass, self.angle)
            self.vel += (accX, accY)

        # If the body moves friction slows it down
        if np.linalg.norm(self.vel) <= self.friction:
            self.vel = np.zeros(2)
        else:
            self.vel = self.vel - self.vel / np.linalg.norm(self.vel) * self.friction

        # Adjust the position according to speed
        self.pos += self.vel

        # force decays TODO make it possible for the force to be a float value
        if self.force >= 1: self.force -= 1

    def move(self, force=1):
        self.force += force

    def turn_right(self):
        self.angle += math.radians(15)

    def turn_left(self):
        self.angle -= math.radians(15)


class Agent2(Agent1):
    def __init__(self, position, env):
        super().__init__(position, env)
        self.type = "autonomous"
        self.color = "red"

        # Initialize network
        self.network = network.Network(self)
        self.network.load_network()

    def next(self):
        super().next()

        # iterate the networks
        self.network.next()
