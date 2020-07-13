import os
import arcade
import arcade.gui
import time

from globals import *
from Utils.core import CounterClass


class SpriteCache():

    # Spritesheets
    PLAYER_IDLE_RIGHT_ANIMATION = None
    PLAYER_IDLE_LEFT_ANIMATION = None
    PLAYER_WALK_RIGHT_ANIMATION = None
    PLAYER_WALK_LEFT_ANIMATION = None

    ENEMY_SLIME_IDLE_LEFT_ANIMATION = None
    ENEMY_SLIME_IDLE_RIGHT_ANIMATION = None
    ENEMY_SLIME_ATTACK_LEFT_ANIMATION = None
    ENEMY_SLIME_ATTACK_RIGHT_ANIMATION = None
    ENEMY_SLIME_DEATH_LEFT_ANIMATION = None
    ENEMY_SLIME_DEATH_RIGHT_ANIMATION = None

    LEVEL_UP_ANIMATION = None

    SHURIKEN_ANIMATION = None

    # UI
    SETTINGS_BUTTON = None
    ACHIEVEMENTS_BUTTON = None
    HIGHSCORES_BUTTON = None
    START_BUTTON = None
    PLAY_BUTTON = None
    BACK_SETTINGS = None

    # Loading feedbakc
    FILE_INDEX = 0

    @staticmethod
    def __init__():

        a = time.time()
        SpriteCache._load_spritesheets()
        print('Spritesheet loading time:', time.time() - a)

        a = time.time()
        SpriteCache._load_textures()
        print('Textures loading time:', time.time() - a)

        a = time.time()
        SpriteCache._load_ui()
        print('UI loading time:', time.time() - a)

    @staticmethod
    def _load_spritesheets():
        index = CounterClass()

        paths = [os.path.join(SPRITESHEETS_PATH, "main_character_idle_right_animation.png"),
                 os.path.join(SPRITESHEETS_PATH, "main_character_idle_left_animation.png"),
                 os.path.join(SPRITESHEETS_PATH, "main_character_walk_right_animation.png"),
                 os.path.join(SPRITESHEETS_PATH, "main_character_walk_left_animation.png"),
                 os.path.join(SPRITESHEETS_PATH, "slime_idle_right_animation.png"),
                 os.path.join(SPRITESHEETS_PATH, "slime_idle_left_animation.png"),
                 os.path.join(SPRITESHEETS_PATH, "slime_attack_right_animation.png"),
                 os.path.join(SPRITESHEETS_PATH, "slime_attack_left_animation.png"),
                 os.path.join(SPRITESHEETS_PATH, "slime_death_right_animation.png"),
                 os.path.join(SPRITESHEETS_PATH, "slime_death_left_animation.png"),
                 os.path.join(SPRITESHEETS_PATH, "level_up_animation.png"),
                 os.path.join(SPRITESHEETS_PATH, "shuriken_animation.png")
                 ]

        SpriteCache.PLAYER_IDLE_RIGHT_ANIMATION = arcade.load_spritesheet(paths[index.counter], 410, 550, 17, 17)
        SpriteCache.PLAYER_IDLE_LEFT_ANIMATION = arcade.load_spritesheet(paths[index.increase_counter()], 410, 550, 17, 17)
        SpriteCache.PLAYER_WALK_RIGHT_ANIMATION = arcade.load_spritesheet(paths[index.increase_counter()], 410, 550, 13, 13)
        SpriteCache.PLAYER_WALK_LEFT_ANIMATION = arcade.load_spritesheet(paths[index.increase_counter()], 410, 550, 13, 13)

        SpriteCache.ENEMY_SLIME_IDLE_RIGHT_ANIMATION = arcade.load_spritesheet(paths[index.increase_counter()], 117, 82, 11, 11)
        SpriteCache.ENEMY_SLIME_IDLE_LEFT_ANIMATION = arcade.load_spritesheet(paths[index.increase_counter()], 117, 82, 11, 11)
        SpriteCache.ENEMY_SLIME_ATTACK_RIGHT_ANIMATION = arcade.load_spritesheet(paths[index.increase_counter()], 118, 82, 8, 8)
        SpriteCache.ENEMY_SLIME_ATTACK_LEFT_ANIMATION = arcade.load_spritesheet(paths[index.increase_counter()], 118, 82, 8, 8)
        SpriteCache.ENEMY_SLIME_DEATH_RIGHT_ANIMATION = arcade.load_spritesheet(paths[index.increase_counter()], 118, 82, 8, 8)
        SpriteCache.ENEMY_SLIME_DEATH_LEFT_ANIMATION = arcade.load_spritesheet(paths[index.increase_counter()], 118, 82, 8, 8)

        SpriteCache.LEVEL_UP_ANIMATION = arcade.load_spritesheet(paths[index.increase_counter()], 610, 710, 2, 2)

        SpriteCache.SHURIKEN_ANIMATION = arcade.load_spritesheet(paths[index.increase_counter()], 160, 160, 3, 3)

    @staticmethod
    def _load_textures():
        for filename in os.listdir(SPRITES_PATH):
            if filename.endswith(".png"):
                cache_sprite = arcade.Sprite(os.path.join(SPRITES_PATH, filename), RESOLUTION_SCALING, calculate_hit_box=False)
                SpriteCache.FILE_INDEX += 1

    @staticmethod
    def _load_ui():
        x = SCREEN_WIDTH/2
        y = (1080 - 232)*RESOLUTION_SCALING
        width = 388*RESOLUTION_SCALING
        height = 177*RESOLUTION_SCALING
        spacing = 185*RESOLUTION_SCALING

        SpriteCache.SETTINGS_BUTTON = arcade.gui.UIImageButton(
            center_x=x,
            center_y=y,
            normal_texture=arcade.load_texture(os.path.join(SPRITES_PATH, 'button_settings_normal.png')),
            hover_texture=arcade.load_texture(os.path.join(SPRITES_PATH, 'button_settings_hover.png')),
            press_texture=arcade.load_texture(os.path.join(SPRITES_PATH, 'button_settings_clicked.png')),
            text=' ',
            id='settings_button'
        )

        SpriteCache.ACHIEVEMENTS_BUTTON = arcade.gui.UIImageButton(
            center_x=x,
            center_y=y - spacing,
            normal_texture=arcade.load_texture(os.path.join(SPRITES_PATH, 'button_achievements_normal.png')),
            hover_texture=arcade.load_texture(os.path.join(SPRITES_PATH, 'button_achievements_hover.png')),
            press_texture=arcade.load_texture(os.path.join(SPRITES_PATH, 'button_achievements_clicked.png')),
            text=' ',
            id='achievements_button'
        )

        SpriteCache.HIGHSCORES_BUTTON = arcade.gui.UIImageButton(
            center_x=x,
            center_y=y - spacing*2,
            normal_texture=arcade.load_texture(os.path.join(SPRITES_PATH, 'button_highscores_normal.png')),
            hover_texture=arcade.load_texture(os.path.join(SPRITES_PATH, 'button_highscores_hover.png')),
            press_texture=arcade.load_texture(os.path.join(SPRITES_PATH, 'button_highscores_clicked.png')),
            text=' ',
            id='highscores_button'
        )

        y = (1080 - 876)*RESOLUTION_SCALING
        SpriteCache.START_BUTTON = arcade.gui.UIImageButton(
            center_x=x,
            center_y=y,
            normal_texture=arcade.load_texture(os.path.join(SPRITES_PATH, 'button_start_normal.png')),
            hover_texture=arcade.load_texture(os.path.join(SPRITES_PATH, 'button_start_hover.png')),
            press_texture=arcade.load_texture(os.path.join(SPRITES_PATH, 'button_start_clicked.png')),
            text=' ',
            id='start_button'
        )

        x = SCREEN_WIDTH/2
        y = (1080 - 854)*RESOLUTION_SCALING
        width = 388*RESOLUTION_SCALING
        height = 177*RESOLUTION_SCALING

        SpriteCache.PLAY_BUTTON = arcade.gui.UIImageButton(
            center_x=x,
            center_y=y,
            normal_texture=arcade.load_texture(os.path.join(SPRITES_PATH, 'button_play_normal.png')),
            hover_texture=arcade.load_texture(os.path.join(SPRITES_PATH, 'button_play_hover.png')),
            press_texture=arcade.load_texture(os.path.join(SPRITES_PATH, 'button_play_clicked.png')),
            text=' ',
            id='play_button'
        )

        x = SCREEN_WIDTH/2
        y = (1080 - 940)*RESOLUTION_SCALING

        SpriteCache.BACK_SETTINGS = arcade.gui.UIImageButton(
            center_x=x,
            center_y=y,
            normal_texture=arcade.load_texture(os.path.join(SPRITES_PATH, 'button_back_normal.png')),
            hover_texture=arcade.load_texture(os.path.join(SPRITES_PATH, 'button_back_hover.png')),
            press_texture=arcade.load_texture(os.path.join(SPRITES_PATH, 'button_back_clicked.png')),
            text=' ',
            id='back_button'
        )

        SpriteCache.FILE_INDEX = 100