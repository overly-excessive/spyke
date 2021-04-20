import pygame
import threading
import math

from lib.env2d import Environment
import lib.func2d as f2d


class Interface():

    def __init__(self):
        # Declare some variables
        self.win_size = (1920, 1080)
        self.env_size = (1500, 1080)
        self.running = False
        self.fps = 30

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

        # TODO handle mouse events

    def render(self):
        # drawing window border
        pygame.draw.line(
            self.win,
            "gray",
            (self.env_size[0] + 1, 0),
            (self.env_size[0] + 1, self.win_size[1]))

        # display stats
        fps_current = int(self.clock.get_fps())
        img = self.font.render(
            "fps: " +
            str(fps_current) +
            "   eif: " +
            str(int(self.env.iter_freq)),
            1, "white")

        self.win.blit(img, (self.env_size[0] + 2, 1))

        # draw agents
        for e in self.env.physical:
            pygame.draw.circle(self.win, e.color, e.pos, e.radius)
            # triangle
            A = f2d.pol2cart(7, e.angle) + e.pos
            B = f2d.pol2cart(7, e.angle + math.radians(150)) + e.pos
            C = f2d.pol2cart(7, e.angle + math.radians(210)) + e.pos
            pygame.draw.polygon(self.win, "black", (A, B, C))

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
