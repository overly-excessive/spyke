import pygame
import time
import threading
import math
import numpy as np

from lib.env2d import Environment
import lib.func2d as f2d

# Initializing pygame
pygame.init()
win_size = (1400, 800)

win = pygame.display.set_mode(win_size)
pygame.display.set_caption("Spyke")
font = pygame.font.SysFont("Hermit", 15)

# TODO this function could live in its own graphics module later
def graphics(env):
    clock = pygame.time.Clock()
    while True:
        # reset window to black
        win.fill((0,0,0))

        # event listener loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                env.running = False
                pygame.quit()
                break
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    env.physical[0].move(2)
                elif event.key == pygame.K_RIGHT:
                    env.physical[0].angle += math.radians(15)
                elif event.key == pygame.K_LEFT:
                    env.physical[0].angle -= math.radians(15)

        # drawing window border
        pygame.draw.line(win, "gray", (env_size[0]+1, 0), (env_size[0]+1, win_size[1]))

        # display stats
        fps = int(clock.get_fps())
        img = font.render("fps: " + str(fps) + "   eif: " + str(int(env.iter_freq)), 1, "white")
        win.blit(img, (env_size[0]+2, 1))

        # draw agents
        for e in env.physical:
            pygame.draw.circle(win, e.color, e.pos, e.radius)
            # triangle
            A = f2d.pol2cart(7, e.angle) + e.pos
            B = f2d.pol2cart(7, e.angle + math.radians(150)) + e.pos
            C = f2d.pol2cart(7, e.angle + math.radians(210)) + e.pos
            pygame.draw.polygon(win, "black", (A, B, C))

        pygame.display.update()

        clock.tick(30)


# Initialize environment
env_size = (1000, 800)
env = Environment(env_size)

# start threads
g_thread = threading.Thread(target=graphics, args=[env])
env_thread = threading.Thread(target=env.run)
env_thread.start()
g_thread.start()
