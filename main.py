import arcade
import multiprocessing

import time

from game_data import GameData
from globals import *
from Views import menu_views
from load_sprites import SpriteCache
from sound_manager import SoundManager


# class LoadSpritesProcess(multiprocessing.Process):
#
#     def __init__(self, class_variable):
#         multiprocessing.Process.__init__(self)
#         self.class_variable = class_variable
#
#     def run(self):
#         SpriteCache.load_all(self.class_variable)
#
# class MainProcess(multiprocessing.Process):
#
#     def __init__(self, class_variable):
#         multiprocessing.Process.__init__(self)
#         self.class_variable = class_variable
#
#     def run(self):
#         GameData(SCREEN_TITLE)
#         window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
#         sound_manager = SoundManager(window)
#         loading_view = menu_views.LoadingMenuView(window, sound_manager, self.class_variable)
#         window.show_view(loading_view)
#         arcade.run()

# if __name__ == "__main__":
#     ClassVariable = multiprocessing.Value('i', 0)
#
#     process_list = []
#     p1 = LoadSpritesProcess(ClassVariable)
#     process_list.append(p1)
#     p1.start()  # Output: 0 1
#     p2 = MainProcess(ClassVariable)
#     process_list.append(p2)
#     p2.start()  # Output: 1 1
#
#     for p in process_list:
#         p.join()

def main():
    GameData(SCREEN_TITLE)
    # SpriteCache()
    GameData.data['player_level'] = 1
    GameData.data['player_xp'] = 0
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    sound_manager = SoundManager(window)
    loading_view = menu_views.LoadingMenuView(window, sound_manager)
    window.show_view(loading_view)
    arcade.run()

if __name__ == "__main__":
    main()

