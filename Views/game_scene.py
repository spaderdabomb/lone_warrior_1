from __future__ import annotations

import arcade
import arcade.gui
import os
import time

from globals import *
from player import Player
from enemies import EnemySlime, create_enemy
from load_sprites import SpriteCache
from misc_classes import LevelUpAnimation, LevelUpLabel, NextStageArrow
from game_data import GameData

from typing import TYPE_CHECKING
from typing import Tuple
if TYPE_CHECKING:
    from sound_manager import SoundManager


class GameSceneView(arcade.View):
    def __init__(self, window: arcade.Window, sound_manager: SoundManager, world_num: int, stage_num: int):
        super().__init__()

        self.window = window
        self.sound_manager = sound_manager
        self.world_num = world_num
        self.stage_num = stage_num
        self.game_scene_initialized = False
        self.game_scene = True

        self.ui_manager = arcade.gui.UIManager(window)
        self.ui_manager.push_handlers(self.on_ui_event)
        self.physics_engine = None
        self.physics_engine_2 = None

        self.current_level = None

        self.keyup_pressed = False
        self.keydown_pressed = False
        self.keyright_pressed = False
        self.keyleft_pressed = False
        self.keyspace_pressed = False

        self.time_elapsed = 0.0
        self.frames_elapsed = 0
        self.spawn_object_index = 0
        self.last_enemy = False
        self.kill_count = 0
        self.all_enemies_killed = False

        self.setup()

    def setup(self):
        # Purge UI
        self.ui_manager.purge_ui_elements()

        # Player
        self.player = Player(os.path.join(SPRITES_PATH, 'main_character_idle.png'), 0.25, self)
        self.player.center_x = 83*RESOLUTION_SCALING
        self.player.center_y = GROUND_LEVEL

        # Setup background UI
        arcade.set_background_color(arcade.color.WHITE)
        self.current_level = Level(self.world_num, self.stage_num, self)

        # Labels
        self.hp_container = arcade.Sprite(os.path.join(SPRITES_PATH, 'XP_container_big.png'), RESOLUTION_SCALING, calculate_hit_box=False)
        self.hp_container.center_x = 1781*RESOLUTION_SCALING
        self.hp_container.center_y = (1080-100)*RESOLUTION_SCALING
        self.hp_heart = arcade.Sprite(os.path.join(SPRITES_PATH, 'heart_game_scene.png'), RESOLUTION_SCALING, calculate_hit_box=False)
        self.hp_heart.center_x = 1617*RESOLUTION_SCALING
        self.hp_heart.center_y = (1080-100)*RESOLUTION_SCALING
        self.hp_color = [228, 52, 52]
        self.xp_container = arcade.Sprite(os.path.join(SPRITES_PATH, 'XP_container_big.png'), RESOLUTION_SCALING, calculate_hit_box=False)
        self.xp_container.center_x = 1781*RESOLUTION_SCALING
        self.xp_container.center_y = (1080-46)*RESOLUTION_SCALING
        self.xp_label = arcade.Sprite(os.path.join(SPRITES_PATH, 'XP_label.png'), RESOLUTION_SCALING, calculate_hit_box=False)
        self.xp_label.center_x = 1619*RESOLUTION_SCALING
        self.xp_label.center_y = (1080-46)*RESOLUTION_SCALING
        self.xp_to_go_text = str(self.player.current_xp) + '/' + str(XP_TO_NEXT_LEVEL_LIST[self.player.current_level - 1])
        self.hp_left_text = str(self.player.current_hp) + '/' + str(self.player.max_hp)

        self.physics_engine = arcade.PhysicsEnginePlatformer(self.player, self.current_level.platform_spritelist, GRAVITY)
        self.enemy_physics_engines_list = []

        # For shuriken powerup
        self.shuriken_sprite_list = arcade.SpriteList()
        self.shurikens_highlighted = 0
        self.shuriken_ready = False
        tutorials_passed_list = GameData.data['tutorials_passed']
        if tutorials_passed_list[2]:
            for i in range(6):
                shuriken = arcade.Sprite(os.path.join(SPRITES_PATH, 'shuriken_power_up_bar.png'), RESOLUTION_SCALING)
                shuriken.center_x = 53*RESOLUTION_SCALING + (47*i)*RESOLUTION_SCALING
                shuriken.center_y = (1080-98)*RESOLUTION_SCALING
                shuriken.alpha = 0.5*255
                self.shuriken_sprite_list.append(shuriken)

        # Pop up stuff
        self.leveled_up_label_list = arcade.SpriteList()
        self.leveled_up_animation_list = arcade.SpriteList()
        self.next_level_arrow_list = arcade.SpriteList()

        self.game_scene_initialized = True

    def on_ui_event(self, event: arcade.gui.UIEvent):
        if event.type == arcade.gui.UIClickable.CLICKED and event.get('ui_element').id == 'settings_button':
            pass
            # start_menu_view = start_menu.StartMenuView()
            # self.window.show_view(start_menu_view)

    def on_draw(self):
        arcade.start_render()

        # Draw main sprites
        self.current_level.level_background_sprite_list.draw()
        self.current_level.platform_spritelist.draw()
        self.leveled_up_label_list.draw()
        self.leveled_up_animation_list.draw()
        self.next_level_arrow_list.draw()
        for enemy in self.current_level.enemy_spritelist:
            enemy.draw()
            enemy.on_draw()
        self.player.draw()
        self.player.on_draw()
        self.hp_heart.draw()
        self.xp_label.draw()
        self.shuriken_sprite_list.draw()

        # Draw hp bar
        if self.player.current_hp == 0:
            width = 0
        else:
            width = self.hp_container.width*self.player.current_hp/self.player.max_hp - 8*RESOLUTION_SCALING
        height = self.hp_container.height - 8*RESOLUTION_SCALING
        x = self.hp_container.center_x - self.hp_container.width/2 + width/2 + 4*RESOLUTION_SCALING
        y = self.hp_container.center_y
        arcade.draw_rectangle_filled(x, y, width, height, self.hp_color)

        # Draw xp bar
        if self.player.current_xp == 0:
            width = 0
        else:
            width = self.xp_container.width * self.player.current_xp / XP_TO_NEXT_LEVEL_LIST[
                self.player.current_level - 1] - 8 * RESOLUTION_SCALING
        height = self.xp_container.height - 8*RESOLUTION_SCALING
        x = self.xp_container.center_x - self.xp_container.width/2 + width/2 + 4*RESOLUTION_SCALING
        y = self.xp_container.center_y
        arcade.draw_rectangle_filled(x, y, width, height, [74, 94, 198])

        self.hp_container.draw()
        self.xp_container.draw()

        self.xp_to_go_label = arcade.draw_text(self.xp_to_go_text, 1690*RESOLUTION_SCALING,
                                               (1080-47)*RESOLUTION_SCALING,
                                               arcade.color.WHITE,
                                               align="left", anchor_x="left", anchor_y="center",
                                               bold=True, font_size=17)
        self.hp_left_label = arcade.draw_text(self.hp_left_text, 1690*RESOLUTION_SCALING,
                                               (1080-101)*RESOLUTION_SCALING,
                                               arcade.color.WHITE,
                                               align="left", anchor_x="left", anchor_y="center",
                                               bold=True, font_size=17)

        # self.player.draw_hit_box()
        # for platform in self.current_level.platform_spritelist:
        #     platform.draw_hit_box()
        # for enemy in self.current_level.enemy_spritelist:
        #     enemy.draw_hit_box()


    def on_update(self, dt):
        # Update main sprites
        self.shuriken_sprite_list.update()
        self.current_level.enemy_spritelist.update()
        self.current_level.enemy_spritelist.update_animation(dt)
        if self.game_scene_initialized:
            self.player.update()
            self.player.update_animation(dt)
        self.sound_manager.update()
        self.physics_engine.update()
        for physics_engine in self.enemy_physics_engines_list:
            physics_engine.update()
        self.leveled_up_label_list.update()
        self.leveled_up_animation_list.update()
        self.next_level_arrow_list.update()

        # Handle key presses
        if (self.keyup_pressed) and (self.physics_engine.can_jump()):
            self.player.handle_jump()

        # Handle Player HP
        if self.player.current_hp/self.player.max_hp < 0.25:
            self.hp_color = [182, 1, 1]
        else:
            self.hp_color = [228, 52, 52]

        # Handle powerup bar
        if self.frames_elapsed % 10 == 9:
            tutorials_passed_list = GameData.data['tutorials_passed']
            if tutorials_passed_list[2] and self.shurikens_highlighted < 6:
                self.shuriken_sprite_list[self.shurikens_highlighted].alpha = 255
                self.shurikens_highlighted += 1
                if self.shurikens_highlighted == 6:
                    self.shuriken_ready = True

        if self.keyspace_pressed and self.shuriken_ready:
            self.player.attack_shuriken()
            self.shuriken_ready = False
            self.shurikens_highlighted = 0
            for shuriken in self.shuriken_sprite_list:
                shuriken.alpha = 0.5*255

        # Text
        self.xp_to_go_text = str(self.player.current_xp) + '/' + str(XP_TO_NEXT_LEVEL_LIST[self.player.current_level - 1])
        self.hp_left_text = str(self.player.current_hp) + '/' + str(self.player.max_hp)

        # Handle enemies
        if len(self.current_level.spawn_object_list) - 1 >= self.spawn_object_index:
            next_spawn_object = self.current_level.spawn_object_list[self.spawn_object_index]
            if self.time_elapsed > next_spawn_object.spawn_time:
                # Create new enemy
                new_enemy = create_enemy(self, next_spawn_object.enemy_type, 1.0)
                new_enemy.center_x = next_spawn_object.spawn_position[0]
                new_enemy.center_y = next_spawn_object.spawn_position[1]
                self.current_level.enemy_spritelist.append(new_enemy)
                self.spawn_object_index += 1

                # Add enemy to physics engine
                enemy_physics_engine = arcade.PhysicsEnginePlatformer(new_enemy,
                                                                      self.current_level.platform_spritelist,
                                                                      GRAVITY)
                self.enemy_physics_engines_list.append(enemy_physics_engine)
        else:
            self.last_enemy = True

        # Add next level arrow
        if self.kill_count >= len(self.current_level.spawn_object_list) and not self.all_enemies_killed:
            self.all_enemies_killed = True
            next_stage_arrow = NextStageArrow(os.path.join(SPRITES_PATH, 'next_stage_arrow.png'), 1.00)
            self.next_level_arrow_list.append(next_stage_arrow)

        # Finish current stage
        if self.player.center_x >= SCREEN_WIDTH - SCREEN_WIDTH/8 and self.all_enemies_killed:
            self.win_or_loss_scene()

        # End of update calls
        self.time_elapsed += 1.0/FRAME_RATE
        self.frames_elapsed += 1

    def damage_player(self, hp: int):
        self.player.damaged(hp)

    def damage_enemy(self, enemy, hp: int):
        dead = enemy.damaged(hp)
        if dead:
            self.kill_count += 1

    def player_level_up(self):
        level_up_label = LevelUpLabel(os.path.join(SPRITES_PATH, 'level_up_label.png'), 1.0)
        self.leveled_up_label_list.append(level_up_label)
        level_up_animation = LevelUpAnimation(SpriteCache.LEVEL_UP_ANIMATION[0], 0.35, self.player)
        level_up_animation.texture = SpriteCache.LEVEL_UP_ANIMATION[0]
        self.leveled_up_animation_list.append(level_up_animation)

    def on_key_press(self, key, modifiers):
        if key == arcade.key.UP:
            self.player.jump_pressed = True
            self.player.double_jump_pressed = True
            self.keyup_pressed = True
        elif key == arcade.key.DOWN:
            self.keydown_pressed = True
        elif key == arcade.key.LEFT:
            self.player.change_x = -self.player.movement_speed
            self.keyleft_pressed = True
        elif key == arcade.key.RIGHT:
            self.player.change_x = self.player.movement_speed
            self.keyright_pressed = True
        elif key == arcade.key.SPACE:
            self.keyspace_pressed = True

        # # Pause Menu
        # if key == arcade.key.ESCAPE:
        #     pause = Pause.PauseView(self)
        #     self.window.show_view(pause)

    def on_key_release(self, key, modifiers):
        if key == arcade.key.UP:
            self.player.jump_pressed = False
            self.player.jump_key_down = False
            self.keyup_pressed = False
        elif key == arcade.key.DOWN:
            self.keydown_pressed = False
        elif key == arcade.key.LEFT:
            self.player.change_x = 0
            self.keyleft_pressed = False
        elif key == arcade.key.RIGHT:
            self.player.change_x = 0
            self.keyright_pressed = False
        elif key == arcade.key.SPACE:
            self.keyspace_pressed = False

        # Extra logic for holding down keys
        if self.keyup_pressed:
            self.player.jump_key_down = True
            self.player.double_jump_key_down = True
        if self.keydown_pressed:
            pass
        if self.keyleft_pressed:
            self.player.change_x = -self.player.movement_speed
        if self.keyright_pressed:
            self.player.change_x = self.player.movement_speed

    def win_or_loss_scene(self):
        if self.player.current_hp > 0:
            self.win_stage()
        else:
            self.lose_stage()

    def win_stage(self):
        game_scene_view = GameSceneView(self.window, self.sound_manager, self.world_num, self.stage_num + 1)
        self.window.show_view(game_scene_view)

    def lose_stage(self):
        pass


class SpawnObject:
    def __init__(self, spawn_position: Tuple, spawn_time: float, enemy_type: int):
        super().__init__()

        self.spawn_position = spawn_position
        self.spawn_time = spawn_time
        self.enemy_type = enemy_type


class Level:
    def __init__(self, world_num: int, stage_num: int, game_view: GameSceneView):
        super().__init__()

        self.game_view = game_view
        self.world_num = world_num
        self.stage_num = stage_num
        # self.stage_num = 3

        self.level_background = None

        self.setup_level()

    def setup_level(self):
        # All level stuff
        self.level_background_sprite_list = arcade.SpriteList()

        # Level specific
        if self.world_num == 0:
            # Level background
            self.level_background = arcade.Sprite(os.path.join(SPRITES_PATH, 'menu_training_room.png'), RESOLUTION_SCALING, calculate_hit_box=False)
            self.level_background.center_x = SCREEN_WIDTH/2
            self.level_background.center_y = SCREEN_HEIGHT/2
            self.level_background_sprite_list.append(self.level_background)

            self.platform_spritelist = arcade.SpriteList(use_spatial_hash=True)
            self.platform_0 = arcade.Sprite(os.path.join(SPRITES_PATH, 'brick_platform_ground.png'), RESOLUTION_SCALING, calculate_hit_box=False)
            self.platform_0.center_x = SCREEN_WIDTH/2
            self.platform_0.center_y = (1080-880)*RESOLUTION_SCALING
            self.platform_1 = arcade.Sprite(os.path.join(SPRITES_PATH, 'brick_platform_1.png'), RESOLUTION_SCALING, calculate_hit_box=False)
            self.platform_1.center_x = 407*RESOLUTION_SCALING
            self.platform_1.center_y = (1080-597)*RESOLUTION_SCALING
            self.platform_2 = arcade.Sprite(os.path.join(SPRITES_PATH, 'brick_platform_1.png'), RESOLUTION_SCALING, calculate_hit_box=False)
            self.platform_2.center_x = 1508*RESOLUTION_SCALING
            self.platform_2.center_y = (1080-597)*RESOLUTION_SCALING
            self.platform_spritelist.extend([self.platform_0, self.platform_1, self.platform_2])

        elif self.world_num == 1:
            if self.stage_num == 1:
                # Level background
                self.level_background = arcade.Sprite(os.path.join(SPRITES_PATH, 'world_1_1.png'), RESOLUTION_SCALING, calculate_hit_box=False)
                self.level_background.center_x = SCREEN_WIDTH/2
                self.level_background.center_y = SCREEN_HEIGHT/2
                self.level_background_sprite_list.append(self.level_background)

                self.platform_spritelist = arcade.SpriteList(use_spatial_hash=True)
                self.platform_0 = arcade.Sprite(os.path.join(SPRITES_PATH, 'brick_platform_ground.png'), RESOLUTION_SCALING, calculate_hit_box=False)
                self.platform_0.center_x = SCREEN_WIDTH/2
                self.platform_0.center_y = (1080-0)*RESOLUTION_SCALING
                self.platform_1 = arcade.Sprite(os.path.join(SPRITES_PATH, 'brick_platform_1.png'), RESOLUTION_SCALING, calculate_hit_box=False)
                self.platform_1.center_x = 1600*RESOLUTION_SCALING
                self.platform_1.center_y = (1080-284)*RESOLUTION_SCALING
                self.platform_2 = arcade.Sprite(os.path.join(SPRITES_PATH, 'brick_platform_1.png'), RESOLUTION_SCALING, calculate_hit_box=False)
                self.platform_2.center_x = 318*RESOLUTION_SCALING
                self.platform_2.center_y = (1080-282)*RESOLUTION_SCALING
                self.platform_3 = arcade.Sprite(os.path.join(SPRITES_PATH, 'brick_platform_1.png'), RESOLUTION_SCALING, calculate_hit_box=False)
                self.platform_3.center_x = 921*RESOLUTION_SCALING
                self.platform_3.center_y = (1080-560)*RESOLUTION_SCALING
                self.platform_4 = arcade.Sprite(os.path.join(SPRITES_PATH, 'brick_platform_ground.png'), RESOLUTION_SCALING, calculate_hit_box=False)
                self.platform_4.center_x = SCREEN_WIDTH/2
                self.platform_4.center_y = (1080-876)*RESOLUTION_SCALING
                self.platform_spritelist.extend([self.platform_0, self.platform_1, self.platform_2, self.platform_3,
                                                 self.platform_4])

                self.enemy_spritelist = arcade.SpriteList()

                # spawn_point_1 = (SCREEN_WIDTH/2 + 100*RESOLUTION_SCALING, GROUND_LEVEL)
                # spawn_point_2 = (SCREEN_WIDTH + 50*RESOLUTION_SCALING, GROUND_LEVEL)
                # spawn_object_position_list = [spawn_point_1]
                # spawn_object_time_list = [0]
                # spawn_object_type_list = [0]

                spawn_point_1 = (SCREEN_WIDTH/2 + 100*RESOLUTION_SCALING, GROUND_LEVEL)
                spawn_point_2 = (SCREEN_WIDTH + 50*RESOLUTION_SCALING, GROUND_LEVEL)
                spawn_object_position_list = [spawn_point_1, spawn_point_1, spawn_point_2, spawn_point_2, spawn_point_2,
                                              spawn_point_2, spawn_point_2]
                spawn_object_time_list = [0, 5, 10, 14, 17, 19, 20]
                spawn_object_type_list = [0, 0, 0, 0, 0, 0, 0]

                self.spawn_object_list = [SpawnObject(spawn_object_position_list[i], spawn_object_time_list[i],
                                                  spawn_object_type_list[i]) for i in range(len(spawn_object_position_list))]
            elif self.stage_num == 2:
                self.level_background = arcade.Sprite(os.path.join(SPRITES_PATH, 'world_1_2.png'), RESOLUTION_SCALING,
                                                      calculate_hit_box=False)
                self.level_background.center_x = SCREEN_WIDTH / 2
                self.level_background.center_y = SCREEN_HEIGHT / 2
                self.level_background_sprite_list.append(self.level_background)

                self.platform_spritelist = arcade.SpriteList(use_spatial_hash=True)
                self.platform_0 = arcade.Sprite(os.path.join(SPRITES_PATH, 'brick_platform_ground_2.png'), RESOLUTION_SCALING,
                                                calculate_hit_box=False)
                self.platform_0.center_x = SCREEN_WIDTH / 2
                self.platform_0.center_y = (1080 - 0) * RESOLUTION_SCALING
                self.platform_1 = arcade.Sprite(os.path.join(SPRITES_PATH, 'brick_platform_1.png'), RESOLUTION_SCALING,
                                                calculate_hit_box=False)
                self.platform_1.center_x = 121 * RESOLUTION_SCALING
                self.platform_1.center_y = (1080 - 398) * RESOLUTION_SCALING
                self.platform_2 = arcade.Sprite(os.path.join(SPRITES_PATH, 'brick_platform_1.png'), RESOLUTION_SCALING,
                                                calculate_hit_box=False)
                self.platform_2.center_x = 960 * RESOLUTION_SCALING
                self.platform_2.center_y = (1080 - 559) * RESOLUTION_SCALING
                self.platform_3 = arcade.Sprite(os.path.join(SPRITES_PATH, 'brick_platform_1.png'), RESOLUTION_SCALING,
                                                calculate_hit_box=False)
                self.platform_3.center_x = 1805 * RESOLUTION_SCALING
                self.platform_3.center_y = (1080 - 386) * RESOLUTION_SCALING
                self.platform_4 = arcade.Sprite(os.path.join(SPRITES_PATH, 'brick_platform_ground_2.png'), RESOLUTION_SCALING,
                                                calculate_hit_box=False)
                self.platform_4.center_x = SCREEN_WIDTH / 2
                self.platform_4.center_y = (1080 - 876) * RESOLUTION_SCALING
                self.platform_spritelist.extend([self.platform_0, self.platform_1, self.platform_2, self.platform_3,
                                                 self.platform_4])

                self.enemy_spritelist = arcade.SpriteList()

                spawn_point_1 = (SCREEN_WIDTH + 50 * RESOLUTION_SCALING, GROUND_LEVEL)
                spawn_point_2 = (0 - 50 * RESOLUTION_SCALING, GROUND_LEVEL)
                spawn_object_position_list = [spawn_point_1, spawn_point_2, spawn_point_2, spawn_point_2, spawn_point_2,
                                              spawn_point_1, spawn_point_1, spawn_point_2]
                spawn_object_time_list = [0, 5, 10, 15, 18, 20, 25, 25]
                spawn_object_type_list = [0 for i in range(len(spawn_object_position_list))]
                self.spawn_object_list = [SpawnObject(spawn_object_position_list[i], spawn_object_time_list[i],
                                                      spawn_object_type_list[i]) for i in
                                          range(len(spawn_object_position_list))]
            elif self.stage_num == 3:
                self.level_background = arcade.Sprite(os.path.join(SPRITES_PATH, 'world_1_3.png'), RESOLUTION_SCALING,
                                                      calculate_hit_box=False)
                self.level_background.center_x = SCREEN_WIDTH / 2
                self.level_background.center_y = SCREEN_HEIGHT / 2
                self.level_background_sprite_list.append(self.level_background)

                self.platform_spritelist = arcade.SpriteList(use_spatial_hash=True)
                self.platform_0 = arcade.Sprite(os.path.join(SPRITES_PATH, 'brick_platform_1.png'), RESOLUTION_SCALING,
                                                calculate_hit_box=False)
                self.platform_0.center_x = 490 * RESOLUTION_SCALING
                self.platform_0.center_y = (1080 - 546) * RESOLUTION_SCALING
                self.platform_1 = arcade.Sprite(os.path.join(SPRITES_PATH, 'brick_platform_1.png'), RESOLUTION_SCALING,
                                                calculate_hit_box=False)
                self.platform_1.center_x = 1459 * RESOLUTION_SCALING
                self.platform_1.center_y = (1080 - 546) * RESOLUTION_SCALING
                self.platform_2 = arcade.Sprite(os.path.join(SPRITES_PATH, 'brick_platform_ground_2.png'), RESOLUTION_SCALING,
                                                calculate_hit_box=False)
                self.platform_2.center_x = SCREEN_WIDTH / 2
                self.platform_2.center_y = (1080 - 876) * RESOLUTION_SCALING
                self.platform_spritelist.extend([self.platform_0, self.platform_1, self.platform_2])

                self.enemy_spritelist = arcade.SpriteList()

                spawn_point_1 = (SCREEN_WIDTH + 50 * RESOLUTION_SCALING, GROUND_LEVEL)
                spawn_point_2 = (0 - 50 * RESOLUTION_SCALING, GROUND_LEVEL)
                spawn_point_3 = (self.platform_0.center_x, self.platform_0.center_y + 50*RESOLUTION_SCALING)
                spawn_point_4 = (self.platform_1.center_x, self.platform_1.center_y + 50*RESOLUTION_SCALING)
                spawn_point_5 = (self.platform_0.center_x, (1080 - 0)*RESOLUTION_SCALING + 150*RESOLUTION_SCALING)
                spawn_point_6 = (self.platform_1.center_x, (1080 - 0)*RESOLUTION_SCALING + 150*RESOLUTION_SCALING)
                spawn_object_position_list = [spawn_point_3, spawn_point_4, spawn_point_1, spawn_point_2, spawn_point_5,
                                              spawn_point_6, spawn_point_5, spawn_point_6, spawn_point_1, spawn_point_2,
                                              spawn_point_5, spawn_point_6, spawn_point_1, spawn_point_2]
                spawn_object_time_list = [0, 0, 0, 0, 5, 5, 6, 6, 12, 12, 13, 13, 20, 20]
                spawn_object_type_list = [0 for i in range(len(spawn_object_position_list))]
                self.spawn_object_list = [SpawnObject(spawn_object_position_list[i], spawn_object_time_list[i],
                                                      spawn_object_type_list[i]) for i in
                                          range(len(spawn_object_position_list))]

                if len(spawn_object_position_list) != len(spawn_object_time_list):
                    print('You fucked up level init')

        elif self.world_num == 2:
            pass
        elif self.world_num == 3:
            pass
        elif self.world_num == 4:
            pass

        # All level stuff
        tutorials_passed_list = GameData.data['tutorials_passed']
        if tutorials_passed_list[2]:
            powerup_bar_text = arcade.Sprite(os.path.join(SPRITES_PATH, 'powerup_bar_text.png'), RESOLUTION_SCALING, calculate_hit_box=False)
            powerup_bar_text.center_x = 161*RESOLUTION_SCALING
            powerup_bar_text.center_y = (1080-45)*RESOLUTION_SCALING
            self.level_background_sprite_list.append(powerup_bar_text)
