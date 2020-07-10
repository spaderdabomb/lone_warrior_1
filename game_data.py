import os
import pickle
import numpy as np

from Utils import py_gjapi

NUM_ACHIEVEMENTS = 8
NUM_SCORES_DISPLAYED = 10
NUM_SCORES_LOGGED = 100

class GameData():
    '''
    Stores persistent data
    '''

    # Initializes data dictionary keys for saving and loading data
    DATA_FILE_PATH = None
    initial_data = {
        'highscore': 0,
        'my_scores': [],
        'alltime_scores': [],
        'achievements_complete': [False for j in range(NUM_ACHIEVEMENTS)],
        'username': None,
        'player_level': 1,
        'player_xp': 0,
        'tutorials_passed': [True for i in range(10)]
    }
    data = initial_data

    @staticmethod
    def __init__(game_name):
        '''
        When GameData class is initialized, it tries to load previous GameData
        '''
        # Create local data folder and files for game
        home = os.path.expanduser('~')
        local_data_path = 'AppData\\Local\\' + game_name
        data_file_name = 'GameData.pickle'
        game_data_path = os.path.join(home, local_data_path)
        file_path = os.path.join(game_data_path, data_file_name)

        # Create local folder
        GameData.DATA_FILE_PATH = file_path
        if not os.path.exists(game_data_path):
            os.makedirs(game_data_path)

        # Load data if file exists, otherwise create initial file
        if os.path.exists(GameData.DATA_FILE_PATH):
            GameData.update_data_dict()
            GameData.load_data()
        else:
            GameData.save_data()

    @staticmethod
    def update_data_dict():
        data = None
        try:
            with open(GameData.DATA_FILE_PATH, 'rb') as f:
                data = pickle.load(f)
                if len(GameData.data.keys()) == len(data.keys()):
                    pass
                else:
                    # Update dictionary before loading
                    GameData.save_data()
        except:
            pass

    @staticmethod
    def save_data():
        '''
        Saves data
        '''
        try:
            with open(GameData.DATA_FILE_PATH, 'wb') as f:
                pickle.dump(GameData.data, f, pickle.HIGHEST_PROTOCOL)
        except:
            pass

    @staticmethod
    def load_data():
        '''
        Loads data
        '''

        data = None
        try:
            with open(GameData.DATA_FILE_PATH, 'rb') as f:
                data = pickle.load(f)
                GameData.data = data
        except:
            pass

        return GameData.data

    @staticmethod
    def clear_data():
        '''
        Resets data back to initial values
        '''
        GameData.data = GameData.initial_data
        GameData.save_data()

    @staticmethod
    def get_key_value(key):
        return GameData.data.get(key)

    @staticmethod
    def set_key_value(key, value):
        GameData.data[key] = value

    @staticmethod
    def sort_highscores():
        my_scores_dict = GameData.data['my_scores']
        num_entries = len(my_scores_dict)

        my_scores_arr = np.zeros(num_entries, dtype=np.int)
        my_scores_usernames_arr = ['' for i in range(num_entries)]
        for i in range(num_entries):
            my_scores_arr[i] = my_scores_dict[i]['score']

        my_scores_indexed_arr = np.argsort(my_scores_arr)[::-1]
        my_scores_arr = np.sort(my_scores_arr)[::-1]
        for i in range(num_entries):
            my_scores_usernames_arr[i] = my_scores_dict[my_scores_indexed_arr[i]]['username']

        return my_scores_arr, my_scores_usernames_arr

    @staticmethod
    def add_highscore_entry(score):
        # Local highscores
        my_scores_dict = GameData.data["my_scores"]
        my_scores_arr, my_scores_usernames_arr = GameData.sort_highscores()

        if len(my_scores_dict) > 0:
            if (min(my_scores_arr) > score) and (len(my_scores_arr) > NUM_SCORES_LOGGED):
                pass
            else:
                username = GameData.data["username"]
                new_dict_entry = {"username": username, "score": score}
                my_scores_dict.append(new_dict_entry)
                GameData.data['my_scores'] = my_scores_dict
        else:
            username = GameData.data["username"]
            new_dict_entry = {"username": username, "score": score}
            my_scores_dict.append(new_dict_entry)
            GameData.data['my_scores'] = my_scores_dict

        # Online highscores
        gamejolt = py_gjapi.GameJoltTrophy(GameData.data['username'], 'token', '484162', '113bbb2d41c5bb3331393e2cdddc7338')
        gamejolt.addScores(str(score), score, table_id=491301, guest=True, guestname=GameData.data["username"])
        gamejolt.addScores(str(score), score, table_id=491315, guest=True, guestname=GameData.data["username"])



    # Debugging
    @staticmethod
    def add_fake_highscores():
        highscore_dict = {"my_scores": [{'username': 'player'+str(i), 'score': np.random.randint(0, 10000)} for i in range(6)]}
        GameData.data["my_scores"] = highscore_dict["my_scores"]
        GameData.save_data()

    @staticmethod
    def complete_all_achievements():
        achievements_dict = GameData.data["achievements_complete"]
        for i in range(NUM_ACHIEVEMENTS):
            achievements_dict[i] = True

        GameData.data['achievements_complete'] = achievements_dict
        GameData.save_data()