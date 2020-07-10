import arcade
import os
import numpy as np
from time import time

from CoronaJump.globals import *
from CoronaJump.Assets.Views import GameOver, Pause, SubmitHighscore
from CoronaJump.game_data import GameData
from CoronaJump.load_sprites import SpriteCache

from PyQt5.QtWidgets import QLineEdit


class Player(arcade.Sprite):

    def __init__(self, file_name, scale):
        super().__init__(file_name, scale)

        # Powerups
        #   1 = shield
        #   2 = ...

        self.health = 1
        self.jump_height = 400 / 60

        #self.powerups_enabled_list = [False for i in range(NUM_POWERUPS_PERMANENT)]
        self.powerups_enabled_list = [True for i in range(NUM_POWERUPS_PERMANENT)]
        self.powerups_active_list = [False for i in range(NUM_POWERUPS_PERMANENT)]

        self.powerup_level_list = [0 for i in range(NUM_POWERUPS_PERMANENT)]
        self.powerup_recharge_time_list = [
            POWERUP_RECHARGE_TIMES[i] * (1 - (self.powerup_level_list[i] / (2 * POWERUP_MAX_LEVEL)))
            for i in range(NUM_POWERUPS_PERMANENT)]
        self.powerup_time_since_used = [0 for i in range(NUM_POWERUPS_PERMANENT)]

        self.time_since_jump = 0
        self.time_since_double_jump = 0
        self.jump_pressed = False
        self.jump_key_down = False
        self.jumping = False

        self.shield_pressed = False
        self.shield_key_down = False
        self.shield_hit = False
        self.time_shield_active = 0
        self.shield_list = arcade.SpriteList()

        self.double_jump_pressed = False
        self.double_jump_key_down = False
        self.double_jumping_allowed = False
        self.double_jumping = False

        self.slime_blast_pressed = False
        self.slime_blast_key_down = False
        self.slime_blast_sprite_list = arcade.SpriteList()

        self.shockwave_pressed = False
        self.shockwave_key_down = False
        self.shockwave_sprite_list = arcade.SpriteList()

        self.time_warp_pressed = False
        self.time_warp_key_down = False
        self.time_warp_sprite_list = arcade.SpriteList()
        self.timer_hand_sprite_list = arcade.SpriteList()
        self.timer_hand_rotation = 0

        self.current_texture = 0
        self.frame_count = 0
        self.frames_before_next_animation = 3

        self.attack = False
        self.death = False
        self.hit = False
        self.idle = True

    def update(self):
        self.center_x += self.change_x

        # Handle screen boundaries
        if self.left < 0:
            self.left = SCREEN_BORDER_PADDING
        elif self.right > SCREEN_WIDTH - SCREEN_BORDER_PADDING:
            self.right = SCREEN_WIDTH - SCREEN_BORDER_PADDING

        self.handle_jump()
        if self.powerups_enabled_list[1]:
            self.handle_double_jump()
        if self.powerups_enabled_list[0]:
            self.handle_shield()
        if self.powerups_enabled_list[2]:
            self.handle_slime_blast()
        if self.powerups_enabled_list[3]:
            self.handle_shockwave()
        if self.powerups_enabled_list[4]:
            self.handle_time_warmp()

        for i in range(len(self.powerup_time_since_used)):
            self.powerup_time_since_used[i] += 1 / FRAME_RATE

        # Reset frame dependent values
        self.double_jumping_allowed = False
        self.jump_pressed = False
        self.double_jump_pressed = False
        self.slime_blast_pressed = False
        self.shockwave_pressed = False
        self.time_warp_pressed = False
        for i in range(len(self.powerups_enabled_list)):
            if self.powerups_enabled_list[i] is False:
                self.powerup_time_since_used[i] = 0

    def handle_jump(self):
        # Handle of jump key is pressed or held down
        if (self.jump_pressed or self.jump_key_down):
            if self.jump_pressed and self.jumping:
                self.double_jumping_allowed = True
            self.jumping = True

        # Change values if jumping
        if self.jumping:
            self.change_y = self.jump_height - self.time_since_jump * 6
            self.time_since_jump += 1 / FRAME_RATE
        else:
            self.change_y = 0
            self.time_since_jump = 0

        self.center_y += self.change_y

        # Handle if jump is completed
        if self.center_y <= GROUND_LEVEL:
            self.center_y = GROUND_LEVEL
            self.jumping = False
            self.double_jumping_allowed = False
            self.time_since_jump = 0

    def handle_shield(self):

        # Handle logic if shield is ready and shield button is pressed
        if ((self.powerup_time_since_used[0] > self.powerup_recharge_time_list[0]) and
                ((self.shield_pressed) or self.shield_key_down) and
                (self.powerups_enabled_list[0]) and
                (self.powerups_active_list[0] is False)):
            shield = arcade.Sprite(os.path.join(SPRITES_PATH, 'Shield.png'), SPRITE_SCALING)
            shield.center_x = self.center_x + shield.width / 2
            shield.center_y = self.center_y
            shield.alpha = 150
            self.shield_list.append(shield)

            self.powerups_active_list[0] = True
            self.powerup_time_since_used[0] = 0
            self.shield_pressed = False

        # Handle if shield has expired or not
        if (self.shield_hit) or (POWERUP_ACTIVE_TIMES[0] < self.time_shield_active):
            self.powerups_active_list[0] = False
            self.time_shield_active = 0
            for shield in self.shield_list:
                self.shield_hit = False
                shield.remove_from_sprite_lists()

        for shield in self.shield_list:
            shield.center_x = self.center_x
            shield.center_y = self.center_y
            self.time_shield_active += 1 / FRAME_RATE

    def handle_double_jump(self):

        self.change_y = 0
        if (self.double_jump_pressed and
                self.jumping and
                self.powerups_enabled_list[1] and
                self.powerups_active_list[1] is False and
                self.powerup_time_since_used[1] > self.powerup_recharge_time_list[1] and
                self.double_jumping_allowed):
            self.double_jumping = True
            self.double_jump_pressed = False
            self.time_since_double_jump = 0
            self.powerup_time_since_used[1] = 0

        if self.double_jumping:
            self.change_y = self.jump_height * 1.5 - self.time_since_double_jump * 6
            self.time_since_double_jump += 1 / FRAME_RATE
            self.powerup_time_since_used[1] += 1 / FRAME_RATE
        else:
            self.change_y = 0

        self.center_y += self.change_y
        if self.center_y <= GROUND_LEVEL:
            self.center_y = GROUND_LEVEL
            self.double_jumping = False
            self.powerups_active_list[1] = False
            self.time_since_double_jump = 0

    def handle_slime_blast(self):
        # Handle logic if slime_blast is ready and slime_blast button is pressed
        if ((self.powerup_time_since_used[2] > self.powerup_recharge_time_list[2]) and
                ((self.slime_blast_pressed) or self.slime_blast_key_down) and
                (self.powerups_enabled_list[2]) and
                (self.powerups_active_list[2] is False)):
            slime_blast = arcade.Sprite(os.path.join(SPRITES_PATH, 'slime_blast.png'), SPRITE_SCALING)
            slime_blast.center_x = self.center_x
            slime_blast.center_y = self.center_y
            self.slime_blast_sprite_list.append(slime_blast)

            self.powerups_active_list[2] = True
            self.powerup_time_since_used[2] = 0
            self.slime_blast_pressed = False

        # Handle if slime blast has expired or not
        if (self.powerup_time_since_used[2] > POWERUP_ACTIVE_TIMES[2]) and (self.powerups_active_list[2]):
            self.powerups_active_list[2] = False
            self.powerup_time_since_used[2] = 0
            for slime_blast in self.slime_blast_sprite_list:
                slime_blast.remove_from_sprite_lists()

        for slime_blast in self.slime_blast_sprite_list:
            slime_blast.center_x = self.center_x + slime_blast.width / 2
            slime_blast.center_y = self.center_y

    def handle_shockwave(self):
        # Handle logic if shockwave is ready and shockwave button is pressed
        if ((self.powerup_time_since_used[3] > self.powerup_recharge_time_list[3]) and
                ((self.shockwave_pressed) or self.shockwave_key_down) and
                (self.powerups_enabled_list[3]) and
                (self.powerups_active_list[3] is False)):
            shockwave = arcade.Sprite(os.path.join(SPRITES_PATH, 'shockwave.png'), SPRITE_SCALING)
            shockwave.center_x = self.center_x
            shockwave.center_y = self.center_y
            self.shockwave_sprite_list.append(shockwave)

            self.powerups_active_list[3] = True
            self.powerup_time_since_used[3] = 0
            self.shockwave_pressed = False

        # Handle if shockwave blast has expired or not
        if (self.powerup_time_since_used[3] > POWERUP_ACTIVE_TIMES[3]) and (self.powerups_active_list[3]):
            self.powerups_active_list[3] = False
            for shockwave in self.shockwave_sprite_list:
                shockwave.remove_from_sprite_lists()

        for shockwave in self.shockwave_sprite_list:
            shockwave.scale += 0.1
            shockwave.collision_radius = shockwave.scale * shockwave.width

    def handle_time_warmp(self):
        # Handle logic if time_warp is ready and time_warp button is pressed
        if ((self.powerup_time_since_used[4] > self.powerup_recharge_time_list[4]) and
                ((self.time_warp_pressed) or self.time_warp_key_down) and
                (self.powerups_enabled_list[4]) and
                (self.powerups_active_list[4] is False)):
            time_warp = arcade.Sprite(os.path.join(SPRITES_PATH, 'timer.png'), SPRITE_SCALING / 2)
            time_warp.center_x = SCREEN_WIDTH / 2
            time_warp.center_y = SCREEN_HEIGHT * 6 / 7
            self.time_warp_sprite_list.append(time_warp)

            timer_hand = arcade.Sprite(os.path.join(SPRITES_PATH, "timer_hand.png"), SPRITE_SCALING / 2)
            timer_hand.center_x = SCREEN_WIDTH / 2
            timer_hand.center_y = SCREEN_HEIGHT * 6 / 7
            self.timer_hand_sprite_list.append(timer_hand)

            self.powerups_active_list[4] = True
            self.powerup_time_since_used[4] = 0
            self.time_warp_pressed = False

        # Handle if time_warp blast has expired or not
        if (self.powerup_time_since_used[4] > POWERUP_ACTIVE_TIMES[4]) and (self.powerups_active_list[4]):
            Globals.GLOBAL_SCROLL_SPEED = 10
            self.powerups_active_list[4] = False
            for time_warp in self.time_warp_sprite_list:
                time_warp.remove_from_sprite_lists()
            for timer_hand in self.timer_hand_sprite_list:
                timer_hand.remove_from_sprite_lists()

        for time_warp in self.time_warp_sprite_list:
            Globals.GLOBAL_SCROLL_SPEED = 5
            self.timer_hand_rotation -= 2 * (360 / 60) / (POWERUP_ACTIVE_TIMES[4])
            self.timer_hand_rotation %= 360

    def update_animation(self, delta_time: float = 1 / 60):
        self.frame_count += 1
        if self.frame_count % self.frames_before_next_animation == 0:
            self.current_texture += 1

        if self.idle:
            if self.current_texture >= len(SpriteCache.SPRITELIST_CORONAVIRUS_IDLE):
                self.current_texture = 0
            self.texture = SpriteCache.SPRITELIST_CORONAVIRUS_IDLE[self.current_texture]


class Obstacle(arcade.Sprite):

    def __init__(self, file_name, scale):
        super().__init__(file_name, scale)

        self.type = 0
        self.custom_scale = 1
        self.cur_texture = 0
        self.frame_count = 0
        self.animation_frames_per_transition = 5
        self.animation_textures = []

        self.animation_sequence_state = 0

        self.jumping = False
        self.dying = False
        self.sequence_repeat = False
        self.sequence_running = False
        self.sequence_num_repeats = 0
        self.sequence_repeat_index = 0

        self.change_y = 0
        self.jump_velocity = 15
        self.jump_time = 0.833
        self.jump_gravity = 0.6

        self.dead = False

    def init_animation_textures(self):
        if self.type == 1:
            self.custom_scale = 0.8
            self.scale = self.custom_scale
            self.animation_textures = SpriteCache.SPRITELIST_COWBOY_RUN
        elif self.type == 2:
            self.custom_scale = 0.8
            self.scale = self.custom_scale
            self.animation_textures = SpriteCache.SPRITELIST_NINJA_RUN
        elif self.type == 3:
            self.custom_scale = 0.8
            self.scale = self.custom_scale
            self.animation_textures = SpriteCache.SPRITELIST_PLANE_FLY
        elif self.type == 4:
            self.custom_scale = 0.8
            self.scale = self.custom_scale
            self.animation_textures = SpriteCache.SPRITELIST_DINO_RUN
        elif self.type == 5:
            self.custom_scale = 0.8
            self.scale = self.custom_scale
            self.animation_textures = SpriteCache.SPRITELIST_ROBOT_RUNSHOOT
        elif self.type == 6:
            self.custom_scale = 0.8
            self.scale = self.custom_scale
            self.animation_textures = SpriteCache.SPRITELIST_NINJA_RUN

    def update(self):
        if self.type == 1:
            self.change_x = -Globals.GLOBAL_SCROLL_SPEED
            if self.jumping:
                self.change_y -= self.jump_gravity
            else:
                self.change_y = 0
                self.center_y = GROUND_LEVEL

            if self.center_y < GROUND_LEVEL:
                self.jumping = False
                self.center_y = GROUND_LEVEL
                self.change_y = 0

            if self.dead:
                self.alpha -= 4
                if self.alpha < 4:
                    self.alpha = 5
        elif self.type == 2:
            self.change_x = -Globals.GLOBAL_SCROLL_SPEED
            self.change_y = 0
        elif self.type == 3:
            self.change_x = -Globals.GLOBAL_SCROLL_SPEED
            self.change_y = 0
        elif self.type == 4:
            self.change_x = -Globals.GLOBAL_SCROLL_SPEED
            self.change_y = 0
        elif self.type == 5:
            self.change_x = -Globals.GLOBAL_SCROLL_SPEED
            self.change_y = 0
        elif self.type == 6:
            self.change_x = -Globals.GLOBAL_SCROLL_SPEED
            self.change_y = 0

        self.center_x += self.change_x
        self.center_y += self.change_y

    def handle_animation_sequence_state(self):
        if self.type == 1:
            if self.animation_sequence_state == 1 and self.sequence_running is False:
                self.animation_textures = SpriteCache.SPRITELIST_COWBOY_JUMP
                self.change_y = self.jump_velocity
                self.jumping = True
                self.sequence_repeat = False
                self.sequence_running = True
                self.sequence_num_repeats = 0
            elif self.animation_sequence_state == 2 and self.dying is False:
                self.animation_textures = SpriteCache.SPRITELIST_COWBOY_DEATH
                self.dying = True
                self.sequence_repeat = False
                self.sequence_running = True
                self.sequence_num_repeats = 0
            elif self.cur_texture > (len(self.animation_textures) - 1):
                if self.dead:
                    self.remove_from_sprite_lists()
                else:
                    self.cur_texture = 0
                    if self.sequence_repeat_index < self.sequence_num_repeats:
                        self.sequence_repeat_index += 1
                    else:
                        self.animation_sequence_state = 0
                        self.sequence_running = False
                        self.sequence_repeat = False
                        self.sequence_repeat_index = 0
                        self.jumping = False
                        self.dying = False
                        self.dead = False
                        self.animation_textures = SpriteCache.SPRITELIST_COWBOY_RUN
        elif self.type == 2:
            pass
        elif self.type == 3:
            pass
        elif self.type == 4:
            pass
        elif self.type == 5:
            pass
        elif self.type == 6:
            pass

    def update_animation(self, delta_time: float = 1 / 60):

        if self.type == 1:
            # Handle texture number
            self.frame_count += 1
            if self.frame_count % self.animation_frames_per_transition == 0:
                self.cur_texture += 1

            # Handle animation sequence events
            random_generator_jump = np.random.randint(1, 120)
            if self.dead and self.dying is False:
                self.cur_texture = 0
                self.animation_sequence_state = 2
                self.handle_animation_sequence_state()
            elif random_generator_jump == 1 and self.jumping is False and self.dead is False:
                self.cur_texture = 0
                self.animation_sequence_state = 1
                self.handle_animation_sequence_state()
            elif self.cur_texture > (len(self.animation_textures) - 1):
                self.handle_animation_sequence_state()

            # Reset texture to 0 if sequence ended
            if self.cur_texture > (len(self.animation_textures) - 1):
                self.cur_texture = 0

        elif self.type == 2:
            self.frame_count += 1
            if self.frame_count % self.animation_frames_per_transition == 0:
                self.cur_texture += 1
            if self.cur_texture > 9:
                self.cur_texture = 0
        elif self.type == 3:
            if self.cur_texture > 3:
                self.cur_texture = 0
        elif self.type == 4:
            if self.cur_texture > 3:
                self.cur_texture = 0
        elif self.type == 5:
            if self.cur_texture > 3:
                self.cur_texture = 0
        elif self.type == 6:
            if self.cur_texture > 3:
                self.cur_texture = 0

        self.set_hit_box(self.texture.hit_box_points)
        self.texture = self.animation_textures[self.cur_texture]


class Powerup(arcade.Sprite):

    def __init__(self, file_name, scale):
        super().__init__(file_name, scale)

        self.type = 0
        self.decreasing_alpha = True

    def update(self):
        if self.type == 1:
            self.center_x += -Globals.GLOBAL_SCROLL_SPEED
            self.change_y = 0
        if self.type == 2:
            self.center_x += -Globals.GLOBAL_SCROLL_SPEED
            self.change_y = 0
        if self.type == 3:
            self.center_x += -Globals.GLOBAL_SCROLL_SPEED
            self.change_y = 0
        if self.type == 4:
            self.center_x += -Globals.GLOBAL_SCROLL_SPEED
            self.change_y = 0
        if self.type == 5:
            self.center_x += -Globals.GLOBAL_SCROLL_SPEED
            self.change_6 = 0

        self.handle_blinking()

    def handle_blinking(self):
        max_alpha = 255
        min_alpha = 150
        blink_rate = 10
        if self.decreasing_alpha:
            self.alpha = np.maximum(self.alpha - blink_rate, min_alpha)
            if self.alpha <= min_alpha:
                self.alpha = min_alpha
                self.decreasing_alpha = False
        else:
            self.alpha = np.minimum(self.alpha + blink_rate, max_alpha)
            if self.alpha >= max_alpha:
                self.alpha = max_alpha
                self.decreasing_alpha = True


class PowerupEnabled(arcade.Sprite):

    def __init__(self, file_name, scale):
        super().__init__(file_name, scale)

        self.type = 0
        self.decreasing_alpha = True

    def update(self):
        if self.type == 1:
            self.center_x += -Globals.GLOBAL_SCROLL_SPEED
            self.change_y = 0
        if self.type == 2:
            self.center_x += -Globals.GLOBAL_SCROLL_SPEED
            self.change_y = 0
        if self.type == 3:
            self.center_x += -Globals.GLOBAL_SCROLL_SPEED
            self.change_y = 0
        if self.type == 4:
            self.center_x += -Globals.GLOBAL_SCROLL_SPEED
            self.change_y = 0
        if self.type == 5:
            self.center_x += -Globals.GLOBAL_SCROLL_SPEED
            self.change_y = 0

        self.handle_blinking()

    def handle_blinking(self):
        max_alpha = 255
        min_alpha = 100
        blink_rate = 10
        if self.decreasing_alpha:
            self.alpha = np.maximum(self.alpha - blink_rate, min_alpha)
            if self.alpha <= min_alpha:
                self.alpha = min_alpha
                self.decreasing_alpha = False
        else:
            self.alpha = np.minimum(self.alpha + blink_rate, max_alpha)
            if self.alpha >= max_alpha:
                self.alpha = max_alpha
                self.decreasing_alpha = True


class AchievementDropdown(arcade.Sprite):

    def __init__(self, file_name, scale, *args):
        super().__init__(file_name, scale)

        self.time = 0.0

        self.center_x = SCREEN_WIDTH / 2
        self.center_y = SCREEN_HEIGHT + self.height / 2
        self.final_y = SCREEN_HEIGHT - self.height - SCREEN_BORDER_PADDING
        self.delta_y = self.center_y - self.final_y
        self.time_to_reach_bottom = 2.0
        self.time_to_pause_end = 4.0
        self.time_to_reach_top = 6.0

        self.finished = False

        if len(args) > 0:
            self.center_y = args[0]
            self.final_y = self.center_y - self.delta_y

    def update(self):
        # Move achievement down, pause, then up
        if self.time < self.time_to_reach_bottom:
            self.center_y -= (self.center_y - self.final_y) / (self.time_to_reach_bottom * 60)
        elif self.time_to_reach_bottom < self.time < self.time_to_pause_end:
            pass
        elif self.time > self.time_to_pause_end:
            self.center_y += (self.center_y - self.final_y) / (self.time_to_reach_bottom * 60)
        elif self.time > self.time_to_reach_top:
            self.finished = True

        self.time += 1.0 / 60.0


class GameView(arcade.View):

    def __init__(self):
        super().__init__()
        self.init_vars()
        self.init_UI()
        self.init_sprites()

    def on_show(self):
        arcade.set_background_color(arcade.color.WHITE)

    def init_vars(self):
        self.score = 0
        self.distance = 0
        self.time = 0

        self.keyup_pressed = False
        self.keydown_pressed = False
        self.keyright_pressed = False
        self.keyleft_pressed = False
        self.key1_pressed = False
        self.key2_pressed = False
        self.key3_pressed = False
        self.key4_pressed = False
        self.key5_pressed = False

        self.single_jumped = False
        self.double_jumped = False

        self.powerup_spawns_enabled_list = [False for i in range(NUM_POWERUPS_PERMANENT)]
        self.powerups_permanent_scores = NEW_POWERUPS_SPAWN_VALUES
        self.new_object_spawn_values = NEW_OBJECT_SPAWN_VALUES

    def init_UI(self):
        arcade.set_background_color(arcade.color.WHITE)
        self.game_background = SpriteCache.BACKGROUND_GAME
        self.game_background.center_x = self.game_background.width / 2 + Globals.GLOBAL_SCROLL_SPEED
        self.game_background.center_y = SCREEN_HEIGHT / 2
        self.game_background.change_x = -Globals.GLOBAL_SCROLL_SPEED

    def init_sprites(self):
        self.player_sprite_path = os.path.join(SPRITES_PATH, 'coronavirus-classic-idle1_00.png')
        self.player = Player(self.player_sprite_path, SPRITE_SCALING)
        self.player.center_x = SCREEN_BORDER_PADDING * 4
        self.player.center_y = SCREEN_HEIGHT / 3.4

        self.obstacle_initial_textures = [SpriteCache.SPRITELIST_COWBOY_RUN[0],
                                          SpriteCache.SPRITELIST_NINJA_RUN[0],
                                          SpriteCache.SPRITELIST_NINJA_RUN[0],
                                          SpriteCache.SPRITELIST_NINJA_RUN[0],
                                          SpriteCache.SPRITELIST_NINJA_RUN[0],
                                          SpriteCache.SPRITELIST_NINJA_RUN[0]]
        self.obstacles_list = arcade.SpriteList()

        powerup_enabled_1_path = os.path.join(SPRITES_PATH, "powerup_enabled_shield.png")
        powerup_enabled_2_path = os.path.join(SPRITES_PATH, "powerup_enabled_double_jump.png")
        powerup_enabled_3_path = os.path.join(SPRITES_PATH, "powerup_enabled_slime_blast.png")
        powerup_enabled_4_path = os.path.join(SPRITES_PATH, "powerup_enabled_shockwave.png")
        powerup_enabled_5_path = os.path.join(SPRITES_PATH, "powerup_enabled_time_warp.png")
        self.powerup_enabled_sprite_list = arcade.SpriteList()
        self.powerup_enabled_path_list = []
        self.powerup_enabled_path_list.extend([powerup_enabled_1_path, powerup_enabled_2_path, powerup_enabled_3_path,
                                               powerup_enabled_4_path, powerup_enabled_5_path])

        powerup_holder_path = os.path.join(SPRITES_PATH, 'PowerupHolder.png')
        powerup_holder = arcade.Sprite(powerup_holder_path, SPRITE_SCALING)
        self.powerup_bar_lengths = [POWERUP_BAR_LENGTH for i in range(NUM_POWERUPS_PERMANENT)]
        self.powerup_holder_list = arcade.SpriteList()
        self.powerup_bar_colors = [arcade.color.PURPLE, arcade.color.BLUE, arcade.color.RED, arcade.color.GREEN,
                                   arcade.color.YELLOW]
        self.powerup_positions_y = [SCREEN_HEIGHT - SCREEN_BORDER_PADDING * 2 - i * powerup_holder.height * 2
                                    for i in range(NUM_POWERUPS_PERMANENT)]
        for i in range(NUM_POWERUPS_PERMANENT):
            powerup_holder = arcade.Sprite(powerup_holder_path, SPRITE_SCALING)
            powerup_holder.center_x = SCREEN_BORDER_PADDING + POWERUP_BAR_LENGTH / 2
            powerup_holder.center_y = self.powerup_positions_y[i]
            self.powerup_holder_list.append(powerup_holder)

        powerup_shield_path = os.path.join(SPRITES_PATH, "powerup_shield.png")
        powerup_double_jump_path = os.path.join(SPRITES_PATH, "powerup_double_jump.png")
        powerup_slime_blast_path = os.path.join(SPRITES_PATH, "powerup_slime_blast.png")
        powerup_shockwave_path = os.path.join(SPRITES_PATH, "powerup_shockwave.png")
        powerup_time_warp_path = os.path.join(SPRITES_PATH, "powerup_time_warp.png")
        self.powerup_sprite_path_list = []
        self.powerup_sprite_path_list.extend([powerup_shield_path, powerup_double_jump_path, powerup_slime_blast_path,
                                              powerup_shockwave_path, powerup_time_warp_path])

        self.powerup_sprite_list = arcade.SpriteList()
        self.achievement_dropdown_list = arcade.SpriteList()
        self.achievement_dropdown_icon_list = arcade.SpriteList()
        self.achievement_dropdown_text_list = []

    def update(self, dt):
        # Update main sprites
        self.player.update()
        self.player.update_animation(dt)
        if self.game_background.center_x < 0:
            self.game_background.center_x += self.game_background.width / 2 * RESOLUTION_SCALING
        for obstacle in self.obstacles_list:
            if obstacle.center_x < -obstacle.width * 2:
                obstacle.remove_from_sprite_lists()
            obstacle.update()
            obstacle.update_animation(dt)

        # Update powerup collectibles
        for powerup_bar in self.powerup_holder_list:
            powerup_bar.update()
        for powerup in self.powerup_sprite_list:
            if powerup.center_x < -powerup.width * 2:
                powerup.remove_from_sprite_lists()
            powerup.update()
        for powerup_enabled in self.powerup_enabled_sprite_list:
            if powerup_enabled.center_x < -powerup_enabled.width * 2:
                powerup_enabled.remove_from_sprite_lists()
            powerup_enabled.update()

        # Update powerup sprites
        for shockwave in self.player.shockwave_sprite_list:
            shockwave.update()
        for time_warp in self.player.time_warp_sprite_list:
            time_warp.update()
        for timer_hand in self.player.timer_hand_sprite_list:
            timer_hand.angle = self.player.timer_hand_rotation
            timer_hand.update()

        # Update achievements
        for achievement_dropdown in self.achievement_dropdown_list:
            if achievement_dropdown.finished:
                achievement_dropdown.remove_from_sprite_lists()
            else:
                achievement_dropdown.update()
        i = 0
        for achievement_icon in self.achievement_dropdown_icon_list:
            if len(self.achievement_dropdown_list) == 0:
                achievement_icon.remove_from_sprite_lists()
            else:
                achievement_icon.center_x = self.achievement_dropdown_list[i].center_x
                achievement_icon.center_y = self.achievement_dropdown_list[i].center_y - \
                                            self.achievement_dropdown_list[i].height / 5
                achievement_icon.update()
            i += 1
        i = 0
        for text_label in self.achievement_dropdown_text_list:
            if len(self.achievement_dropdown_list) == 0:
                self.achievement_dropdown_text_list.clear()
            else:
                text_label.x = self.achievement_dropdown_list[i].center_x
                text_label.y = self.achievement_dropdown_list[i].center_y + \
                               self.achievement_dropdown_list[i].height / 5
            i += 1

        self.game_background.update()
        self.game_background.change_x = -Globals.GLOBAL_SCROLL_SPEED

        # Game logic
        for i in range(len(self.obstacle_initial_textures)):
            obstacle_generator = np.random.randint(0, 20000)
            if ((self.time > self.new_object_spawn_values[i]) and
                    (obstacle_generator - self.time) < 100):
                obstacle = Obstacle(None, SPRITE_SCALING)
                obstacle.type = i + 1
                obstacle.texture = self.obstacle_initial_textures[i]
                obstacle.center_x = SCREEN_WIDTH + obstacle.width * 2
                obstacle.center_y = GROUND_LEVEL
                obstacle.change_x = -Globals.GLOBAL_SCROLL_SPEED
                obstacle.init_animation_textures()
                self.obstacles_list.append(obstacle)

        for i in range(len(self.powerups_permanent_scores)):
            if self.time > self.powerups_permanent_scores[i]:
                self.powerup_spawns_enabled_list[i] = True
            else:
                break

        # Powerup bar lengths
        for i in range(NUM_POWERUPS_PERMANENT):
            bar_length_temp = (POWERUP_BAR_LENGTH *
                               (self.player.powerup_time_since_used[i] / self.player.powerup_recharge_time_list[i]))
            bar_length = np.minimum(bar_length_temp, POWERUP_BAR_LENGTH)
            self.powerup_bar_lengths[i] = bar_length

        # Spawn powerups
        for i in range(NUM_POWERUPS_PERMANENT):
            # Generate powerup enabled sprites
            powerup_enabled_generator = np.random.randint(0, 7200)
            if ((self.time > self.powerups_permanent_scores[i]) and (powerup_enabled_generator < 60) and
                    self.player.powerups_enabled_list[i] is False):
                powerup_enabled_sprite = PowerupEnabled(self.powerup_enabled_path_list[i], SPRITE_SCALING)
                powerup_enabled_sprite.center_x = SCREEN_WIDTH + powerup_enabled_sprite.width * 2
                powerup_enabled_sprite.center_y = GROUND_LEVEL
                powerup_enabled_sprite.change_x = -SCROLL_SPEED
                powerup_enabled_sprite.type = i + 1
                self.powerup_enabled_sprite_list.append(powerup_enabled_sprite)

            # Gemerate powerup upgrades
            powerup_generator = np.random.randint(0, 7200)
            if ((self.time > self.new_object_spawn_values[i]) and
                    (powerup_generator < 60) and
                    (self.player.powerup_level_list[i] < POWERUP_MAX_LEVEL) and
                    (self.player.powerups_enabled_list[i])):
                powerup = Powerup(self.powerup_sprite_path_list[i], SPRITE_SCALING)
                powerup.type = i + 1
                powerup.center_x = SCREEN_WIDTH + powerup.width * 2
                powerup.center_y = GROUND_LEVEL
                powerup.change_x = -Globals.GLOBAL_SCROLL_SPEED
                self.powerup_sprite_list.append(powerup)

        # Check for collisions
        for shield in self.player.shield_list:
            collisions = arcade.check_for_collision_with_list(shield, self.obstacles_list)
            for obstacle in collisions:
                if obstacle.dead is False:
                    self.player.shield_hit = True
                    obstacle.dead = True
        for slime_blast in self.player.slime_blast_sprite_list:
            collisions = arcade.check_for_collision_with_list(slime_blast, self.obstacles_list)
            for obstacle in collisions:
                if obstacle.dead is False:
                    obstacle.dead = True
                    self.score += 10
        for shockwave in self.player.shockwave_sprite_list:
            collisions = arcade.check_for_collision_with_list(shockwave, self.obstacles_list)
            for obstacle in collisions:
                if obstacle.dead is False:
                    obstacle.dead = True
                    self.score += 10

        powerup_hit_list = arcade.check_for_collision_with_list(self.player, self.powerup_sprite_list)
        for powerup in powerup_hit_list:
            next_level = self.player.powerup_level_list[powerup.type - 1] + 1
            self.player.powerup_level_list[powerup.type - 1] = np.minimum(next_level, POWERUP_MAX_LEVEL)
            self.player.powerup_recharge_time_list[powerup.type - 1] = (POWERUP_RECHARGE_TIMES[powerup.type - 1] *
                                                                        (1 - (self.player.powerup_level_list[
                                                                                  powerup.type - 1] / (
                                                                                          2 * POWERUP_MAX_LEVEL))))
            powerup.remove_from_sprite_lists()

        powerup_enabled_hit_list = arcade.check_for_collision_with_list(self.player, self.powerup_enabled_sprite_list)
        for powerup_enabled in powerup_enabled_hit_list:
            self.player.powerups_enabled_list[powerup_enabled.type - 1] = True
            powerup_enabled.remove_from_sprite_lists()
            powerup_enabled.update()

        for i in range(len(ACHIEVEMENT_SCORES)):
            if self.score > ACHIEVEMENT_SCORES[i] and not GameData.data['achievements_complete'][i]:
                path = os.path.join(SPRITES_PATH, 'achievement_dropdown.png')
                path_icon = os.path.join(SPRITES_PATH, 'achievement_icon_' + str(i + 1) + '.png')
                achievement_dropdown = AchievementDropdown(path, SPRITE_SCALING)
                achievement_icon = arcade.Sprite(path_icon, SPRITE_SCALING)
                achievement_icon.center_x = achievement_dropdown.center_x
                achievement_icon.center_y = achievement_dropdown.center_y + achievement_dropdown.height / 5
                text_label = arcade.gui.TextLabel(ACHIEVEMENT_NAMES[i], achievement_dropdown.center_x,
                                                  achievement_dropdown.center_y - achievement_dropdown.height / 5,
                                                  arcade.color.BLACK, font_size=20)
                self.achievement_dropdown_list.append(achievement_dropdown)
                self.achievement_dropdown_icon_list.append(achievement_icon)
                self.achievement_dropdown_text_list.append(text_label)
                GameData.data['achievements_complete'][i] = True
                GameData.save_data()
        for i in range(len(ACHIEVEMENT_DISTANCES)):
            if self.distance > ACHIEVEMENT_DISTANCES[i] and not GameData.data['achievements_complete'][i + 4]:
                GameData.data['achievements_complete'][i + 4] = True
                GameData.save_data()

        object_hit_list = arcade.check_for_collision_with_list(self.player, self.obstacles_list)
        for object in object_hit_list:
            if obstacle.dead is False:
                self.player.health -= 1
                if self.player.health <= 0:
                    self.init_game_over()

        self.time += dt
        self.distance += dt * 60
        self.score += dt * 60

    def on_draw(self):
        # Draw Sprites
        arcade.start_render()
        self.game_background.draw()
        self.player.draw()
        for shield in self.player.shield_list:
            shield.draw()
        for slime_blast in self.player.slime_blast_sprite_list:
            slime_blast.draw()
        for shockwave in self.player.shockwave_sprite_list:
            shockwave.draw()
        for time_warp in self.player.time_warp_sprite_list:
            time_warp.draw()
        for timer_hand in self.player.timer_hand_sprite_list:
            timer_hand.draw()
            timer_hand.angle = self.player.timer_hand_rotation
        for achievement_dropdown in self.achievement_dropdown_list:
            achievement_dropdown.draw()
        for achievement_icon in self.achievement_dropdown_icon_list:
            achievement_icon.draw()
        for text_label in self.achievement_dropdown_text_list:
            text_label.draw()
        for obstacle in self.obstacles_list:
            obstacle.draw()
            obstacle.draw_hit_box()

        # Powerup bars
        for i in range(NUM_POWERUPS_PERMANENT):
            # Draw powerup bars
            if self.player.powerups_enabled_list[i]:
                arcade.draw_rectangle_filled(SCREEN_BORDER_PADDING + self.powerup_bar_lengths[i] / 2,
                                             self.powerup_positions_y[i],
                                             self.powerup_bar_lengths[i], POWERUP_BAR_HEIGHT,
                                             self.powerup_bar_colors[i])
                # Draw powerup level bars
                for j in range(self.player.powerup_level_list[i]):
                    pos_x = (self.powerup_holder_list[
                                 i].left + POWERUP_LEVEL_BAR_WIDTH / 2 + POWERUP_LEVEL_BAR_X_BUFFER +
                             (POWERUP_LEVEL_BAR_WIDTH + POWERUP_LEVEL_BAR_GAP) * j)
                    pos_y = self.powerup_holder_list[i].bottom - POWERUP_LEVEL_BAR_Y_BUFFER
                    arcade.draw_rectangle_filled(pos_x, pos_y, POWERUP_LEVEL_BAR_WIDTH, POWERUP_LEVEL_BAR_HEIGHT,
                                                 self.powerup_bar_colors[i])
            else:
                arcade.draw_rectangle_filled(SCREEN_BORDER_PADDING + POWERUP_BAR_LENGTH / 2,
                                             self.powerup_positions_y[i],
                                             POWERUP_BAR_LENGTH, POWERUP_BAR_HEIGHT,
                                             (100, 100, 100, 100))

        for powerup_bar in self.powerup_holder_list:
            powerup_bar.draw()
        for powerup in self.powerup_sprite_list:
            powerup.draw()
        for powerup_enabled in self.powerup_enabled_sprite_list:
            powerup_enabled.draw()

        # Draw UI
        self.scoretext_str = 'Score: ' + str(int(np.floor(self.score)))
        self.scoretext = arcade.draw_text(self.scoretext_str, SCREEN_WIDTH - SCREEN_BORDER_PADDING,
                                          SCREEN_HEIGHT - SCREEN_BORDER_PADDING * 2, arcade.color.BLACK,
                                          align="left", anchor_x="right", bold=True, font_size=22)

    def init_game_over(self):
        if GameData.data['username'] is None:
            submit_highscore_view = SubmitHighscore.SubmitHighscoresView(self.score)
            self.window.show_view(submit_highscore_view)
        else:
            game_over_view = GameOver.GameOverView(self.score)
            self.window.show_view(game_over_view)

    def on_key_press(self, key, modifiers):
        if key == arcade.key.UP:
            self.keyup_pressed = True
            self.player.jump_pressed = True
            self.player.double_jump_pressed = True
            self.player.jump_key_down = True
            self.player.double_jump_key_down = True
        elif key == arcade.key.DOWN:
            self.keydown_pressed = True
        elif key == arcade.key.LEFT:
            self.player.change_x = -(MOVEMENT_SPEED + Globals.GLOBAL_SCROLL_SPEED)
            self.keyleft_pressed = True
        elif key == arcade.key.RIGHT:
            self.player.change_x = MOVEMENT_SPEED
            self.keyright_pressed = True
        elif key == arcade.key.KEY_1:
            self.player.shield_pressed = True
            self.player.shield_key_down = True
            self.key1_pressed = True
        elif key == arcade.key.KEY_2:
            self.player.double_jump_pressed = True
            self.player.double_jump_key_down = True
            self.key2_pressed = True
        elif key == arcade.key.KEY_3:
            self.player.slime_blast_pressed = True
            self.player.slime_blast_key_down = True
            self.key3_pressed = True
        elif key == arcade.key.KEY_4:
            self.player.shockwave_pressed = True
            self.player.shockwave_key_down = True
            self.key4_pressed = True
        elif key == arcade.key.KEY_5:
            self.player.time_warp_pressed = True
            self.player.time_warp_key_down = True
            self.key5_pressed = True

        # Pause Menu
        if key == arcade.key.ESCAPE:
            pause = Pause.PauseView(self)
            self.window.show_view(pause)

    def on_key_release(self, key, modifiers):
        if key == arcade.key.UP:
            self.player.jump_pressed = False
            self.player.jump_key_down = False
            self.player.double_jump_pressed = False
            self.player.double_jump_key_down = False
            self.keyup_pressed = False
        elif key == arcade.key.DOWN:
            self.player.change_y = 0
            self.keydown_pressed = False
        elif key == arcade.key.LEFT:
            self.player.change_x = 0
            self.keyleft_pressed = False
        elif key == arcade.key.RIGHT:
            self.player.change_x = 0
            self.keyright_pressed = False
        elif key == arcade.key.KEY_1:
            self.player.shield_pressed = False
            self.player.shield_key_down = False
            self.key1_pressed = False
        elif key == arcade.key.KEY_2:
            self.player.jump_pressed = False
            self.player.jump_key_down = False
            self.player.double_jump_pressed = False
            self.player.double_jump_key_down = False
            self.key2_pressed = False
        elif key == arcade.key.KEY_3:
            self.player.slime_blast_pressed = False
            self.player.slime_blast_key_down = False
            self.key3_pressed = False
        elif key == arcade.key.KEY_4:
            self.player.shockwave_pressed = False
            self.player.shockwave_key_down = False
            self.key4_pressed = False
        elif key == arcade.key.KEY_5:
            self.player.time_warp_pressed = False
            self.player.time_warp_key_down = False
            self.key5_pressed = False

        # Extra logic for holding down keys
        if self.keyup_pressed:
            self.player.jump_key_down = True
            self.player.double_jump_key_down = True
        if self.keydown_pressed:
            pass
        if self.keyleft_pressed:
            self.player.change_x = -MOVEMENT_SPEED
        if self.keyright_pressed:
            self.player.change_x = MOVEMENT_SPEED
        if self.key1_pressed:
            self.player.shield_key_down = True
        if self.key2_pressed:
            self.player.double_jump_key_down = True
        if self.key3_pressed:
            self.player.slime_blast_key_down = True
        if self.key4_pressed:
            self.player.shockwave_key_down = True
        if self.key5_pressed:
            self.player.time_warp_key_down = True
