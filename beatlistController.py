import spotifyAPI
import datamanager
import tracksanalyser
import os
import unicodedata

"""
Controller for the handling of the extract, data and display.

The Controller Class handle all calls for extraction, data saving, analysing, etc. The controller handle the SpotifyAPI, datamanager objetcs and the 
trackanalyser module.

This module include
==================  =============================================
Function            Description
==================  =============================================
clear_interpreter   Clear the command interpreter for a better lisibility
menu_list           Handle all the list choice to make in the command interpreter. Ask for a list of choice in a list of string. Return a choice number (int)
==================  =============================================

The class Controller include:
==================                  =============================================
Function                            Description
==================                  =============================================
__init__                            Initialise the datamanager object.
get_credentials                     Handle the call to request the user credentials. First step of two for the Spotify API connexion
get_authentification                Handle the call to authentify the user for all Spotify API call. Second step of two for the Spotify API connexion.
request_refresh                     Handle the connexion refresh if the connexion is too old (authentification is good 1 hour).
extract_user_id                     Return the user id from the SpotifyAPI object.
create_the_spotify_playlist         Ask for a playlist name and call the SpotifyAPI object for the Spotify playlist creation.
extract_data_from_source            Ask to choose a data base source and ask for the data extraction
extract_data_from_spotify           Request the data extraction from Spotify based on the user choice. 
extract_data_from_local_database    Request the data extraction from the local database.
==================                  =============================================
"""


def clear_interpreter():
    os.system('cls' if os.name == 'nt' else 'clear')


def menu_list(header="", menu_list=None):
    if menu_list is None:
        menu_list = list()
    choice = 0
    while choice <= 0 or choice > len(menu_list):
        print("\n" + header)
        for i in range(0, len(menu_list)):
            to_print = (str(i+1) + ") " + menu_list[i])
            print(to_print)
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

    text = unicodedata.normalize('NFD', text)\
           .encode('ascii', 'ignore')\
           .decode("utf-8")

    return str(text)


class Controller(object):
    # Variables.
    data_manager = None
    table_name_list = None
    spotify_API = None
    songs_analyser = None
    client_ID = None
    client_secret = None
    user_ID = None
    access_token = None
    refresh_token = None
    expires = None
    connect = None
    tracks_data = None
    output_data = None
    output_track_IDs = None
    playlist_ID = None
    parameter_list = None

    debug = 0

    # Constructor
    def __init__(self):
        self.data_manager = datamanager.DataManager()
        connect = False

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
            while choice.upper() != 'Y' and choice.upper() != 'N':
                print("Client_ID: " + self.client_ID)
                print("Client_Secret: " + self.client_secret)
                choice = input("Client ID and secret seems to exist, do you want to use those? (Y/N) : ")
            if not choice.upper() == 'Y':
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

    def extract_data_from_source(self):

        # The local tracks SQL database is to gain time if the data have already been extracted.
        data_source_choice = menu_list(header="Do you want to extract from the local database or extract from Spotify?",
                                       menu_list=['Local Database',
                                                  'Spotify Personnal Playlist',
                                                  'Spotify Liked Songs',
                                                  'Spotify Saved Albums'
                                                  ]
                                       )

        if data_source_choice == 1:  # Tracks data extraction from local SQL database.
            self.tracks_data = self.extract_data_from_local_database()
            self.parameter_list = tracksanalyser.extract_parameter_list(self.tracks_data)
        elif data_source_choice == 2:  # Tracks data extraction from API request.
            spotify_source_type = "playlist"
            playlist_name, self.tracks_data = self.extract_data_from_spotify(spotify_source_type)
            self.parameter_list = tracksanalyser.extract_parameter_list(self.tracks_data)
            choice = ""
            while choice.upper() != 'Y' and choice.upper() != 'N':  # Choice to replace the local SQL database with new data.
                clear_interpreter()
                choice = input("\nDo you want to flush the data in the database and replace those with the new data? (Y/N): ")
            if choice.upper() == 'Y':
                table = 'playlist_' + strip_accents(playlist_name.replace(" ", "_"))
                self.save_data_to_local_database(table, self.tracks_data)
        elif data_source_choice == 3:
            spotify_source_type = "liked_tracks"
            self.tracks_data = self.extract_data_from_spotify(spotify_source_type)
            table = "liked_tacks"
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

    def extract_data_from_spotify(self, spotify_source_type):
        spotify_source_type = spotify_source_type
        tracks_data = None
        if spotify_source_type == "playlist":
            playlist_info = self.spotify_API.extract_list_of_user_playlist()
            playlist_name = [info[0] for info in playlist_info]
            playlist_id = [info[1] for info in playlist_info]
            choice = menu_list(header="From which playlist?", menu_list=playlist_name)

            track_IDs_list = self.spotify_API.extract_tracks_IDs_from_playlist(playlist_id[choice - 1])
            tracks_data = self.spotify_API.extract_tracks_data(track_IDs_list)
            return playlist_name[choice - 1], tracks_data

        elif spotify_source_type == "liked_tracks":
            track_IDs = self.spotify_API.extract_saved_tracks_IDs()
            tracks_data = self.spotify_API.extract_tracks_data(track_IDs)
            return tracks_data

        elif spotify_source_type == "saved_albums":
            album_counts = 50
            offset = 0
            album_IDs_list = list()
            while album_counts == 50:
                album_IDs_buff = self.spotify_API.extract_library_albums_IDs(offset=offset)
                album_counts = len(album_IDs_buff)
                offset = offset + album_counts
                album_IDs_list = album_IDs_list + album_IDs_buff
            track_IDs = self.spotify_API.extract_tracks_IDs_from_album(album_IDs_list)
            tracks_data = self.spotify_API.extract_tracks_data(track_IDs)
            return tracks_data
        else:
            return None

    def extract_data_from_local_database(self):
        self.data_manager.connect_to_database()
        table_name = self.data_manager.extract_all_table_name()
        choice = menu_list(header="Which table?", menu_list=table_name)
        tracks_data = self.data_manager.read_all_tracks_data_table(table_name[choice - 1])
        self.data_manager.close_database()
        return tracks_data

    def save_data_to_local_database(self, table, data):
        self.data_manager.connect_to_database()

        if self.data_manager.is_table_exist(table):
            header = "\nThe table: " + table + " exist. Do you want to flush the old data and replace it with new data?"
            menu_list("Yes", "No")
            choice = menu_list(header=header, menu_list=menu_list())
            if choice == 1:
                self.data_manager.clear_all_data_from_table(table)
                self.data_manager.write_tracks_data_to_table(table, data)
        else:
            self.data_manager.write_tracks_data_to_table(table, data)

        self.data_manager.close_database()

    def generate_graph_for_statistic(self):
        tracks_data = self.tracks_data
        tracks_dataframe = tracksanalyser.convert_dataset_to_panda_dataframe(tracks_data)
        print("For which parameter do you want to display the boxplot: ")
        print(self.parameter_list)
        parameter = input("Parameter to analyse: ")
        tracksanalyser.generate_histogram_for_stat(tracks_dataframe, parameter)

    def extract_tracks_based_on_tempo(self):
        print("\nThe program will now sort the songs with the requested tempo (±10%): ")
        tempo = input("Which tempo do you want: ")
        tracks_data = self.tracks_data

        # Sort tracks with the requested tempo with the .
        output_tracks = tracksanalyser.extract_track_by_parameter_and_value(tracks_data, 'tempo', float(tempo), 0.1)
        self.output_track_IDs = tracksanalyser.extract_tracks_URI_IDs(output_tracks)

    def analyse_tracks_data(self):
        tracks_data = self.tracks_data
        self.output_data = tracksanalyser.extract_stats_from_tracks(tracks_data)
        print("\nMean: ")
        print(self.output_data[0])
        print("\nStDev: ")
        print(self.output_data[1])

    def add_tracks_to_playlist(self):
        if self.playlist_ID is not None:
            result = self.spotify_API.add_tracks_to_a_playlist(self.playlist_ID, self.output_track_IDs)
            if result:
                print("\nPlaylist generated successfully")
            else:
                print("\nPlaylist body generated successfully but tracks have not been add to the playlist...")
        else:
            print("\nPlaylist not created...")