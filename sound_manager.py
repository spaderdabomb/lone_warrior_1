import os
import arcade
import time

from globals import *

class SoundManager():
    """ Main application class. """

    def __init__(self, window: arcade.Window):
        super().__init__()

        self.window = window

        # Variables used to manage our music. See setup() for giving them
        # values.
        self.music_list = []
        self.current_song = 0
        self.music = None
        self.sound = None

        self.music_volume = 0.0
        self.sound_volume = 0.50

        self.setup()

    def setup(self):
        # List of music
        self.music_list = [os.path.join(AUDIO_PATH, "main_menu_music.wav")]
        self.sound_list = [os.path.join(AUDIO_PATH, "menu_selection_click.wav")]

        self.current_song = 0
        self.play_song()

    def play_sound(self, index):
        self.sound = arcade.Sound(self.sound_list[index], streaming=True)
        self.sound.play(self.sound_volume)

    def play_song(self):
        # Stop what is currently playing.
        if self.music:
            self.music.stop()

        # Play the next song
        self.music = arcade.Sound(self.music_list[self.current_song], streaming=True)
        self.music.play(self.music_volume)
        time.sleep(0.01)

    def update(self):

        position = self.music.get_stream_position()
        if position == 0.0:
            self.play_song()