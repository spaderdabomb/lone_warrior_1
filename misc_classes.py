from __future__ import annotations

import arcade
import numpy as np

from globals import *
from load_sprites import SpriteCache

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from player import Player


class DamageLabel:

    def __init__(self, hp: int, parent):
        super().__init__()

        self.hp = hp
        self.parent = parent
        self.text_sprite = None

        self.center_x = self.parent.hp_container.center_x
        self.center_y = self.parent.hp_container.center_y + 20*RESOLUTION_SCALING
        self.change_x = 0
        self.change_y = 1
        self.text_size = DAMAGE_LABEL_TEXT_SIZE

        self.damaged_text = None
        self.damaged_color = (255, 255, 255, 255)

        self.frame_stamp_list = [5, 10, 20, 50]
        self.frames_elapsed = 0
        self.animation_complete = False

        self.setup()

    def setup(self):
        if self.hp == 0:
            self.damaged_color = (100, 122, 237, 255)
            self.damaged_text = str(self.hp)
        else:
            self.damaged_color = (228, 52, 52, 255)
            self.damaged_text = '-' + str(self.hp)

    def change_color(self):
        current_color = self.damaged_color
        new_color = (current_color[0], current_color[1], current_color[2], current_color[3] - 8)
        self.damaged_color = new_color

    def update(self):
        if self.frames_elapsed < self.frame_stamp_list[0]:
            self.text_size += 1
            self.change_y = 1
        elif self.frames_elapsed < self.frame_stamp_list[1]:
            self.text_size -= 1
            self.change_y = 1
        elif self.frames_elapsed < self.frame_stamp_list[2]:
            self.change_y = 1
            self.text_size = DAMAGE_LABEL_TEXT_SIZE
        elif self.frames_elapsed < self.frame_stamp_list[3]:
            self.change_y = 1
            self.change_color()
        else:
            self.animation_complete = True

        self.center_x += self.change_x
        self.center_y += self.change_y
        self.frames_elapsed += 1

    def draw(self):
        arcade.draw_text(self.damaged_text, self.center_x, self.center_y, self.damaged_color,
                                            align="center", anchor_x="center", anchor_y="center",
                                            bold=True, font_size=self.text_size)


class LevelUpLabel(arcade.Sprite):

    def __init__(self, file_name: str, scale: float):
        super().__init__(file_name, scale, calculate_hit_box=False)
        self.setup()

    def setup(self):
        self.change_y = 2
        self.change_x = 0
        self.center_x = SCREEN_WIDTH / 2
        self.center_y = (1080-261)*RESOLUTION_SCALING

    def update(self):
        self.center_y += self.change_y

        if self.alpha > 5:
            self.alpha -= 4
        else:
            self.remove_from_sprite_lists()


class LevelUpAnimation(arcade.Sprite):

    def __init__(self, file_name: str, scale: float, player_inst: Player):
        super().__init__(file_name, scale, calculate_hit_box=False)

        self.player = player_inst

        self.current_texture = 0
        self.frame_count = 0

        self.frames_before_next_animation = 3
        self.frames_til_opacity_lowering = 30

        self.setup()

    def setup(self):
        self.center_x = self.player.center_x
        self.center_y = self.player.center_y + 50
        self.alpha = 150

    def update(self):
        self.center_x = self.player.center_x
        self.center_y = self.player.center_y + 50

        if self.frame_count > self.frames_til_opacity_lowering:
            if self.alpha >= 4:
                self.alpha -= 3
            else:
                self.remove_from_sprite_lists()

        self.update_animation()

    def draw(self):
        pass

    def update_animation(self, delta_time: float = 1/60):
        self.frame_count += 1
        if self.frame_count % self.frames_before_next_animation == 0:
            self.current_texture += 1

        if self.current_texture >= len(SpriteCache.LEVEL_UP_ANIMATION):
            self.current_texture = 0
        self.texture = SpriteCache.LEVEL_UP_ANIMATION[self.current_texture]


class NextStageArrow(arcade.Sprite):

    def __init__(self, file_name: str, scale: float):
        super().__init__(file_name, scale, calculate_hit_box=False)
        self.setup()

    def setup(self):
        self.right_boundary = 1829*RESOLUTION_SCALING
        self.left_boundary = 1785*RESOLUTION_SCALING

        self.change_x = 1.5
        self.change_y = 0
        self.center_x = self.left_boundary
        self.center_y = (1080 - 578)*RESOLUTION_SCALING
        self.alpha = math.ceil(0.75*255)

    def update(self):
        if self.center_x <= self.left_boundary:
            self.change_x = 1.5
        elif self.center_x >= self.right_boundary:
            self.change_x = -1.5

        self.center_x += self.change_x
        self.center_y += self.change_y

    def draw(self):
        pass


class Shuriken(arcade.Sprite):

    def __init__(self, file_name: str, scale: float, player_inst: Player):
        super().__init__(file_name, scale, calculate_hit_box=False)

        self.player = player_inst
        self.player_sign = (int(self.player.facing_right)*2) - 1

        self.current_texture = 0
        self.frame_count = 0
        self.frames_before_next_animation = 3

        self.animation = SpriteCache.SHURIKEN_ANIMATION

        self.setup()

    def setup(self):
        self.change_x = 30*self.player_sign
        self.change_y = 0

    def update(self):
        self.frame_count += 1
        self.change_x += np.sign(self.player.center_x - self.center_x)*0.5*(1 + self.frame_count/60)
        self.change_y += np.sign(self.player.center_y - self.center_y)*0.5*(1 + self.frame_count/60)

        if np.abs(self.change_x) > 40:
            self.change_x = np.sign(self.change_x)*40
        if np.abs(self.change_y) > 40:
            self.change_y = np.sign(self.change_y)*40

        self.center_x += self.change_x
        self.center_y += self.change_y

        if arcade.get_distance_between_sprites(self, self.player) < self.player.width and self.frame_count > 20:
            self.remove_from_sprite_lists()

    def update_animation(self, delta_time: float = 1/60):
        # Update frame and current texture
        self.frame_count += 1
        if self.frame_count % self.frames_before_next_animation == 0:
            self.current_texture += 1

        if self.current_texture >= len(SpriteCache.SHURIKEN_ANIMATION):
            self.current_texture = 0
        self.texture = SpriteCache.SHURIKEN_ANIMATION[self.current_texture]