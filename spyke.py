import pygame
import pygame_gui

import numpy as np

import gui


class Interface():

    def __init__(self):
        # Static Variables
        self.win_size = (1920, 1018)
        self.fps = 30
        self.background = (67, 93, 80)
        self.padding = 15   # gap between gui elements
        self.button_height = 30  # height of buttons, selectors, sliders, etc.
        self.button_width = 60  # width of buttons only

        # Initialize graphical interface
        pygame.init()
        self.win = pygame.display.set_mode(self.win_size)
        pygame.display.set_caption("Spyke")
        self.font = pygame.font.SysFont("Hermit", 15)
        self.manager = pygame_gui.UIManager(self.win_size, "theme.json")
        self.clock = pygame.time.Clock()
        self.running = True

        # Initialize GUI elements
        self.env_control_win = gui.EnvControlWin(self)
        self.message_win = gui.MessageWin(self)
        self.stats_win = gui.StatsWin(self)
        self.command_win = gui.CommandWin(self)
        self.env_win = None
        self.agent_win = None
        self.net_win = None

    def quit(self):
        # stop running processes and exit
        # TODO stop & save env if running
        self.running = False
        if self.env_win:
            if self.env_win.env.running:
                self.env_win.env.running = False
        pygame.quit()

    def open_env_win(self):
        # TODO several env windows possible
        if self.env_win is not None: return
        # TODO check which env is selected

        self.env_win = gui.EnvWin(self)

    def open_net_win(self, agent):
        if self.net_win is not None: return
        self.net_win = gui.NetWin(self, agent)

    def handle(self, event):
        self.manager.process_events(event)

        # Handle keypresses
        if self.env_win and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.env_win.env.agents[0].move(1)
            elif event.key == pygame.K_RIGHT:
                self.env_win.env.agents[0].turn_right()
            elif event.key == pygame.K_LEFT:
                self.env_win.env.agents[0].turn_left()

        # Handle GUI Events
        if event.type == pygame.USEREVENT:

            # Environment Controll Events
            if hasattr(event.ui_element, "ui_container"):
                if event.ui_element.ui_container == self.env_control_win.get_container():
                    self.env_control_win.handle(event)

                if self.agent_win:
                    if event.ui_element.ui_container == self.agent_win.get_container():
                        if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                            if event.ui_element == self.agent_win.show_button:
                                self.open_net_win(self.agent_win.agent)

                if self.net_win:
                    if event.ui_element.ui_container == self.net_win._window_root_container:
                        if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                            if event.ui_element == self.net_win.spikes_button:
                                self.net_win.toggle_spikes()

        # Handle Mouse Events
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mpos = pygame.mouse.get_pos()
            # if there is an env window and if click was inside it
            if self.env_win:
                env_rect = self.env_win.get_container().get_rect()
                if env_rect.collidepoint(mpos):
                    # trasnform mouse pos into env coordinates
                    mpos = np.array(mpos)
                    scale = self.env_win.env.size[0] / self.env_win.scaled_surface.get_width()
                    mpos = (mpos - np.array((env_rect.left, env_rect.top))) * scale

                    # iterate through agents, check if one was clicked, if yes select it
                    old_select = self.env_win.selected_agent
                    for a in self.env_win.env.agents:
                        dist = np.linalg.norm(a.pos - mpos)
                        if dist <= a.radius:
                            self.env_win.selected_agent = a.id
                            if self.agent_win: self.agent_win.kill()
                            self.agent_win = gui.AgentWin(self, a.id)

                    # if selection not changed, deselect
                    if self.env_win.selected_agent == old_select:
                        if self.agent_win: self.agent_win.kill()
                        self.env_win.selected_agent = None

        # Handle keypresses
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.command_win.text_entry.focus()
                self.command_win.enter()

    def run(self):
        while self.running:

            # reset window to background color
            self.win.fill(self.background)

            # check for events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                    return
                else:
                    self.handle(event)

            # render, set fps and update screen
            self.manager.draw_ui(self.win)
            delta = self.clock.tick(self.fps) / 1000.0
            pygame.display.update()
            self.manager.update(delta)


if __name__ == '__main__':
    app = Interface()
    app.run()
