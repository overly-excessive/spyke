import pygame
import time
import math
import numpy as np

from lib.env2d import Environment
import lib.func2d as f2d

pygame.init()
win_size = (1400, 800)

win = pygame.display.set_mode(win_size)
pygame.display.set_caption("Spyke")

# Initialize scene
env_size = (1000, 800)
env = Environment(env_size)
env.add_agent("manual", np.array(env_size)/2)
for i in range(10):
    env.add_agent("autonomous")

# Main loop TODO put the grahics on a separate thread with its own loop
while True:
    # event listener loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            break
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                env.physical[0].move(2)
            elif event.key == pygame.K_RIGHT:
                env.physical[0].angle += math.radians(15)
            elif event.key == pygame.K_LEFT:
                env.physical[0].angle -= math.radians(15)

    # drawing the scene
    win.fill((0,0,0))
    pygame.draw.line(win, "gray", (env_size[0]+1, 0), (env_size[0]+1, win_size[1]))

    # draw agents
    for e in env.physical:
        pygame.draw.circle(win, e.color, e.pos, e.radius)
        # triangle
        A = f2d.pol2cart(7, e.angle) + e.pos
        B = f2d.pol2cart(7, e.angle + math.radians(150)) + e.pos
        C = f2d.pol2cart(7, e.angle + math.radians(210)) + e.pos
        pygame.draw.polygon(win, "black", (A, B, C))

    pygame.display.update()

    env.next()

    # TODO adjust refresh frequency more intelligently
    time.sleep(0.015)
