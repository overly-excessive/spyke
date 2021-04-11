from .agents2d import Agent1, Agent2
import lib.func2d as f2d
import random
import math
import numpy as np

class Environment():
    def __init__(self, size):
        self.size = np.array(size)
        self.physical = []

    # Advance to next iteration
    def next(self):

        others = list(self.physical)

        for entity in self.physical:

            # border collisions are fully inelastic,
            # if the wall is hit, normal component of the velocity vector disappears
            adj_pos = np.clip(entity.pos, np.zeros(2) + entity.radius, self.size - entity.radius)
            entity.vel *= adj_pos == entity.pos
            entity.pos = adj_pos

            # TODO put this into its own function and fix collision bug
            # agent collision (the equations are for equal mass objects only)
            others.remove(entity)
            for entity2 in others:

                # get distance to other entity
                pos_diff = entity.pos - entity2.pos
                d = np.linalg.norm(pos_diff)

                # a collision should occur
                if d <= entity.radius + entity2.radius:
                    v1 = entity.vel
                    v2 = entity2.vel
                    entity.vel = v1 - np.dot(v1-v2, pos_diff)/pow(d, 2) * pos_diff
                    entity2.vel = v2 - np.dot(v2-v1, pos_diff)/pow(d, 2) * pos_diff

        for entity in self.physical:
            entity.next()


    def add_agent(self, type, position=None):
        # If position not supplied, put to random position
        if position is None:
            position = np.array((random.uniform(10, self.size[0] - 10), random.uniform(10, self.size[1] - 10)))

        if type == "manual":
            self.physical.append(Agent1(position))
        elif type == "autonomous":
            self.physical.append(Agent2(position))
        else:
            raise ValueError
