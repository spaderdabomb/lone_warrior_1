from __future__ import annotations

import arcade
import os
import time
import numpy as np

from globals import *
from load_sprites import SpriteCache
from game_data import GameData
from misc_classes import DamageLabel, Shuriken

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from Views.game_scene import GameSceneView


class Player(arcade.Sprite):

    def __init__(self, file_name: str, scale: float, game_view: GameSceneView):
        super().__init__(file_name, scale, calculate_hit_box=False)

        self.game_view = game_view

        self.setup_bool = True
        self.change_y = 0

        self.current_level = GameData.data['player_level']
        self.current_xp = GameData.data['player_xp']
        self.max_hp = math.ceil((self.current_level + 9)*1.05**(self.current_level - 1))
        self.current_hp = self.max_hp
        self.max_damage = 1 + (self.current_level - 1)
        self.attack_speed = 0.5 + (1.5*self.current_level/100)
        self.defense_level = self.current_level
        self.attack_level = self.current_level

        self.jump_velocity = 28
        self.movement_speed = 6
        self.can_attack = False
        self.attack_hit = False
        self.time_since_damaged = 99999
        self.frames_between_attack = FRAME_RATE / self.attack_speed
        self.frames_since_attack = 0

        self.current_texture = 0
        self.frame_count = 0
        self.frames_before_next_animation = 3

        # 0 - idle right
        # 1 - idle left
        self.animation_index = 0
        self.animation_list = []
        self.facing_right = True

        self.setup()

    def setup(self):
        self.player_hitbox = [[-self.width, 1.75*self.height], [self.width, 1.75*self.height],
                             [self.width, -1.75*self.height], [-self.width, -1.75*self.height]]
        self.set_hit_box(self.player_hitbox)

        self.hp_container = arcade.Sprite(os.path.join(SPRITES_PATH, 'XP_container_small.png'), 0.5, calculate_hit_box=False)
        self.hp_container.center_x = self.center_x
        self.hp_container.center_y = self.center_y + self.height*3/4
        self.hp_color = (228, 52, 52)

        self.damaged_label_list = []
        self.shuriken_sprite_list = arcade.SpriteList()

        self.animation_list.extend([SpriteCache.PLAYER_IDLE_RIGHT_ANIMATION, SpriteCache.PLAYER_IDLE_LEFT_ANIMATION,
                                    SpriteCache.PLAYER_WALK_RIGHT_ANIMATION, SpriteCache.PLAYER_WALK_LEFT_ANIMATION])

    def update(self):
        # Setup textures
        if self.setup:
            for texture_list in self.animation_list:
                for texture in texture_list:
                    self.texture = texture
            self.setup_bool = False

        # Handle screen boundaries
        self.center_x += self.change_x
        if self.left < SCREEN_BORDER_PADDING:
            self.left = SCREEN_BORDER_PADDING
        elif self.right > SCREEN_WIDTH - SCREEN_BORDER_PADDING:
            self.right = SCREEN_WIDTH - SCREEN_BORDER_PADDING

        # Game scene updates
        if self.game_view.game_scene:
            self.game_scene_updates()

        self.time_since_damaged += 1.0 / FRAME_RATE
        self.frames_since_attack += 1

    def game_scene_updates(self):
        # Updates to sprite lists
        self.shuriken_sprite_list.update()

        # Handle HP
        self.hp_container.center_x = self.center_x
        self.hp_container.center_y = self.center_y + self.height*2/3
        if self.current_hp/self.max_hp < 0.25:
            self.hp_color = [182, 1, 1]
        else:
            self.hp_color = [228, 52, 52]

        # Handle auto-attack
        enemy_to_attack = None
        collision_list = arcade.check_for_collision_with_list(self, self.game_view.current_level.enemy_spritelist)
        if len(collision_list) >= 1:
            enemy_to_attack = collision_list[0]
            self.can_attack = True
        else:
            self.can_attack = False
        if enemy_to_attack is not None:
            if (self.can_attack) and (self.frames_since_attack > self.frames_between_attack) and (enemy_to_attack.dead is False):
                self.attack(enemy_to_attack)
                self.frames_since_attack = 0

        # Handle shuriken attack
        for shuriken in self.shuriken_sprite_list:
            shuriken_collisions = arcade.check_for_collision_with_list(shuriken, self.game_view.current_level.enemy_spritelist)
            for collision in shuriken_collisions:
                print('colliding')

        # Labels
        for damaged_label_object in self.damaged_label_list:
            damaged_label_object.update()
            if damaged_label_object.animation_complete:
                self.damaged_label_list.remove(damaged_label_object)

    def on_draw(self):
        # Sprite lists
        self.shuriken_sprite_list.draw()

        if self.time_since_damaged < TIME_TO_HP_BAR_DISAPPEAR:
            if self.current_hp == 0:
                width = 0
            else:
                width = self.hp_container.width*self.current_hp/self.max_hp - 3*RESOLUTION_SCALING
            height = self.hp_container.height - 3*RESOLUTION_SCALING
            x = self.hp_container.center_x - self.hp_container.width/2 + width/2 + 2*RESOLUTION_SCALING
            y = self.hp_container.center_y
            arcade.draw_rectangle_filled(x, y, width, height, self.hp_color)

            self.hp_container.draw()

        for damage_label in self.damaged_label_list:
            damage_label.draw()

    def update_animation(self, delta_time: float = 1 / 60):
        # Updates to sprite list
        for shuriken in self.shuriken_sprite_list:
            shuriken.update_animation()

        # Change animation index
        if self.change_x > 0:
            self.animation_index = 2
            self.facing_right = True
        elif self.change_x < 0:
            self.animation_index = 3
            self.facing_right = False
        elif self.change_x == 0:
            if self.facing_right:
                self.animation_index = 0
            else:
                self.animation_index = 1

        # Update frame and current texture
        self.frame_count += 1
        if self.frame_count % self.frames_before_next_animation == 0:
            self.current_texture += 1

        # Set animations
        self.handle_new_animation(self.animation_index)

        # Set values based on specific animation
        pass

    def handle_new_animation(self, index: int):
        texture_list = self.animation_list[index]
        if self.current_texture >= len(texture_list):
            self.current_texture = 0
        self.texture = texture_list[self.current_texture]

    def handle_jump(self):
        self.change_y = self.jump_velocity

    def damaged(self, hp: int):
        self.current_hp -= hp
        self.time_since_damaged = 0
        damage_label = DamageLabel(hp, self)
        self.damaged_label_list.append(damage_label)

    def attack(self, enemy):
        chance_to_hit = (1.0 / (1.0 + (enemy.defense_level/self.attack_level)))
        chance_to_hit_int = int(chance_to_hit*1000)
        rand_num = np.random.randint(0, 1000)
        if rand_num < chance_to_hit_int:
            self.attack_hit = True
        else:
            self.attack_hit = False

        if self.attack_hit:
            self.game_view.damage_enemy(enemy, self.max_damage)
        else:
            self.game_view.damage_enemy(enemy, 0)

    def attack_shuriken(self):
        shuriken = Shuriken(os.path.join(SPRITES_PATH, 'shuriken.png'), 0.30, self)
        shuriken.center_x = self.center_x
        shuriken.center_y = self.center_y
        self.shuriken_sprite_list.append(shuriken)

    def increase_xp(self, xp: int):
        leveled_up_bool = True
        self.current_xp += xp
        while leveled_up_bool:
            if self.current_xp >= XP_TO_NEXT_LEVEL_LIST[self.current_level - 1]:
                self.current_xp -= XP_TO_NEXT_LEVEL_LIST[self.current_level - 1]
                self.current_level += 1
                self.max_hp = math.ceil((self.current_level + 9) * 1.05 ** (self.current_level - 1))
                self.current_hp = self.max_hp
                self.max_damage = 1 + (self.current_level - 1)
                self.attack_speed = 0.5 + (1.5 * self.current_level / 100)
                self.defense_level = self.current_level
                self.attack_level = self.current_level
                self.game_view.player_level_up()
            else:
                leveled_up_bool = False

        GameData.data['player_level'] = self.current_level
        GameData.data['player_xp'] = self.current_xp
        GameData.save_data()