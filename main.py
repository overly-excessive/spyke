import pygame
import threading
import math
import numpy as np

from lib.env2d import Environment
import lib.util2d as u2d


class Interface():

    def __init__(self):
        # Declare some variables
        self.win_size = (1920, 1015)
        self.net_win_size = 500
        self.env_size = (self.win_size[0] - self.net_win_size, self.win_size[1])
        self.running = False
        self.fps = 30
        self.selected_agent = -1    # -1 means none here
        self.displayed_agent = -1
        self.embedding = None

    def setup(self):
        # Initialize graphical interface
        pygame.init()
        self.win = pygame.display.set_mode(self.win_size)
        pygame.display.set_caption("Spyke")
        self.font = pygame.font.SysFont("Hermit", 15)
        self.clock = pygame.time.Clock()
        self.running = True

        # Initialize environment model
        self.env = Environment(self.env_size)
        self.env_thread = threading.Thread(target=self.env.run)
        self.env_thread.start()

    def quit(self):
        # stop environment and exit
        self.running = False
        self.env.running = False
        pygame.quit()

    def handle(self, event):

        # Handle keypresses
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.env.physical[0].move(1)
            elif event.key == pygame.K_RIGHT:
                self.env.physical[0].turn_right()
            elif event.key == pygame.K_LEFT:
                self.env.physical[0].turn_left()

        # Handle mouse events
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mpos = np.array(pygame.mouse.get_pos())
            # Check if agent was clicked
            for entity in self.env.physical:
                dist = np.linalg.norm(entity.pos - mpos)
                if dist <= entity.radius:
                    self.selected_agent = entity.id

    def render(self):

        # Reuseable rendering functions:
        def display_text(text, pos):
            # Displays one line of text at position
            img = self.font.render(text, 1, "white")
            self.win.blit(img, pos)

        # TODO function for displaying dictionaries

        # DRAW WINDOW BORDERS
        pygame.draw.line(
            self.win,
            "gray",
            (self.env_size[0], 0),
            (self.env_size[0], self.win_size[1])
        )
        pygame.draw.line(
            self.win,
            "gray",
            (self.env_size[0], self.net_win_size),
            (self.win_size[0], self.net_win_size)
        )

        # DISPLAY STATS
        fps_current = int(self.clock.get_fps())
        text = "fps: " + str(fps_current) + "   eif: " + str(int(self.env.iter_freq))
        display_text(text, (self.env_size[0] + 2, self.net_win_size + 2))

        # TODO DRAW CONTROL BUTTONS

        # DRAW AGENTS
        for e in self.env.physical:
            pygame.draw.circle(self.win, e.color, e.pos, e.radius)
            # triangle
            A = u2d.pol2cart(7, e.angle) + e.pos
            B = u2d.pol2cart(7, e.angle + math.radians(150)) + e.pos
            C = u2d.pol2cart(7, e.angle + math.radians(210)) + e.pos
            pygame.draw.polygon(self.win, "black", (A, B, C))

        # DRAW NETWORK
        # check if selection changed, because only then a new embedding is generated
        if self.displayed_agent != self.selected_agent:
            self.embedding = u2d.Embedding(
                self.env.physical[self.selected_agent].network,
                np.ones(2) * self.net_win_size)
            self.embedding.compute()
            self.displayed_agent = self.selected_agent

        # only if agent is selected
        if self.selected_agent != -1:
            # display agent id
            display_text("id: " + str(self.selected_agent), (self.env_size[0] + 2, 2))

            # display inputs
            for pos in self.embedding.input_positions:
                pygame.draw.rect(
                    self.win,
                    "gray",
                    (pos + np.array((self.env_size[0], 0)),
                        (u2d.Embedding.square_size, u2d.Embedding.square_size)),
                    1)

            # display outputs
            for pos in self.embedding.output_positions:
                pygame.draw.rect(
                    self.win,
                    "gray",
                    (pos + np.array((self.env_size[0], 0)),
                        (u2d.Embedding.square_size, u2d.Embedding.square_size)),
                    1)

        # TODO display neurons
        # TODO display synapses

    def run(self):
        self.setup()
        while self.running:

            # reset window to black
            self.win.fill((0, 0, 0))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                    return
                else:
                    self.handle(event)

            self.render()
            pygame.display.update()
            self.clock.tick(self.fps)


if __name__ == '__main__':
    gui = Interface()
    gui.run()
