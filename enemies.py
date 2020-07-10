from __future__ import annotations

import arcade
import os
import time
import numpy as np

from globals import *
from load_sprites import SpriteCache
from misc_classes import DamageLabel

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from Views.game_scene import GameSceneView


def create_enemy(game_view: GameSceneView, index: int, scale: float):
    enemy = None
    if index == 0:
        enemy = EnemySlime(os.path.join(SPRITES_PATH, 'enemy_slime_default.png'), scale, game_view)

    return enemy


class EnemySlime(arcade.Sprite):

    def __init__(self, file_name: str, scale: float, game_view: GameSceneView):
        super().__init__(file_name, scale, calculate_hit_box=False)

        self.game_view = game_view

        self.setup_bool = True
        self.movement_speed = 1

        self.current_texture = 0
        self.frame_count = 0
        self.frames_before_next_animation = 4

        self.max_hp = 5
        self.max_damage = 1
        self.attack_speed = 0.5
        self.defense_level = 0
        self.attack_level = 1
        self.current_hp = self.max_hp

        self.can_attack = False
        self.attack_hit = False
        self.frames_between_attack = FRAME_RATE / self.attack_speed
        self.frames_since_attack = 0
        self.time_since_damaged = 99999
        self.exp_reward = 100

        # 0 - idle right
        # 1 - idle left
        self.animation_index = 1
        self.facing_left = True
        self.attacking = False
        self.dead = False
        self.death_animation_finished = False
        self.ready_to_remove = False

        self.setup()

    def setup(self):
        hit_box_width = 0.5*self.width
        hit_box_height = 0.5*self.height
        self.enemy_hitbox = [[-hit_box_width, hit_box_height], [hit_box_width, hit_box_height],
                             [hit_box_width, -hit_box_height], [-hit_box_width, -hit_box_height]]
        self.set_hit_box(self.enemy_hitbox)

        self.hp_container = arcade.Sprite(os.path.join(SPRITES_PATH, 'XP_container_small.png'), 0.5, calculate_hit_box=False)
        self.hp_container.center_x = self.center_x
        self.hp_container.center_y = self.center_y + self.height*2/3
        self.hp_color = (228, 52, 52)

        self.damaged_label_list = []

    def update(self):
        if not self.dead:
            # Pre-load animations
            if self.setup_bool:
                for i in range(len(SpriteCache.ENEMY_SLIME_IDLE_RIGHT_ANIMATION)):
                    self.texture = SpriteCache.ENEMY_SLIME_IDLE_RIGHT_ANIMATION[i]
                for i in range(len(SpriteCache.ENEMY_SLIME_IDLE_LEFT_ANIMATION)):
                    self.texture = SpriteCache.ENEMY_SLIME_IDLE_LEFT_ANIMATION[i]
                for i in range(len(SpriteCache.ENEMY_SLIME_ATTACK_LEFT_ANIMATION)):
                    self.texture = SpriteCache.ENEMY_SLIME_ATTACK_LEFT_ANIMATION[i]
                for i in range(len(SpriteCache.ENEMY_SLIME_ATTACK_RIGHT_ANIMATION)):
                    self.texture = SpriteCache.ENEMY_SLIME_ATTACK_RIGHT_ANIMATION[i]
                self.setup_bool = False

            # Handle HP
            self.hp_container.center_x = self.center_x
            self.hp_container.center_y = self.center_y + self.height
            if self.current_hp/self.max_hp < 0.25:
                self.hp_color = [182, 1, 1]
            else:
                self.hp_color = [228, 52, 52]

            # Handle attacking and moving
            sign = np.sign(self.game_view.player.center_x - self.center_x)
            self.change_x = sign*self.movement_speed
            if self.change_x > 0:
                self.facing_left = False
            elif self.change_x < 0:
                self.facing_left = True

            # Handle auto-attack
            enemy_to_attack = None
            distance_to_player = arcade.get_distance_between_sprites(self, self.game_view.player)
            distance_to_player_x = np.abs(self.center_x - self.game_view.player.center_x)
            collided = arcade.check_for_collision(self, self.game_view.player)
            if collided:
                self.can_attack = True
            else:
                self.can_attack = False
            if distance_to_player_x < self.width/2 - 1:
                self.change_x = 0
            if (self.can_attack) and (self.frames_since_attack > self.frames_between_attack):
                self.attack()
                self.frames_since_attack = 0

            # Damage label
            for damaged_label_object in self.damaged_label_list:
                damaged_label_object.update()
                if damaged_label_object.animation_complete:
                    self.damaged_label_list.remove(damaged_label_object)

            if self.current_hp <= 0:
                self.death()

            # End of frame updates
            self.center_x += self.change_x
            self.frames_since_attack += 1
            self.time_since_damaged += 1.0 / FRAME_RATE
        else:
            # Damage label
            for damaged_label_object in self.damaged_label_list:
                damaged_label_object.update()
                if damaged_label_object.animation_complete:
                    self.damaged_label_list.remove(damaged_label_object)

            # Check animation status
            if self.death_animation_finished:
                if self.alpha > 7:
                    self.alpha -= 6
                else:
                    self.ready_to_remove = True
                    self.remove_from_sprite_lists()

    def on_draw(self):
        if self.time_since_damaged < TIME_TO_HP_BAR_DISAPPEAR:
            if self.current_hp <= 0:
                width = 0
            else:
                width = self.hp_container.width * self.current_hp / self.max_hp - 3 * RESOLUTION_SCALING
            height = self.hp_container.height - 3*RESOLUTION_SCALING
            x = self.hp_container.center_x - self.hp_container.width/2 + width/2 + 2*RESOLUTION_SCALING
            y = self.hp_container.center_y
            arcade.draw_rectangle_filled(x, y, width, height, self.hp_color)

            self.hp_container.draw()

        for damaged_label_object in self.damaged_label_list:
            damaged_label_object.draw()

    def attack(self):
        self.attacking = True
        self.current_texture = 0

        chance_to_hit = (1.0 / (1.0 + (self.game_view.player.defense_level/self.attack_level)))
        chance_to_hit_int = int(chance_to_hit*1000)
        rand_num = np.random.randint(0, 1000)
        if rand_num < chance_to_hit_int:
            self.attack_hit = True
        else:
            self.attack_hit = False

        if self.attack_hit:
            self.game_view.damage_player(self.max_damage)
        else:
            self.game_view.damage_player(0)

    def damaged(self, hp: int):
        self.current_hp -= hp
        self.time_since_damaged = 0
        damage_label = DamageLabel(hp, self)
        self.damaged_label_list.append(damage_label)

        death_return_val = False
        if self.current_hp <= 0:
            death_return_val = True

        return death_return_val

    def death(self):
        self.dead = True
        self.game_view.player.increase_xp(self.exp_reward)


    def update_animation(self, delta_time: float = 1 / 60):
        # Choose animation index
        if not self.dead:
            if self.attacking:
                if self.facing_left:
                    self.animation_index = 3
                else:
                    self.animation_index = 2
            else:
                if self.facing_left:
                    self.animation_index = 1
                else:
                    self.animation_index = 0
        else:
            if self.facing_left:
                self.animation_index = 5
            else:
                self.animation_index = 4

        self.frame_count += 1
        if self.frame_count % self.frames_before_next_animation == 0:
            self.current_texture += 1

        if self.animation_index == 0:
            if self.current_texture >= len(SpriteCache.ENEMY_SLIME_IDLE_RIGHT_ANIMATION):
                self.current_texture = 0
            self.texture = SpriteCache.ENEMY_SLIME_IDLE_RIGHT_ANIMATION[self.current_texture]
        elif self.animation_index == 1:
            if self.current_texture >= len(SpriteCache.ENEMY_SLIME_IDLE_LEFT_ANIMATION):
                self.current_texture = 0
            self.texture = SpriteCache.ENEMY_SLIME_IDLE_LEFT_ANIMATION[self.current_texture]
        elif self.animation_index == 2:
            if self.current_texture >= len(SpriteCache.ENEMY_SLIME_ATTACK_RIGHT_ANIMATION):
                self.current_texture = 0
                self.attacking = False
            self.texture = SpriteCache.ENEMY_SLIME_ATTACK_RIGHT_ANIMATION[self.current_texture]
        elif self.animation_index == 3:
            if self.current_texture >= len(SpriteCache.ENEMY_SLIME_ATTACK_LEFT_ANIMATION):
                self.current_texture = 0
                self.attacking = False
            self.texture = SpriteCache.ENEMY_SLIME_ATTACK_LEFT_ANIMATION[self.current_texture]
        elif self.animation_index == 4:
            if self.current_texture >= len(SpriteCache.ENEMY_SLIME_DEATH_RIGHT_ANIMATION):
                self.current_texture = len(SpriteCache.ENEMY_SLIME_DEATH_RIGHT_ANIMATION) - 1
                self.death_animation_finished = True
            self.texture = SpriteCache.ENEMY_SLIME_DEATH_RIGHT_ANIMATION[self.current_texture]
        elif self.animation_index == 5:
            if self.current_texture >= len(SpriteCache.ENEMY_SLIME_DEATH_LEFT_ANIMATION):
                self.current_texture = len(SpriteCache.ENEMY_SLIME_DEATH_LEFT_ANIMATION) - 1
                self.death_animation_finished = True
            self.texture = SpriteCache.ENEMY_SLIME_DEATH_LEFT_ANIMATION[self.current_texture]

