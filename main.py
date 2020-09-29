import spotifyAPI
import datamanager
import songsanalyser
import datetime
import os

# Variables
client_id = None
client_secret = None
user_id = None
access_token = None
refresh_token = None
expires = None
data_manager = datamanager.DataManager()  # Handle all data writing and access from file and SQL database
spotify_API = None  # spotifyAPI class to handle all POST and GET request to the API.
songs_analyser = None  # class to handle all the tracks data processing.
track_data = None
tempo = None


def clear_interpreter():
    os.system('cls' if os.name == 'nt' else 'clear')


# look for credentials and ask for them
if not data_manager.is_client_info_exist():
    print("No client_ID and client_Secret found. Please provide the required credentials to continue.")
    client_id = input("Client_ID: ")
    client_secret = input("Client_Secret: ")
    data_manager.save_line_info('1', 0)  # v1) 1 for client info in file. Should have some way to verify if info are reliable.
    data_manager.save_client_info_to_file(client_id, client_secret)
else:
    choice = ''
    client_id, client_secret = data_manager.extract_client_info_from_file()
    while choice.upper() != 'Y' and choice.upper() != 'N':
        print("Client_ID: " + client_id)
        print("Client_Secret: " + client_secret)
        choice = input("Client ID and secret seems to exist, do you want to use those? (Y/N) : ")
    if not choice.upper() == 'Y':
        clear_interpreter()
        print("Choose new client_ID and client_Secret")
        client_id = input("Client_ID: ")
        client_secret = input("Client_Secret: ")
        data_manager.save_client_info_to_file(client_id, client_secret)
        data_manager.save_authentification_to_file('0')

# Look for authentification and ask it if not authentified
if client_id is not None and client_secret is not None:
    now = datetime.datetime.now()
    spotify_API = spotifyAPI.SpotifyAPI(client_id, client_secret)  # spotifyAPI class to handle all POST and GET request to the API.
    expires = spotify_API.get_expires()
    if not data_manager.is_auth_granted():
        clear_interpreter()
        spotify_API.request_auth()
        expiress = spotify_API.get_expires()
        [request_success, access_token, refresh_token] = spotify_API.extract_access_token()
        if request_success:
            data_manager.save_line_info('1', 3)
            data_manager.save_tokens_to_file(access_token, refresh_token)
        else:
            print("Authentification not successful.")

    elif now >= expires:  # Verify if the access token is still valid, if not, do a request to have a new one.
        refresh_token = data_manager.extract_line_info(5)
        spotify_API.set_refresh_token(refresh_token)
        access_token = spotify_API.refresh()
        expires = spotify_API.get_expires()
        data_manager.save_line_info(access_token, 4)

spotify_API.extract_current_user_id()
user_id = spotify_API.get_user_id()

print("\nCredentials and authentification granted.")
print("User ID: " + user_id)
print("Next step is to extract from a source, which is the saved tracks. ")

# Extract tracks (songs) data information.
data_source_choice = ""
while data_source_choice != '1' and data_source_choice != '2':  # The local tracks SQL database is to gain time if the data have already been extracted.
    print("\nDo you want to extract from the local database or extract from Spotify?")
    data_source_choice = input("1)Local Database, 2)Spotify: ")

if data_source_choice == '1':  # Tracks data extraction from local SQL database.
    data_manager.connect_to_database()
    track_data = data_manager.read_all_tracks_data_table()
    data_manager.close_database()
elif data_source_choice == '2':  # Tracks data extraction from API request.
    track_IDs_list = spotify_API.extract_saved_tracks_IDs()
    track_data = spotify_API.extract_tracks_data(track_IDs_list)
    choice =""
    while choice.upper() != 'Y' and choice.upper() != 'N':  # Choice to replace the local SQL database with new data.
        clear_interpreter()
        choice = input("\nDo you want to flush the data in the database and replace those with the new data? (Y/N): ")
    if choice.upper() == 'Y':
        data_manager.connect_to_database()
        data_manager.clear_all_data_from_table('songData')
        data_manager.write_tracks_data_to_table(track_data)
        data_manager.close_database()

print("\nThe program will now sort the songs with the requested tempo (±10%): ")
tempo = input("Which tempo do you want: ")

# Sort tracks with the requested tempo.
songs_analyser = songsanalyser.SongAnalyser(track_data)
output_track_IDs = songs_analyser.extract_track_URIs_by_parameter('tempo', float(tempo), 0.1)

# Send request to create the playlist with the tracks
playlist_name = input("\nEnter the playlist name: ")
playlist_id = spotify_API.create_a_playlist(playlist_name)

# Send request to add tracks to the playlist
if playlist_id is not None:
    result = spotify_API.add_tracks_to_a_playlist(playlist_id, output_track_IDs)
    if result:
        print("\nPlaylist generated successfully")
    else:
        print("\nPlaylist body generated successfully but tracks have not been add to the playlist...")
else:
    print("\nPlaylist not created...")