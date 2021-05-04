import pygame
import pygame_gui

from math import radians
from threading import Thread

from lib.env2d import Environment
from lib.util2d import pol2cart
from lib.embedding import Embedding
# Gui Window Module Classes


class EnvControlWin(pygame_gui.elements.ui_window.UIWindow):
    def __init__(self, iface):
        # Static Variables
        self.iface = iface
        self.pos = (0, 0)
        self.dropdown_menu_width = 130
        self.speed_slider_width = 200
        self.size = (702, 115)

        # Window Frame
        super().__init__(
            rect=pygame.Rect(self.pos, self.size),
            manager=iface.manager,
            window_display_title="Environment Control",
            object_id="env_ctrl_win")

        # GUI ELEMENTS
        # Env selector
        self.env_selector = pygame_gui.elements.ui_drop_down_menu.UIDropDownMenu(
            options_list=["Basic 2D", "Single-agent"],  # TODO define this list dynamically
            starting_option="Basid 2D",
            relative_rect=pygame.Rect(
                (iface.padding, iface.padding),
                (self.dropdown_menu_width, iface.button_height)),
            manager=iface.manager,
            container=self)

        # Buttons
        self.new_button = pygame_gui.elements.ui_button.UIButton(
            relative_rect=pygame.Rect(
                (self.dropdown_menu_width + 2 * iface.padding, iface.padding),
                (iface.button_width, iface.button_height)),
            text="New",
            manager=iface.manager,
            container=self)

        self.load_button = pygame_gui.elements.ui_button.UIButton(
            relative_rect=pygame.Rect(
                (self.dropdown_menu_width + iface.button_width + 3 * iface.padding, iface.padding),
                (iface.button_width, iface.button_height)),
            text="Load",
            manager=iface.manager,
            container=self)

        self.save_button = pygame_gui.elements.ui_button.UIButton(
            relative_rect=pygame.Rect(
                (self.dropdown_menu_width + 2 * iface.button_width + 4 * iface.padding,
                    iface.padding),
                (iface.button_width, iface.button_height)),
            text="Save",
            manager=iface.manager,
            container=self)

        self.start_button = pygame_gui.elements.ui_button.UIButton(
            relative_rect=pygame.Rect(
                (self.dropdown_menu_width + 3 * iface.button_width + 5 * iface.padding,
                    iface.padding),
                (iface.button_width, iface.button_height)),
            text="Start",
            manager=iface.manager,
            container=self)

        # Speed Slider
        self.speed_slider = pygame_gui.elements.ui_horizontal_slider.UIHorizontalSlider(
            relative_rect=pygame.Rect(
                (self.dropdown_menu_width + 4 * iface.button_width + 6 * iface.padding,
                 iface.padding),
                (self.speed_slider_width, iface.button_height)),
            start_value=10,
            value_range=(0, 100),
            manager=iface.manager,
            container=self)

    def handle(self, event):
        if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.new_button:
                self.iface.open_env_win()
                # TODO add check of dropdown list which env is selected

            elif event.ui_element == self.load_button:
                pass

            elif event.ui_element == self.save_button:
                pass

            elif event.ui_element == self.start_button:
                if self.start_button.text == "Start":
                    self.start_button.set_text("Stop")
                    self.iface.env_win.env_thread.start()
                else:
                    self.start_button.set_text("Start")
                    self.iface.env_win.env.running = False
                    self.iface.env_win.env_thread = Thread(target=self.iface.env_win.env.run)

        elif event.user_type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
            self.iface.env_win.env.target_freq = (
                1
                + ((self.iface.env_win.env.iter_freq - 1) / 100)
                * event.value)


class MessageWin(pygame_gui.elements.ui_window.UIWindow):
    def __init__(self, iface):
        self.size = (iface.win_size[0] / 3, 150)
        self.pos = (0, iface.win_size[1] - self.size[1])
        super().__init__(
            rect=pygame.Rect(self.pos, self.size),
            window_display_title="Messages",
            object_id="messages_win",
            manager=iface.manager)
        # TODO finish message window


class DisplayWin(pygame_gui.elements.ui_window.UIWindow):
    # Parent class of windows that display a dinamically changing surface
    # Not meant to be instantiated on its own
    def __init__(self, size, pos, surface_size, iface, title):
        self.iface = iface
        self.size = size
        self.pos = pos

        # Initialize window gui element
        super().__init__(
            rect=pygame.Rect(self.pos, self.size),
            window_display_title=title,
            manager=iface.manager,
            resizable=True)

        # display surface size
        self.container_size = surface_size
        self.surface_size = self.container_size

        # create a surface and stretch it into the window
        self.surface = pygame.Surface(self.surface_size)
        self.scaled_surface = None
        self.display = pygame_gui.elements.ui_image.UIImage(
            relative_rect=pygame.Rect((0, 0), (self.get_container().get_size())),
            image_surface=self.surface,
            manager=iface.manager,
            container=self,
            anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'bottom'})

        # TODO add header buttons

    def render(self):
        # placeholder to be overriden by child classes
        pass

    def update(self, delta):
        super().update(delta)

        # Render displayed image onto surface
        self.render()

        # Get container dims and stretch the display surface into it, but keeping aspect ratio
        self.container_size = self.get_container().get_size()
        cont_ratio = self.container_size[0] / self.container_size[1]
        surf_ratio = self.surface_size[0] / self.surface_size[1]
        if cont_ratio < surf_ratio:
            self.surface_size = (self.container_size[0], int(self.container_size[0] / surf_ratio))
        elif cont_ratio > surf_ratio:
            self.surface_size = (int(self.container_size[1] * surf_ratio), self.container_size[1])
        else:
            self.surface_size = self.container_size

        self.scaled_surface = pygame.transform.smoothscale(self.surface, self.surface_size)
        self.display.set_image(self.scaled_surface)


class EnvWin(DisplayWin):
    def __init__(self, iface):
        self.iface = iface
        # Create environment model object  # TODO add ability to load one from memory
        self.env = Environment()
        self.env_thread = Thread(target=self.env.run)

        self.selected_agent = None

        # Define size and position in relation to other windows and as function of env size
        sizeY = iface.win_size[1] - iface.env_control_win.size[1] - iface.message_win.size[1]
        sizeX = int(sizeY * (self.env.size[0] / self.env.size[1])) - 53
        self.size = (sizeX, sizeY)
        self.pos = (0, iface.env_control_win.size[1])

        # Initialize display window (parent class)
        super().__init__(self.size, self.pos, self.env.size, iface, "Environment")

    def render(self):
        # reset window to background color
        self.surface.fill((32, 38, 36))

        # Draw Agents
        for a in self.env.agents:
            pygame.draw.circle(self.surface, a.color, a.pos, a.radius)
            # triangle
            A = pol2cart(7, a.angle) + a.pos
            B = pol2cart(7, a.angle + radians(150)) + a.pos
            C = pol2cart(7, a.angle + radians(210)) + a.pos
            pygame.draw.polygon(self.surface, "black", (A, B, C))

            # highlight if agent selected
            if self.selected_agent == a.id:
                pygame.draw.circle(self.surface, "yellow", a.pos, a.radius + 3, 1)

    def kill(self):
        # TODO ask if save
        self.iface.env_win.env.running = False
        self.iface.env_win = None
        self.iface.env_control_win.start_button.set_text("Start")
        super().kill()


class AgentWin(pygame_gui.elements.ui_window.UIWindow):
    def __init__(self, iface, id):
        self.iface = iface
        self.agent = iface.env_win.env.agents[id]
        self.size = (
            iface.env_win.size[0] - iface.env_control_win.size[0],
            iface.env_control_win.size[1])
        self.pos = (iface.env_control_win.size[0], 0)
        super().__init__(
            rect=pygame.Rect(self.pos, self.size),
            manager=iface.manager,
            window_display_title="Agent id: " + str(id))

        # Gui elements
        self.show_button = pygame_gui.elements.ui_button.UIButton(
            relative_rect=pygame.Rect(
                (iface.padding, iface.padding),
                (iface.button_width, iface.button_height)),
            text="Show",
            manager=iface.manager,
            container=self)

        self.save_button = pygame_gui.elements.ui_button.UIButton(
            relative_rect=pygame.Rect(
                (iface.button_width + 2 * iface.padding, iface.padding),
                (iface.button_width, iface.button_height)),
            text="Save",
            manager=iface.manager,
            container=self)


class NetWin(DisplayWin):
    surface_size = (500, 500)

    def __init__(self, iface, agent):
        self.iface = iface
        self.pos = (iface.env_control_win.size[0] + iface.agent_win.size[0],
                    iface.env_control_win.size[1])
        self.size = (iface.env_win.size[1] - 24, iface.env_win.size[1])
        super().__init__(self.size, self.pos, NetWin.surface_size, iface, "Network")

        self.agent = agent
        self.embedding = Embedding(agent.network, self.surface)

    def kill(self):
        self.iface.net_win = None
        super().kill()

    def render(self):
        self.surface = self.embedding.surface


class StatsWin(pygame_gui.elements.ui_window.UIWindow):
    def __init__(self, iface):
        self.iface = iface
        self.pos = (iface.message_win.size[0],
                    iface.win_size[1] - iface.message_win.size[1])
        self.size = (iface.win_size[0] / 3, iface.message_win.size[1])
        super().__init__(
            rect=pygame.Rect(self.pos, self.size),
            manager=iface.manager,
            window_display_title="Stats")


class CommandWin(pygame_gui.elements.ui_window.UIWindow):
    def __init__(self, iface):
        self.iface = iface
        self.pos = (iface.message_win.size[0] + iface.stats_win.size[0],
                    iface.win_size[1] - iface.message_win.size[1])
        self.size = (iface.win_size[0] / 3,
                     iface.message_win.size[1])
        super().__init__(
            rect=pygame.Rect(self.pos, self.size),
            manager=iface.manager,
            window_display_title="Command Prompt")

        # Gui elements
        self.text_entry = pygame_gui.elements.ui_text_entry_line.UITextEntryLine(
            relative_rect=pygame.Rect(
                (0, 1 - iface.button_height),
                (self.get_container().get_size()[0], iface.button_height)),
            manager=iface.manager,
            container=self,
            anchors={"left": "left",
                     "right": "left",
                     "top": "bottom",
                     "bottom": "bottom"})

    def enter(self):
        entry = self.text_entry.get_text()
        if entry == "": return
        self.text_entry.set_text("")
        if entry == "t":
            # t sets up the app for testing the current thing im testing
            self.iface.env_win = EnvWin(self.iface)
            self.iface.env_win.selected_agent = 1
            self.iface.agent_win = AgentWin(self.iface, self.iface.env_win.selected_agent)
            self.iface.net_win = NetWin(self.iface, self.iface.agent_win.agent)
