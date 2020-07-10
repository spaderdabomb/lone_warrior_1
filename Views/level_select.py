import arcade
import arcade.gui
import os
import time

from globals import *
from player import Player
from load_sprites import SpriteCache
from Views import game_scene



class LevelSelectView(arcade.View):
    def __init__(self, window: arcade.Window, sound_manager):
        super().__init__()

        self.window = window
        self.sound_manager = sound_manager
        self.game_scene = False

        self.ui_manager = arcade.gui.UIManager(window)
        self.ui_manager.push_handlers(self.on_ui_event)
        self.physics_engine = None

        self.keyup_pressed = False
        self.keydown_pressed = False
        self.keyright_pressed = False
        self.keyleft_pressed = False

        self.up_pressed_on_door = False
        self.door_collision_index = -1

        self.setup()

    def setup(self):
        self.ui_manager.purge_ui_elements()

        # Setup background UI
        arcade.set_background_color(arcade.color.WHITE)
        self.level_select_menu_background = arcade.Sprite(os.path.join(SPRITES_PATH, 'menu_level_select.png'), calculate_hit_box=False)
        self.level_select_menu_background.center_x = SCREEN_WIDTH/2
        self.level_select_menu_background.center_y = SCREEN_HEIGHT/2

        self.door_list = arcade.SpriteList()
        door_1 = arcade.Sprite(os.path.join(SPRITES_PATH, 'level_select_door.png'), calculate_hit_box=False)
        door_2 = arcade.Sprite(os.path.join(SPRITES_PATH, 'level_select_door.png'), calculate_hit_box=False)
        door_3 = arcade.Sprite(os.path.join(SPRITES_PATH, 'level_select_door.png'), calculate_hit_box=False)
        door_4 = arcade.Sprite(os.path.join(SPRITES_PATH, 'level_select_door.png'), calculate_hit_box=False)
        door_5 = arcade.Sprite(os.path.join(SPRITES_PATH, 'level_select_door.png'), calculate_hit_box=False)

        x = 329*RESOLUTION_SCALING
        y = (1080-763)*RESOLUTION_SCALING
        door_1.center_x = x
        door_1.center_y = y

        x = 770*RESOLUTION_SCALING
        spacing = float(1058-770)*RESOLUTION_SCALING

        door_2.center_x = x
        door_2.center_y = y
        door_3.center_x = x + spacing
        door_3.center_y = y
        door_4.center_x = x + spacing*2
        door_4.center_y = y
        door_5.center_x = x + spacing*3
        door_5.center_y = y

        self.door_list.extend([door_1, door_2, door_3, door_4, door_5])

        self.platform_spritelist = arcade.SpriteList(use_spatial_hash=True)
        self.platform_0 = arcade.Sprite(os.path.join(SPRITES_PATH, 'brick_platform_ground.png'), calculate_hit_box=False)
        self.platform_0.center_x = SCREEN_WIDTH / 2
        self.platform_0.center_y = (1080 - 880) * RESOLUTION_SCALING
        self.platform_spritelist.append(self.platform_0)

        # Player
        self.player = Player(os.path.join(SPRITES_PATH, 'main_character_idle.png'), 0.25, self)
        self.player.center_x = 83*RESOLUTION_SCALING
        self.player.center_y = GROUND_LEVEL
        self.physics_engine = arcade.PhysicsEnginePlatformer(self.player, self.platform_spritelist, GRAVITY)

    def on_ui_event(self, event: arcade.gui.UIEvent):
        if event.type == arcade.gui.UIClickable.CLICKED and event.get('ui_element').id == 'settings_button':
            pass
            # start_menu_view = start_menu.StartMenuView()
            # self.window.show_view(start_menu_view)

    def on_draw(self):
        arcade.start_render()
        self.level_select_menu_background.draw()
        self.door_list.draw()
        self.player.draw()

    def on_update(self, dt):
        # Update main sprites
        self.player.update()
        self.player.update_animation(dt)
        self.physics_engine.update()
        self.sound_manager.update()

        for (i, door) in enumerate(self.door_list):
            collision_bool = arcade.check_for_collision(self.player, door)
            if collision_bool:
                self.door_collision_index = i
                break
            else:
                self.door_collision_index = -1

        if (self.keyup_pressed) and (not self.door_collision_index == -1):
            self.go_to_level(self.door_collision_index, 1)

        if (self.keyup_pressed) and (self.physics_engine.can_jump()):
            self.player.handle_jump()


    def go_to_level(self, world_num, level_num):
        self.ui_manager.purge_ui_elements()
        game_scene_view = game_scene.GameSceneView(self.window, self.sound_manager, world_num, level_num)
        self.window.show_view(game_scene_view)


    def on_key_press(self, key, modifiers):
        if key == arcade.key.UP:
            self.player.jump_pressed = True
            self.keyup_pressed = True
        elif key == arcade.key.DOWN:
            self.keydown_pressed = True
        elif key == arcade.key.LEFT:
            self.player.change_x = -self.player.movement_speed
            self.keyleft_pressed = True
        elif key == arcade.key.RIGHT:
            self.player.change_x = self.player.movement_speed
            self.keyright_pressed = True

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

        # Extra logic for holding down keys
        if self.keyup_pressed:
            self.player.jump_key_down = True
        if self.keydown_pressed:
            pass
        if self.keyleft_pressed:
            self.player.change_x = -self.player.movement_speed
        if self.keyright_pressed:
            self.player.change_x = self.player.movement_speed

