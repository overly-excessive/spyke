import numpy as np


def pol2cart(rho, phi):
    x = rho * np.cos(phi)
    y = rho * np.sin(phi)
    return np.array((x, y))


def divide_line(Apos, Bpos, n):
    result = np.zeros((n, 2))
    inter_dist_vec = (Bpos - Apos) / (n + 1)
    for i in range(n):
        result[i, 0] = Apos[0] + (i + 1) * inter_dist_vec[0]
        result[i, 1] = Apos[1] + (i + 1) * inter_dist_vec[1]
    return result


# Only works with lists of form [time, id, next], these are referred to as events
class EventQueue():
    def __init__(self):
        self.head = None

    # Insert event into the event queue
    def insert(self, time, id):
        event = [time, id, None]
        # if queue is empty, just add the event and return
        if not self.head:
            self.head = event
            return

        # else, iterate to insertion position
        next = self.head
        previous = None
        while next[2] and event[0] > next[0]:
            previous = next
            next = next[2]

        # and insert event
        if not previous:
            self.head = event
        else:
            previous[2] = event
        event[2] = next

    # check if there is more events for supplied time
    def check(self, time):
        if not self.head: return False
        if self.head[0] == time: return True
        else: return False

    # get next event
    def get(self):
        event = self.head
        self.head = self.head[2]
        return event[1]
