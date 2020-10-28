"""
Main module for the BeatList project.

This module handle the controller that handle all the request to the Spotify API, the data management and the data analysis.

"""

import beatlistController
import sys


def generate_playlist_from_scratch(controller_beatlist: beatlistController.Controller):
    """Generate playlist from raw dataset.

    The module:
        1. call the controller method to extract the required data from a source (load or Spotify).
        2. call the controller method to filter the data based on a tempo.
        3. call the controller method for the playlist creation (name and POST to Spotify API).
        4. call the controller method to add tracks to the created playlist.

    Parameters
    ----------
    controller_beatlist: beatlistController.Controller
        controller for the project.

    """
    if controller_beatlist.extract_data_from_source():  # Extract tracks data from source (Spotify or local databse)
        controller_beatlist.extract_tracks_based_on_tempo()  # Extract tracks based on tempo.
        controller_beatlist.create_the_spotify_playlist()  # Send request to create the playlist with the tracks
        controller_beatlist.add_tracks_to_playlist()  # Send request to add tracks to the playlist


def analyse_a_playlist(controller_beatlist):  # Extracts all the tracks data of a playlist and give the general stats of the server. Show a box plot graph of the stats
    if controller_beatlist.extract_data_from_source():  # Extract data from source (Spotify or local databse)
        controller_beatlist.analyse_tracks_data()
        controller_beatlist.generate_graph_for_statistic()


def extract_stats_from_playlist():

    return


def save_tracks_to_database(controller_beatlist):
    controller_beatlist.extract_data_from_source()
    # Save tracks to database


def delete_table_from_database(controller_beatlist):
    controller_beatlist.delete_table_from_local_database()


def connexion_menu():
    controller_beatlist = beatlistController.Controller()  # object that handle all other objects (Datamanager, SpotifyAPI, SongAnalyser) and handle all the logic.
    print("Welcome to BeatList. A program to analyse songs and create Spotify playlist based on inputs.")
    header_menu = 'Main Menu: '
    menu_list = ['Connect']

    choice = 0
    while 1 > choice or choice > len(menu_list) + 1:
        choice = beatlistController.menu_generator(header=header_menu, menu_list=menu_list, exit_choice=True)
        if choice == 1:
            print("\nLogin: ")
            controller_beatlist.get_credentials()  # Looks for credentials and ask for them
            controller_beatlist.get_authentification()  # Looks for authentification and ask it if not already granted.
            if controller_beatlist.connect:
                beatlistController.clear_interpreter()
                print("\nCredentials and authentification granted.")
                controller_beatlist.extract_user_id()
                return controller_beatlist
            else:
                connexion_menu()
        elif choice == len(menu_list) + 1:
            sys.exit()


def main_menu(controller_beatlist):
    choice = 0
    header_menu = 'Main menu: '
    menu_list = ['Save tracks to local database', 'Delete a table from local database', 'Generate a playlist', 'Analyse a playlist']
    while 1 > choice or choice > 5:
        choice = beatlistController.menu_generator(header=header_menu, menu_list=menu_list, exit_choice=True)

    if choice == 1:
        save_tracks_to_database(controller_beatlist)
    elif choice == 2:
        delete_table_from_database(controller_beatlist)
    elif choice == 3:
        generate_playlist_from_scratch(controller_beatlist)
    elif choice == 4:
        analyse_a_playlist(controller_beatlist)
    elif choice == len(menu_list) + 1:
        print('End of program')
        sys.exit()

    main_menu(controller_beatlist)


def main():
    controller_beatlist = connexion_menu()

    main_menu(controller_beatlist)


if __name__ == "__main__":
    main()