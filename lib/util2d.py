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


# Event queue with possibility of future events but may be useful for other things
class FutureQueue():
    def __init__(self):
        self.head = None

    # Insert event into the event queue at any point future or present
    def insert(self, time, payload):
        block = [time, payload, None]
        # if queue is empty, just add the event and return
        if not self.head:
            self.head = block
            return

        # else, iterate to insertion position
        next = self.head
        previous = None
        while next[2] and block[0] > next[0]:
            previous = next
            next = next[2]

        # and insert event
        if not previous:
            self.head = block
        else:
            previous[2] = block
        block[2] = next

    # check if there is more events for supplied time
    def check(self, time):
        if not self.head: return False
        if self.head[0] == time: return True
        else: return False

    # get next event
    def get(self):
        block = self.head
        self.head = self.head[2]
        return block[1]
