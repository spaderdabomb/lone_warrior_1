import math
import os

RESOLUTION_SCALING = 0.5
SCREEN_WIDTH = 1920*RESOLUTION_SCALING
SCREEN_HEIGHT = 1080*RESOLUTION_SCALING
SCREEN_BORDER_PADDING = 10*RESOLUTION_SCALING
FRAME_RATE = 60
SCREEN_TITLE = "Lone Warrior"


FILE_PATH = os.getcwd()
SPRITES_PATH = os.path.join(FILE_PATH, 'Assets', 'Sprites')
SPRITESHEETS_PATH = os.path.join(FILE_PATH, 'Assets', 'Spritesheets')
AUDIO_PATH = os.path.join(FILE_PATH, 'Assets', 'Audio')

GROUND_LEVEL = (1080-805)*RESOLUTION_SCALING
GRAVITY = 1

XP_TO_NEXT_LEVEL_LIST = [math.ceil(100 + 200*i + (8*i)**2 + (1.1*i)**3) for i in range(100)]
TIME_TO_HP_BAR_DISAPPEAR = 10
STANDARD_ATTACK_DISTANCE = 100*RESOLUTION_SCALING

# Text sizes
DAMAGE_LABEL_TEXT_SIZE = 16


class Globals():
    '''
    Stores persistent data
    '''

    # Initializes data dictionary keys for saving and loading data

    @staticmethod
    def __init__(game_name):
        pass

