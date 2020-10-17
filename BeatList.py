import os
import beatlistController
import sys


def clear_interpreter():
    os.system('cls' if os.name == 'nt' else 'clear')


def generate_playlist_from_scratch(controller_beatlist):
    controller_beatlist.extract_data_from_source()  # Extract tracks data from source (Spotify or local databse)
    controller_beatlist.extract_tracks_based_on_tempo()  # Extract tracks based on tempo.
    controller_beatlist.create_the_spotify_playlist()  # Send request to create the playlist with the tracks
    controller_beatlist.add_tracks_to_playlist()  # Send request to add tracks to the playlist


def analyse_a_playlist(controller_beatlist): # Extracts all the tracks data of a playlist and give the general stats of the server. Show a box plot graph of the stats
    controller_beatlist.extract_data_from_source()  # Extract data from source (Spotify or local databse)
    controller_beatlist.analyse_tracks_data()
    controller_beatlist.generate_graph_for_statistic()


def extract_stats_from_playlist():
    return


def save_tracks_to_database(controller_beatlist):
    controller_beatlist.extract_data_from_source()
    # Save tracks to database


def connexion_menu():
    controller_beatlist = beatlistController.Controller() # object that handle all other objects (Datamanager, SpotifyAPI, SongAnalyser) and handle all the logic.
    print("Welcome to BeatList. A program to analyse songs and create Spotify playlist based on inputs.")
    header_menu = 'Main Menu: '
    menu_list = ['Connect', 'Exit']
    choice = beatlistController.menu_list(header=header_menu, menu_list=menu_list)

    if choice == 1:
        print("\nLogin: ")
        controller_beatlist.get_credentials()  # Looks for credentials and ask for them
        controller_beatlist.get_authentification()  # Looks for authentification and ask it if not already granted.
        if controller_beatlist.connect:
            clear_interpreter()
            print("\nCredentials and authentification granted.")
            controller_beatlist.extract_user_id()
            return controller_beatlist
        else:
            connexion_menu()
    else:
        sys.exit()


def main_menu(controller_beatlist):
    choice = 0
    header_menu = 'Main menu: '
    menu_list = ['Save tracks to local database', 'Generate a playlist', 'Analyse a playlist', 'Exit']
    while 1 > choice or choice > 4:
        choice = beatlistController.menu_list(header=header_menu, menu_list=menu_list)

    if choice == 1:
        save_tracks_to_database(controller_beatlist)
    elif choice == 2:
        generate_playlist_from_scratch(controller_beatlist)
    elif choice == 3:
        analyse_a_playlist(controller_beatlist)
    return choice


def main():
    controller_beatlist = connexion_menu()

    choice = 0
    while choice != 4:
        choice = main_menu(controller_beatlist)

    print('End of program')


if __name__ == "__main__":
    main()