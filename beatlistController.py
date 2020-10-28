"""
Controller for the handling of the extract, data and display.

The Controller Class handle all calls for extraction, data saving, analysing, etc. The controller handle the SpotifyAPI, datamanager objetcs and the
trackanalyser module.

"""

import spotifyAPI
import datamanager
import tracksanalyser
import os
import unicodedata


def clear_interpreter():
    os.system('cls' if os.name == 'nt' else 'clear')


def menu_generator(header="", menu_list=None, exit_choice=False):
    if menu_list is None:
        return -1

    choice = 0
    while choice <= 0 or choice > len(menu_list) + 1 + int(exit_choice):
        print("\n" + Color.YELLOW + header + Color.END)
        i = 0
        for item in menu_list:
            to_print = (str(i + 1) + ") " + item)

            print(to_print)
            i = i + 1
        if exit_choice:
            print(str(i + 1) + ") Exit")
        try:
            choice = int(input("\nChoice: "))
        except ValueError:
            choice = 0
            clear_interpreter()
    return choice


def strip_accents(text):
    try:
        text.encode('utf-8')
    except NameError:  # unicode is a default on python 3
        pass

    text = unicodedata.normalize('NFD', text) \
        .encode('ascii', 'ignore') \
        .decode("utf-8")

    return str(text)


class Color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


class Controller(object):
    # Variables.
    data_manager = None
    table_name_list = None
    spotify_API = None
    songs_analyser = None
    client_ID = None
    client_secret = None
    user_ID = ''
    access_token = None
    refresh_token = None
    expires = None
    connect = None
    tracks_data = list()
    output_data = None
    output_track_IDs = None
    playlist_ID = None
    parameter_list = None

    debug = 0

    # Constructor
    def __init__(self):
        self.data_manager = datamanager.DataManager()
        self.connect = False

    # Methods
    def get_credentials(self):  # look for credentials and ask for them.
        if not self.data_manager.is_client_info_exist():
            print("No client_ID and client_Secret found. Please provide the required credentials to continue.")
            self.client_ID = input("Client_ID: ")
            self.client_secret = input("Client_Secret: ")
            self.data_manager.save_line_info('1', 0)  # v1) 1 for client info in file. Should have some way to verify if info are reliable.
            self.data_manager.save_client_info_to_file(self.client_ID, self.client_secret)
        else:
            choice = ''
            self.client_ID, self.client_secret = self.data_manager.extract_client_info_from_file()
            menu_list = ['Yes', 'No']
            header = 'Client ID and secret seems to exist, do you want to use those? (Y/N) : '
            while choice != 1 and choice != 2:

                print("Client_ID: " + self.client_ID)
                print("Client_Secret: " + self.client_secret)
                choice = menu_generator(header=header, menu_list=menu_list, exit_choice=False)
                if choice == 2:
                    clear_interpreter()
                    print("Choose new client_ID and client_Secret")
                    self.client_ID = input("Client_ID: ")
                    self.client_secret = input("Client_Secret: ")
                    self.data_manager.save_client_info_to_file(self.client_ID, self.client_secret)
                    self.data_manager.save_authentification_to_file('0')

    def get_authentification(self):  # looks for authentification key and ask for it if not found.
        client_id = self.client_ID
        client_secret = self.client_secret
        if client_id is not None and client_secret is not None:
            self.spotify_API = spotifyAPI.SpotifyAPI(client_id, client_secret)  # spotifyAPI class to handle all POST and GET request to the API.
            if not self.data_manager.is_auth_granted():
                clear_interpreter()
                self.spotify_API.request_auth()
                [request_success, access_token, refresh_token] = self.spotify_API.extract_access_token()
                if request_success:
                    self.data_manager.save_line_info('1', 3)
                    self.data_manager.save_tokens_to_file(access_token, refresh_token)
                    self.connect = True
                    return True
                else:
                    print("Authentification not successful.")
                    self.connect = False
                    return False

            elif self.spotify_API.is_expire:  # Verify if the access token is still valid, if not, do a request to have a new one.
                is_Request_Successful = self.request_refresh()
                self.connect = True
                return is_Request_Successful

    def request_refresh(self):
        refresh_token = self.data_manager.extract_line_info(5)
        self.spotify_API.set_refresh_token(refresh_token)
        access_token = self.spotify_API.refresh()
        if access_token is not None:
            self.data_manager.save_line_info(access_token, 4)
            return True
        else:
            return False

    def extract_user_id(self):
        self.user_ID = self.spotify_API.extract_current_user_id()
        print("User ID: " + self.user_ID)

    def create_the_spotify_playlist(self):
        playlist_name = input("\nEnter the playlist name: ")
        self.playlist_ID = self.spotify_API.create_a_playlist(playlist_name)
        print(self.playlist_ID)

    def extract_data_from_source(self):

        # The local tracks SQL database is to gain time if the data have already been extracted.
        header = 'Do you want to extract from the local database or extract from Spotify?'
        menu_list = ['Local Database',
                     'Spotify Personnal Playlist',
                     'Spotify Liked Songs',
                     'Spotify Saved Albums'
                     ]

        data_source_choice = 0
        while 1 > data_source_choice or data_source_choice > len(menu_list) + 1:
            data_source_choice = menu_generator(header=header, menu_list=menu_list, exit_choice=True)

            if data_source_choice == 1:  # Tracks data extraction from local SQL database.
                self.tracks_data = self.extract_data_from_local_database()
                self.parameter_list = tracksanalyser.extract_parameter_list(self.tracks_data)

            elif data_source_choice == 2:  # Tracks data extraction from API request.
                spotify_source_type = "playlist"

                try:
                    playlist_name, self.tracks_data = self.extract_data_from_spotify(spotify_source_type)
                    self.parameter_list = tracksanalyser.extract_parameter_list(self.tracks_data)
                except TypeError:
                    self.tracks_data = list()
                    return False
                else:
                    choice = ""

                while choice.upper() != 'Y' and choice.upper() != 'N':  # Choice to replace the local SQL database with new data.
                    clear_interpreter()
                    choice = input("\nDo you want to save the data in the local database? (Y/N): ")
                if choice.upper() == 'Y':
                    table = 'playlist_' + strip_accents(playlist_name.replace(" ", "_").replace("-", "_"))
                    self.save_data_to_local_database(table, self.tracks_data)

            elif data_source_choice == 3:
                spotify_source_type = "liked_tracks"
                self.tracks_data = self.extract_data_from_spotify(spotify_source_type)
                choice = ""
                while choice.upper() != 'Y' and choice.upper() != 'N':  # Choice to replace the local SQL database with new data.
                    clear_interpreter()
                    choice = input("\nDo you want to save the data in the local database? (Y/N): ")
                if choice.upper() == 'Y':
                    table = 'liked_tracks'
                    self.save_data_to_local_database(table, self.tracks_data)

            elif data_source_choice == 4:
                spotify_source_type = "saved_albums"
                self.tracks_data = self.extract_data_from_spotify(spotify_source_type)
                choice = ""
                while choice.upper() != 'Y' and choice.upper() != 'N':  # Choice to replace the local SQL database with new data.
                    clear_interpreter()
                    choice = input("\nDo you want to save the data in the local database? (Y/N): ")
                if choice.upper() == 'Y':
                    table = 'saved_albums'
                    self.save_data_to_local_database(table, self.tracks_data)

            elif data_source_choice == len(menu_list) + 1:
                self.tracks_data = None

        return True

    def extract_data_from_spotify(self, spotify_source_type):
        spotify_source_type = spotify_source_type
        if spotify_source_type == 'playlist':
            playlist_info = self.spotify_API.extract_list_of_user_playlist()
            playlist_name = [info[0] for info in playlist_info]
            playlist_id = [info[1] for info in playlist_info]

            choice = 0
            while 1 > choice or choice > len(playlist_name) + 1:
                choice = menu_generator(header='From which playlist?', menu_list=playlist_name, exit_choice=True)

            if choice <= len(playlist_name):
                track_IDs_list = self.spotify_API.extract_tracks_IDs_from_playlist(playlist_id[choice - 1])
                tracks_data = self.spotify_API.extract_tracks_data(track_IDs_list)
                return playlist_name[choice - 1], tracks_data

        elif spotify_source_type == 'liked_tracks':
            track_IDs = self.spotify_API.extract_saved_tracks_IDs()
            tracks_data = self.spotify_API.extract_tracks_data(track_IDs)
            return tracks_data

        elif spotify_source_type == 'saved_albums':
            album_counter = 0
            album_counts = 50
            offset = 0
            album_IDs_list = list()
            while album_counts == 50:
                album_IDs_buff = self.spotify_API.extract_library_albums_IDs(offset=offset)
                album_counts = len(album_IDs_buff)
                album_counter = album_counter + album_counts
                offset = offset + album_counts
                album_IDs_list = album_IDs_list + album_IDs_buff
            print("\nNumber of album extracted: " + str(album_counter))
            track_IDs = self.spotify_API.extract_tracks_IDs_from_album(album_IDs_list)
            tracks_data = self.spotify_API.extract_tracks_data(track_IDs)
            return tracks_data
        else:
            return None

    def extract_data_from_local_database(self):
        self.data_manager.connect_to_database()
        table_name = self.data_manager.extract_all_table_name()
        choice = menu_generator(header='Which table?', menu_list=table_name)
        tracks_data = self.data_manager.read_all_tracks_data_table(table_name[choice - 1])
        self.data_manager.close_database()
        return tracks_data

    def save_data_to_local_database(self, table, data):
        self.data_manager.connect_to_database()

        if self.data_manager.is_table_exist(table):
            header = '\nThe table: ' + table + ' exist. Do you want to flush the old data and replace it with new data?'
            choice = menu_generator(header=header, menu_list=['Yes', 'No'])
            if choice == 1:
                self.data_manager.clear_all_data_from_table(table)
                self.data_manager.write_tracks_data_to_table(table, data)
        else:
            self.data_manager.write_tracks_data_to_table(table, data)

        self.data_manager.close_database()

    def delete_table_from_local_database(self):
        self.data_manager.connect_to_database()
        table_name = self.data_manager.extract_all_table_name()
        menu_list = table_name
        choice_header = 'Which table do you want to delete?'
        choice = 0
        while 1 > choice or choice > len(menu_list) + 1:
            choice = menu_generator(header=choice_header, menu_list=menu_list, exit_choice=True)
            if 0 < choice <= len(table_name):
                choice_confirm_header = 'Are you sure you want to delete the table ' + table_name[choice - 1] + ' ?'
                menu_list_confirm = ['Yes', 'No']
                choice_confirm = menu_generator(header=choice_confirm_header, menu_list=menu_list_confirm)
                if choice_confirm == 1:
                    if self.data_manager.drop_table(table_name[choice - 1]):
                        print("Table " + table_name[choice - 1] + " have been deleted.")
                    else:
                        print("Table " + table_name[choice - 1] + "have not been deleted.")
            elif choice == len(table_name) + 1:
                return

        self.data_manager.close_database()

    def generate_graph_for_statistic(self):
        tracks_data = self.tracks_data
        if tracks_data is not None:
            tracks_dataframe = tracksanalyser.convert_dataset_to_panda_dataframe(tracks_data)
            parameter = self.parameter_list
            choice = 0
            menu_list = parameter
            header = 'For which parameter do you want to display the boxplot:'
            while 1 > choice or choice > len(self.parameter_list):
                choice = menu_generator(header=header, menu_list=menu_list, exit_choice=False)
            tracksanalyser.generate_histogram_for_stat(tracks_dataframe, parameter[choice - 1])
        else:
            print("There is no data to plot.")

    def extract_tracks_based_on_tempo(self):
        tracks_data = self.tracks_data

        if tracks_data:
            print("\nThe program will now sort the songs with the requested tempo (±10%): ")
            tempo = input("Which tempo do you want: ")
            tracks_data = self.tracks_data

            # Sort tracks with the requested tempo.
            output_tracks = tracksanalyser.extract_track_by_parameter_and_value(tracks_data, 'tempo', float(tempo), 0.1)
            self.output_track_IDs = tracksanalyser.extract_tracks_URI_IDs(output_tracks)
        else:
            print("No track data.")

    def analyse_tracks_data(self):
        tracks_data = self.tracks_data
        if tracks_data is not None:
            self.output_data = tracksanalyser.extract_stats_from_tracks(tracks_data)
            print("\nMean: ")
            print(self.output_data[0])
            print("\nStDev: ")
            print(self.output_data[1])
        else:
            print("There is no data to analyse")

    def add_tracks_to_playlist(self):
        if self.playlist_ID:
            if self.spotify_API.is_user_playlist_ID_exist(self.playlist_ID):
                result = self.spotify_API.add_tracks_to_a_playlist(self.playlist_ID, self.output_track_IDs)
                if result:
                    print("\nPlaylist generated successfully")
                else:
                    print("\nPlaylist name exist but tracks have not been add to the playlist...")
            else:
                print("\nPlaylist name don't not created...")
        else:
            print('You need to define a playlist name first.')
