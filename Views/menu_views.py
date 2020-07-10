from __future__ import annotations

import arcade
import arcade.gui
import os
import time
import asyncio
import sys
import itertools
import threading

from globals import *
from load_sprites import SpriteCache
from sound_manager import SoundManager
from Views.level_select import LevelSelectView

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    pass


class MainMenuView(arcade.View):
    def __init__(self, window: arcade.Window, sound_manager: SoundManager):
        super().__init__()

        self.window = window
        self.sound_manager = sound_manager
        self.ui_manager = arcade.gui.UIManager(window)
        self.ui_manager.push_handlers(self.on_ui_event)

        self.setup()

    def setup(self):
        self.ui_manager.purge_ui_elements()

        # Setup background UI
        arcade.set_background_color(arcade.color.WHITE)
        self.main_menu_background = arcade.Sprite(os.path.join(SPRITES_PATH, 'menu_main.png'), calculate_hit_box=False)

        self.main_menu_background.center_x = SCREEN_WIDTH/2
        self.main_menu_background.center_y = SCREEN_HEIGHT/2

        # Setup buttons
        self.play_button = self.ui_manager.add_ui_element(SpriteCache.PLAY_BUTTON)

    def on_ui_event(self, event: arcade.gui.UIEvent):
        if event.type == arcade.gui.UIClickable.CLICKED and event.get('ui_element').id == 'play_button':
            self.sound_manager.play_sound(0)
            self.ui_manager.purge_ui_elements()
            start_menu_view = StartMenuView(self.window, self.sound_manager, self.ui_manager)
            self.window.show_view(start_menu_view)

    def on_draw(self):
        arcade.start_render()
        self.main_menu_background.draw()

    def on_update(self, dt):
        self.sound_manager.update()


class SettingsMenuView(arcade.View):
    def __init__(self, window: arcade.Window, sound_manager: SoundManager):
        super().__init__()

        self.window = window
        self.sound_manager = sound_manager
        self.ui_manager = arcade.gui.UIManager(window)
        self.ui_manager.push_handlers(self.on_ui_event)

        self.setup()

    def setup(self):
        self.ui_manager.purge_ui_elements()

        # Setup background UI
        arcade.set_background_color(arcade.color.WHITE)
        self.settings_menu_background = arcade.Sprite(os.path.join(SPRITES_PATH, 'menu_settings.png'), calculate_hit_box=False)
        self.settings_menu_background.center_x = SCREEN_WIDTH/2
        self.settings_menu_background.center_y = SCREEN_HEIGHT/2

        # Setup buttons
        self.back_button = self.ui_manager.add_ui_element(SpriteCache.BACK_SETTINGS)

    def on_ui_event(self, event: arcade.gui.UIEvent):
        if event.type == arcade.gui.UIClickable.CLICKED and event.get('ui_element').id == 'back_button':
            self.sound_manager.play_sound(0)
            self.ui_manager.purge_ui_elements()
            start_menu_view = StartMenuView(self.window, self.sound_manager, self.ui_manager)
            self.window.show_view(start_menu_view)

    def on_draw(self):
        arcade.start_render()
        self.settings_menu_background.draw()

    def on_update(self, dt):
        self.sound_manager.update()


class AchievementsMenuView(arcade.View):
    def __init__(self, window: arcade.Window, sound_manager: SoundManager):
        super().__init__()

        self.window = window
        self.sound_manager = sound_manager
        self.ui_manager = arcade.gui.UIManager(window)
        self.ui_manager.push_handlers(self.on_ui_event)

        self.setup()

    def setup(self):
        self.ui_manager.purge_ui_elements()

        # Setup background UI
        arcade.set_background_color(arcade.color.WHITE)
        self.achievements_menu_background = arcade.Sprite(os.path.join(SPRITES_PATH, 'menu_achievements.png'), calculate_hit_box=False)
        self.achievements_menu_background.center_x = SCREEN_WIDTH / 2
        self.achievements_menu_background.center_y = SCREEN_HEIGHT / 2

        # Setup buttons
        self.back_button = self.ui_manager.add_ui_element(SpriteCache.BACK_SETTINGS)

    def on_ui_event(self, event: arcade.gui.UIEvent):
        if event.type == arcade.gui.UIClickable.CLICKED and event.get('ui_element').id == 'back_button':
            self.sound_manager.play_sound(0)
            self.ui_manager.purge_ui_elements()
            start_menu_view = StartMenuView(self.window, self.sound_manager, self.ui_manager)
            self.window.show_view(start_menu_view)

    def on_draw(self):
        arcade.start_render()
        self.achievements_menu_background.draw()

    def on_update(self, dt):
        self.sound_manager.update()


class HighscoresMenuView(arcade.View):
    def __init__(self, window: arcade.Window, sound_manager: SoundManager):
        super().__init__()

        self.window = window
        self.sound_manager = sound_manager
        self.ui_manager = arcade.gui.UIManager(window)
        self.ui_manager.push_handlers(self.on_ui_event)

        self.setup()

    def setup(self):
        self.ui_manager.purge_ui_elements()

        # Setup background UI
        arcade.set_background_color(arcade.color.WHITE)
        self.highscores_menu_background = arcade.Sprite(os.path.join(SPRITES_PATH, 'menu_highscores.png'), calculate_hit_box=False)
        self.highscores_menu_background.center_x = SCREEN_WIDTH/2
        self.highscores_menu_background.center_y = SCREEN_HEIGHT/2

        # Setup buttons
        self.back_button = self.ui_manager.add_ui_element(SpriteCache.BACK_SETTINGS)

    def on_ui_event(self, event: arcade.gui.UIEvent):
        if event.type == arcade.gui.UIClickable.CLICKED and event.get('ui_element').id == 'back_button':
            self.sound_manager.play_sound(0)
            self.ui_manager.purge_ui_elements()
            start_menu_view = StartMenuView(self.window, self.sound_manager, self.ui_manager)
            self.window.show_view(start_menu_view)

    def on_draw(self):
        arcade.start_render()
        self.highscores_menu_background.draw()

    def on_update(self, dt):
        self.sound_manager.update()

class StartMenuView(arcade.View):
    def __init__(self, window: arcade.Window, sound_manager: SoundManager, ui_manager: arcade.gui.UIManager):
        super().__init__()


        self.window = window
        self.sound_manager = sound_manager
        self.ui_manager = ui_manager
        self.ui_manager.push_handlers(self.on_ui_event)

        self.setup()

    def setup(self):
        self.ui_manager.purge_ui_elements()

        # Setup background UI
        arcade.set_background_color(arcade.color.WHITE)
        self.start_menu_background = arcade.Sprite(os.path.join(SPRITES_PATH, 'menu_start.png'), calculate_hit_box=False)
        self.start_menu_background.center_x = SCREEN_WIDTH/2
        self.start_menu_background.center_y = SCREEN_HEIGHT/2

        # Setup buttons
        self.settings_button = self.ui_manager.add_ui_element(SpriteCache.SETTINGS_BUTTON)
        self.achievements_button = self.ui_manager.add_ui_element(SpriteCache.ACHIEVEMENTS_BUTTON)
        self.highscores_button = self.ui_manager.add_ui_element(SpriteCache.HIGHSCORES_BUTTON)
        self.start_button = self.ui_manager.add_ui_element(SpriteCache.START_BUTTON)

    def on_ui_event(self, event: arcade.gui.UIEvent):
        if event.type == arcade.gui.UIClickable.CLICKED and event.get('ui_element').id == 'settings_button':
            self.sound_manager.play_sound(0)
            self.ui_manager.purge_ui_elements()
            settings_menu_view = SettingsMenuView(self.window, self.sound_manager)
            self.window.show_view(settings_menu_view)
        elif event.type == arcade.gui.UIClickable.CLICKED and event.get('ui_element').id == 'achievements_button':
            self.sound_manager.play_sound(0)
            self.ui_manager.purge_ui_elements()
            achievements_menu_view = AchievementsMenuView(self.window, self.sound_manager)
            self.window.show_view(achievements_menu_view)
        elif event.type == arcade.gui.UIClickable.CLICKED and event.get('ui_element').id == 'highscores_button':
            self.sound_manager.play_sound(0)
            self.ui_manager.purge_ui_elements()
            highscores_menu_view = HighscoresMenuView(self.window, self.sound_manager)
            self.window.show_view(highscores_menu_view)
        elif event.type == arcade.gui.UIClickable.CLICKED and event.get('ui_element').id == 'start_button':
            self.sound_manager.play_sound(0)
            self.ui_manager.purge_ui_elements()
            level_select_view = LevelSelectView(self.window, self.sound_manager)
            self.window.show_view(level_select_view)

    def on_draw(self):
        arcade.start_render()
        self.start_menu_background.draw()

    def on_update(self, dt):
        self.sound_manager.update()


class LoadingMenuView(arcade.View):
    def __init__(self, window: arcade.Window, sound_manager: SoundManager):
        super().__init__()

        self.window = window
        self.sound_manager = sound_manager
        self.loading_index = 0

        self.done = False

        self.setup()

    def setup(self):
        # Setup background UI
        arcade.set_background_color(arcade.color.WHITE)
        self.loading_menu_background = arcade.Sprite(os.path.join(SPRITES_PATH, 'menu_loading.png'), calculate_hit_box=False)
        self.loading_menu_background.center_x = SCREEN_WIDTH / 2
        self.loading_menu_background.center_y = SCREEN_HEIGHT / 2

        self.loading_screen_container = arcade.Sprite(os.path.join(SPRITES_PATH, 'loading_screen_container.png'), calculate_hit_box=False)
        self.loading_screen_container.center_x = SCREEN_WIDTH / 2
        self.loading_screen_container.center_y = (1080-598)*RESOLUTION_SCALING
        self.loading_screen_container_color = (45, 221, 99)

        t = threading.Thread(target=self.sprite_cache)
        t.start()

    def on_draw(self):
        arcade.start_render()
        self.loading_menu_background.draw()

        if SpriteCache.FILE_INDEX == 0:
            width = 0
        else:
            width = self.loading_screen_container.width * SpriteCache.FILE_INDEX / 40 - 24 * RESOLUTION_SCALING
        height = self.loading_screen_container.height - 18*RESOLUTION_SCALING
        x = self.loading_screen_container.center_x - self.loading_screen_container.width/2 + width/2 + 6*RESOLUTION_SCALING
        y = self.loading_screen_container.center_y
        arcade.draw_rectangle_filled(x, y, width, height, self.loading_screen_container_color)

        self.loading_screen_container.draw()


    def on_update(self, dt):
        if SpriteCache.FILE_INDEX >= 100:
            menu_view = MainMenuView(self.window, self.sound_manager)
            self.window.show_view(menu_view)

    def sprite_cache(self):
        SpriteCache()






