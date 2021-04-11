import math
import random
import numpy as np

from . import func2d as f2d

class Agent1():
    def __init__(self, position):
        self.type = "manual"

        #TODO these should be numpy vectors
        self.pos = position

        self.vel = np.zeros(2)

        self.angle = 0

        self.mass = 1
        self.force = 0
        self.friction = 0.1

        self.radius = 10
        self.color = "blue"

    def next(self):

        # If force is applied, the body accelerates
        if self.force > 0:
            accX, accY = f2d.pol2cart(self.force/self.mass, self.angle)
            self.vel += (accX, accY)

        # If the body moves friction slows it down
        if np.linalg.norm(self.vel) <= self.friction:
            self.vel = np.zeros(2)
        else:
            self.vel = self.vel - self.vel/np.linalg.norm(self.vel) * self.friction

        # Adjust the position according to speed
        self.pos += self.vel

        # force decays TODO make it possible for the force to be a float value
        if self.force >= 1: self.force -= 1

    def move(self, force):
        self.force += force

class Agent2(Agent1):
    def __init__(self, position):
        super().__init__(position)
        self.type = "autonomous"
        self.color = "red"
